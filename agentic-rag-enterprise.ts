import { createClient } from '@supabase/supabase-js';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { pipeline } from '@xenova/transformers';
import dotenv from 'dotenv';
import path from 'path';
import crypto from 'crypto';

dotenv.config({ path: path.resolve(__dirname, '.env') });

const supabaseUrl = process.env.SUPABASE_URL!;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;
const geminiApiKey = process.env.GEMINI_API_KEY!;

const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: { persistSession: false, autoRefreshToken: false },
});

const genAI = new GoogleGenerativeAI(geminiApiKey);

// Global Singleton for local feature extractor
let extractorInstance: any = null;
async function getExtractor() {
  if (!extractorInstance) {
    extractorInstance = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
  }
  return extractorInstance;
}

// ============================================================================
// L1 & L2 CACHING ENGINE
// ============================================================================
interface CacheEntry {
  response: string;
  action: 'RESPOND' | 'MUTE_AI' | 'TRANSFER_HUMAN';
  intent: string;
  embedding: number[];
  timestamp: number;
}

const L1_EXACT_CACHE = new Map<string, CacheEntry>();
const L2_SEMANTIC_CACHE: CacheEntry[] = [];
const CACHE_TTL_MS = 1000 * 60 * 60; // 1 Hour Cache TTL

function hashQuery(query: string): string {
  return crypto.createHash('sha256').update(query.toLowerCase().trim()).digest('hex');
}

function cosineSimilarity(a: number[], b: number[]): number {
  let dotProduct = 0;
  let normA = 0;
  let normB = 0;
  for (let i = 0; i < a.length; i++) {
    dotProduct += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

function checkCache(query: string, embedding?: number[]): CacheEntry | null {
  const queryHash = hashQuery(query);
  const now = Date.now();

  // 1. Exact L1 Hit
  if (L1_EXACT_CACHE.has(queryHash)) {
    const entry = L1_EXACT_CACHE.get(queryHash)!;
    if (now - entry.timestamp < CACHE_TTL_MS) {
      console.log('⚡ [L1 EXACT CACHE HIT]');
      return entry;
    }
  }

  // 2. Semantic L2 Hit (Threshold > 0.95 similarity)
  if (embedding && embedding.length > 0) {
    for (const entry of L2_SEMANTIC_CACHE) {
      if (now - entry.timestamp < CACHE_TTL_MS) {
        const sim = cosineSimilarity(embedding, entry.embedding);
        if (sim >= 0.95) {
          console.log(`⚡ [L2 SEMANTIC CACHE HIT] Similarity Score: ${sim.toFixed(4)}`);
          return entry;
        }
      }
    }
  }

  return null;
}

function setCache(query: string, embedding: number[], result: CacheEntry) {
  const queryHash = hashQuery(query);
  L1_EXACT_CACHE.set(queryHash, result);
  L2_SEMANTIC_CACHE.push({ ...result, embedding });

  // Prevent memory overhead: limit cache to 500 items
  if (L2_SEMANTIC_CACHE.length > 500) {
    L2_SEMANTIC_CACHE.shift();
  }
}

// ============================================================================
// INTENT REASONING ROUTER
// ============================================================================
export type AgentAction = 'RESPOND' | 'MUTE_AI' | 'TRANSFER_HUMAN';

export interface AgentResponse {
  text: string | null;
  action: AgentAction;
  intent: string;
  source?: 'CACHE' | 'RAG_ENGINE' | 'FALLBACK';
}

async function classifyIntent(userQuery: string): Promise<{ intent: string; confidence: number }> {
  try {
    const routerModel = genAI.getGenerativeModel({
      model: 'gemini-3.1-flash-lite',
      generationConfig: { temperature: 0.0, responseMimeType: 'application/json' },
    });

    const prompt = `
Analyze the user message sent to a WhatsApp business number and return JSON with classification.

Categories:
- "PERSONAL": Casual chatter, banter, family check-ins, personal non-commercial messages ("hey bro", "are you free", "lunch today", "mom called").
- "HUMAN_REQUEST": Express desire to talk to real person, owner, manager, complaints, dispute, refund request ("agent", "owner", "human", "call me").
- "BUSINESS_ENQUIRY": Questions about products, pricing, stock, specs, ocean view suites, telehealth, services.
- "OUT_OF_SCOPE": Spam, random trivia, off-topic prompts.

Input: "${userQuery}"

Return format: { "intent": "PERSONAL" | "HUMAN_REQUEST" | "BUSINESS_ENQUIRY" | "OUT_OF_SCOPE", "confidence": 0.0 to 1.0 }
`;

    const res = await routerModel.generateContent(prompt);
    return JSON.parse(res.response.text());
  } catch {
    const low = userQuery.toLowerCase();
    if (['agent', 'human', 'owner', 'manager', 'complaint'].some(k => low.includes(k))) {
      return { intent: 'HUMAN_REQUEST', confidence: 0.9 };
    }
    return { intent: 'BUSINESS_ENQUIRY', confidence: 0.8 };
  }
}

// ============================================================================
// MAIN AGENTIC RAG PIPELINE
// ============================================================================
export async function processAgenticQueryEnterprise(
  userQuery: string,
  phoneNumber: string = 'default_user'
): Promise<AgentResponse> {
  try {
    // 1. STATE LOCK CHECK
    const { data: session } = await supabase
      .from('conversations')
      .select('status')
      .eq('phone_number', phoneNumber)
      .maybeSingle();

    if (session?.status === 'human_agent_requested') {
      return { text: null, action: 'MUTE_AI', intent: 'STATE_LOCKED_HUMAN' };
    }

    // 2. EMBEDDING GENERATION
    const extractor = await getExtractor();
    const output = await extractor(userQuery, { pooling: 'mean', normalize: true });
    const queryEmbedding = Array.from(output.data) as number[];

    // 3. CACHE CHECK
    const cached = checkCache(userQuery, queryEmbedding);
    if (cached) {
      return { text: cached.response, action: cached.action, intent: cached.intent, source: 'CACHE' };
    }

    // 4. INTENT CLASSIFICATION
    const { intent } = await classifyIntent(userQuery);

    if (intent === 'PERSONAL') {
      const result: CacheEntry = { response: '', action: 'MUTE_AI', intent: 'PERSONAL', embedding: queryEmbedding, timestamp: Date.now() };
      setCache(userQuery, queryEmbedding, result);
      return { text: null, action: 'MUTE_AI', intent: 'PERSONAL', source: 'RAG_ENGINE' };
    }

    if (intent === 'HUMAN_REQUEST') {
      await supabase.from('conversations').upsert(
        { phone_number: phoneNumber, status: 'human_agent_requested', last_message_at: new Date().toISOString() },
        { onConflict: 'phone_number' }
      );
      const text = "🚨 *HUMAN AGENT HANDOVER ACTIVATED* 🚨\n\nI have paused automated AI responses and alerted our live team. A team member will join this chat shortly!";
      return { text, action: 'TRANSFER_HUMAN', intent: 'HUMAN_REQUEST', source: 'RAG_ENGINE' };
    }

    if (intent === 'OUT_OF_SCOPE') {
      const text = "I am the automated assistant for our store. Please let me know if you have questions regarding our products, services, or bookings!";
      return { text, action: 'RESPOND', intent: 'OUT_OF_SCOPE', source: 'RAG_ENGINE' };
    }

    // 5. HYBRID SEARCH
    const { data: retrievedDocs, error: searchErr } = await supabase.rpc('match_products_hybrid', {
      query_text: userQuery,
      query_embedding: queryEmbedding,
      match_count: 5,
      rrf_k: 60,
    });

    if (searchErr || !retrievedDocs || retrievedDocs.length === 0) {
      return {
        text: "I searched our database but couldn't find an exact item matching your query. Reply *'agent'* to speak with human support!",
        action: 'RESPOND',
        intent: 'BUSINESS_ENQUIRY',
        source: 'FALLBACK'
      };
    }

    const containsMedical = retrievedDocs.some((d: any) =>
      ['Pharmaceuticals', 'Healthcare Services', 'Pain Relief', 'Antibiotics'].includes(d.category)
    );

    // 6. CONTEXT ASSEMBLY
    const formattedContext = retrievedDocs.map((item: any) => `
• Item: ${item.name}
  Brand: ${item.brand}
  Category: ${item.category}
  Price: $${item.price}
  Availability: ${item.stock_quantity > 0 ? `${item.stock_quantity} available` : 'Out of Stock'}
  Specs: ${JSON.stringify(item.metadata || {})}
  Description: ${item.description}
`).join('\n');

    // 7. GEMINI GROUNDED GENERATION
    const systemPrompt = `
You are an elite, highly accurate AI customer support copilot.

OPERATIONAL CONSTRAINTS:
1. STRICT GROUNDING: Answer using ONLY the database context below. Never hallucinate terms.
2. WHATSAPP FORMAT: Bold product names & prices (*Paracetamol 500mg*, *$12.50*). Use single bullet points (•). Keep responses concise.
3. PRESCRIPTION WARNING: If any item metadata requires a prescription, state in bold: "*⚠️ Prescription Required*".
4. MEDICAL DISCLAIMER: If medical products are mentioned, ALWAYS append:
   "\n\n_⚠️ Disclaimer: I am an AI assistant, not a doctor. Please consult a qualified healthcare professional for medical advice._"

DATABASE CONTEXT:
${formattedContext}
`;

    const model = genAI.getGenerativeModel({
      model: 'gemini-3.1-flash-lite',
      systemInstruction: systemPrompt,
      generationConfig: { temperature: 0.1 },
    });

    const aiRes = await model.generateContent(userQuery);
    let finalResponse = aiRes.response.text();

    if (containsMedical && !finalResponse.includes('Disclaimer')) {
      finalResponse += "\n\n_⚠️ Disclaimer: I am an AI assistant, not a doctor. Please consult a qualified healthcare professional for medical advice._";
    }

    // Save to Cache
    setCache(userQuery, queryEmbedding, {
      response: finalResponse,
      action: 'RESPOND',
      intent: 'BUSINESS_ENQUIRY',
      embedding: queryEmbedding,
      timestamp: Date.now()
    });

    return { text: finalResponse, action: 'RESPOND', intent: 'BUSINESS_ENQUIRY', source: 'RAG_ENGINE' };

  } catch (err: any) {
    console.error('❌ Enterprise Engine Failure:', err.message || err);
    return {
      text: "I experienced a temporary processing glitch. Reply *'agent'* to connect with human support.",
      action: 'RESPOND',
      intent: 'ERROR_FALLBACK',
      source: 'FALLBACK'
    };
  }
}