import { createClient } from '@supabase/supabase-js';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { pipeline } from '@xenova/transformers';
import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(__dirname, '.env') });

const supabaseUrl = process.env.SUPABASE_URL!;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;
const geminiApiKey = process.env.GEMINI_API_KEY!;

const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: { persistSession: false, autoRefreshToken: false },
});

const genAI = new GoogleGenerativeAI(geminiApiKey);

// Singleton instance for local fast embedding extraction (384-dim)
let extractorInstance: any = null;
async function getExtractor() {
  if (!extractorInstance) {
    extractorInstance = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
  }
  return extractorInstance;
}

export type AgentAction = 'RESPOND' | 'MUTE_AI' | 'TRANSFER_HUMAN';

export interface AgentResponse {
  text: string | null;
  action: AgentAction;
  intent?: string;
}

/**
 * FAST REASONING ROUTER
 * Uses Gemini to classify message intent before running RAG search
 */
async function classifyMessageIntent(userQuery: string): Promise<'PERSONAL' | 'BUSINESS_ENQUIRY' | 'HUMAN_REQUEST' | 'OUT_OF_SCOPE'> {
  try {
    const routerModel = genAI.getGenerativeModel({
      model: 'gemini-2.5-flash',
      generationConfig: { temperature: 0.0, responseMimeType: 'application/json' },
    });

    const routerPrompt = `
Analyze the incoming message sent to a business WhatsApp number and categorize its primary intent.

CATEGORIES:
1. "HUMAN_REQUEST": User explicitly wants to talk to a human, manager, owner, real person, or files a serious complaint/dispute (e.g., "speak to owner", "call me", "agent", "human", "I want to complain").
2. "PERSONAL": Casual conversation, social greetings, family/friend banter, personal plans, personal questions not related to commercial transactions (e.g., "Hey bro", "Are you home?", "Mum said to call her", "How was your weekend?", "Lunch today?").
3. "BUSINESS_ENQUIRY": Product/service inquiries, pricing, stock, availability, booking requests, recommendations, technical specs, business hours (e.g., "How much is paracetamol?", "Do you sell laptops?", "Book a doctor slot").
4. "OUT_OF_SCOPE": Unrelated trivia, general knowledge questions, spam, or nonsense not connected to business services or personal social interaction.

INPUT MESSAGE: "${userQuery}"

JSON Output schema:
{ "intent": "PERSONAL" | "BUSINESS_ENQUIRY" | "HUMAN_REQUEST" | "OUT_OF_SCOPE", "reasoning": "short explanation" }
`;

    const result = await routerModel.generateContent(routerPrompt);
    const parsed = JSON.parse(result.response.text());
    return parsed.intent || 'BUSINESS_ENQUIRY';
  } catch (err) {
    console.warn('⚠️ Router classification fallback to BUSINESS_ENQUIRY:', err);
    const humanKeywords = ['agent', 'human', 'representative', 'real person', 'support team', 'manager', 'complaint'];
    if (humanKeywords.some(k => userQuery.toLowerCase().includes(k))) {
      return 'HUMAN_REQUEST';
    }
    return 'BUSINESS_ENQUIRY';
  }
}

/**
 * 💡 WORLD-CLASS AGENTIC RAG ENGINE (MANUAL HYBRID RAG)
 */
export async function processAgenticQuery(
  userQuery: string,
  phoneNumber: string = 'default_user'
): Promise<AgentResponse> {
  try {
    // ----------------------------------------------------------------------
    // STEP 1: STATE LOCK GUARD (Mute AI if human handover is active)
    // ----------------------------------------------------------------------
    const { data: session, error: sessionErr } = await supabase
      .from('conversations')
      .select('status')
      .eq('phone_number', phoneNumber)
      .maybeSingle();

    if (sessionErr) {
      console.warn('⚠️ Conversation table warning:', sessionErr.message);
    }

    if (session?.status === 'human_agent_requested') {
      console.log(`\n🔇 [STATE LOCKED] User ${phoneNumber} is assigned to Human Support. AI Muted.`);
      return { text: null, action: 'MUTE_AI', intent: 'HUMAN_HANDOVER_LOCKED' };
    }

    // ----------------------------------------------------------------------
    // STEP 2: INTENT REASONING & ROUTING
    // ----------------------------------------------------------------------
    const intent = await classifyMessageIntent(userQuery);
    console.log(`🧠 Intent Classified for [${userQuery}]:`, intent);

    // 🔴 CASE A: PERSONAL CHAT -> MUTE AI SILENTLY
    if (intent === 'PERSONAL') {
      console.log(`🤫 Personal chat detected from ${phoneNumber}. AI stays silent.`);
      return {
        text: null,
        action: 'MUTE_AI',
        intent: 'PERSONAL'
      };
    }

    // 🔴 CASE B: HUMAN SUPPORT REQUEST OR COMPLAINT -> LOCK STATE & HANDOVER
    if (intent === 'HUMAN_REQUEST') {
      const { error: upsertErr } = await supabase
        .from('conversations')
        .upsert(
          {
            phone_number: phoneNumber,
            status: 'human_agent_requested',
            last_message_at: new Date().toISOString()
          },
          { onConflict: 'phone_number' }
        );

      if (upsertErr) {
        console.error('❌ Failed to save human handover status:', upsertErr.message);
      }

      return {
        text: `🚨 *HUMAN AGENT HANDOVER ACTIVATED* 🚨\n\nI have paused automated AI responses and alerted our live team. A representative or business owner will join this chat shortly!`,
        action: 'TRANSFER_HUMAN',
        intent: 'HUMAN_REQUEST'
      };
    }

    // 🔴 CASE C: OUT OF SCOPE / SPAM -> POLITE REDIRECTION
    if (intent === 'OUT_OF_SCOPE') {
      return {
        text: "I am the automated business assistant for our store & services catalog. Please let me know if you have any questions about our products, bookings, or pricing!",
        action: 'RESPOND',
        intent: 'OUT_OF_SCOPE'
      };
    }

    // ----------------------------------------------------------------------
    // STEP 3: HYBRID RAG SEARCH (VECTOR 384-DIM + BM25 LEXICAL RRF)
    // ----------------------------------------------------------------------
    const extractor = await getExtractor();
    const output = await extractor(userQuery, { pooling: 'mean', normalize: true });
    const queryEmbedding = Array.from(output.data);

    const { data: retrievedDocs, error: searchError } = await supabase.rpc('match_products_hybrid', {
      query_text: userQuery,
      query_embedding: queryEmbedding,
      match_count: 5,
      rrf_k: 60
    });

    if (searchError) {
      console.error('❌ Hybrid Search Failure:', searchError.message);
      return {
        text: "I encountered a minor database search error. Please reply *'agent'* to connect directly with human support.",
        action: 'RESPOND',
        intent: 'BUSINESS_ENQUIRY'
      };
    }

    if (!retrievedDocs || retrievedDocs.length === 0) {
      return {
        text: "I searched our store catalog but couldn't find an exact item matching your request. Reply *'agent'* to speak with our representative!",
        action: 'RESPOND',
        intent: 'BUSINESS_ENQUIRY'
      };
    }

    const containsMedical = retrievedDocs.some((d: any) =>
      ['Pharmaceuticals', 'Healthcare Services', 'Pain Relief', 'Antibiotics'].includes(d.category)
    );

    // ----------------------------------------------------------------------
    // STEP 4: CONTEXT FORMATTING
    // ----------------------------------------------------------------------
    const formattedContext = retrievedDocs.map((item: any) => `
• Item SKU: ${item.sku}
  Name: ${item.name}
  Brand: ${item.brand}
  Category: ${item.category}
  Price: $${item.price}
  Availability: ${item.stock_quantity > 0 ? `${item.stock_quantity} available` : 'Out of Stock'}
  Specs: ${JSON.stringify(item.metadata || {})}
  Description: ${item.description}
`).join('\n');

    // ----------------------------------------------------------------------
    // STEP 5: GROUNDED LLM GENERATION WITH SAFETY & FORMATTING
    // ----------------------------------------------------------------------
    const systemInstruction = `
You are an elite, highly accurate AI customer support copilot for our WhatsApp business.

OPERATIONAL RULES:
1. STRICT GROUNDING: Rely ONLY on the database context provided below. Do not invent products, prices, or policies.
2. WHATSAPP FORMATTING:
   • Bold key names and prices (*Apple iPhone 15 Pro*, *$1099.00*).
   • Use clean bullet points (•) on single lines.
3. PRESCRIPTION SAFETY: If any product metadata specifies prescription requirements or is an antibiotic, state in bold: "*⚠️ Prescription Required*".
4. MEDICAL DISCLAIMER: If medical/pharmaceutical products are mentioned, ALWAYS append this disclaimer:
   "\n\n_⚠️ Disclaimer: I am an AI assistant, not a medical professional. Please consult a qualified doctor before using any medication._"

DATABASE CONTEXT:
${formattedContext}
`;

    const model = genAI.getGenerativeModel({
      model: 'gemini-2.5-flash',
      systemInstruction: systemInstruction,
      generationConfig: { temperature: 0.1 },
    });

    const aiResult = await model.generateContent(userQuery);
    let finalResponse = aiResult.response.text();

    if (containsMedical && !finalResponse.includes('Disclaimer')) {
      finalResponse += "\n\n_⚠️ Disclaimer: I am an AI assistant, not a medical professional. Please consult a qualified doctor before taking medication._";
    }

    return { text: finalResponse, action: 'RESPOND', intent: 'BUSINESS_ENQUIRY' };

  } catch (err: any) {
    console.error('❌ Agentic Pipeline Exception:', err.message || err);
    return {
      text: "I experienced a temporary processing glitch. Reply *'agent'* to speak directly with our team.",
      action: 'RESPOND',
      intent: 'UNKNOWN'
    };
  }
}