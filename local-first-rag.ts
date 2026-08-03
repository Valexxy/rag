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

// Local Pipeline Singleton (384-dim local MiniLM embedding model)
let extractorInstance: any = null;
async function getExtractor() {
  if (!extractorInstance) {
    extractorInstance = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
  }
  return extractorInstance;
}

export type AgentAction = 'RESPOND' | 'MUTE_AI' | 'TRANSFER_HUMAN';

export interface LocalEngineResponse {
  text: string | null;
  action: AgentAction;
  intent: string;
  source: 'LOCAL_STATE' | 'LOCAL_INTENT' | 'LOCAL_TEMPLATE' | 'GEMINI_LLM' | 'CACHE';
}

// ============================================================================
// 1. COMPREHENSIVE LOCAL INTENT PATTERNS
// ============================================================================
const PERSONAL_PATTERNS = [
  /\b(hey|hi|hello|good\s+morning|good\s+night|goodnight|gm|gn)\b/i,
  /\b(bro|man|friend|dude|boss|chief|pal|family)\b/i,
  /\b(lunch|dinner|drinks|coffee|food|breakfast)\b/i,
  /\b(mum|mom|dad|wife|husband|son|daughter)\b/i,
  /\b(home|busy|free|sleeping|driving|heading)\b/i,
  /\b(watch|saw|seen)\s+the\s+(match|game)\b/i,
  /\b(who\s+won|premier\s+league|champions\s+league)\b/i,
  /\b(borrow|car|vehicle|house|apartment|party)\b/i,
  /\b(meeting|meet)\s+at\b/i,
  /\b(where\s+are\s+you|are\s+you\s+there)\b/i,
  /\b(lol|lmao|haha|funny|joke)\b/i,
  /\bhappy\s+birthday\b/i,
  /\bcall\s+me\b/i
];

const HUMAN_PATTERNS = [
  /\b(speak|talk)\s+(to|with)\b/i,
  /\b(real\s+person|human|agent|manager|owner|representative)\b/i,
  /\b(transfer|connect)\s+me\b/i,
  /\b(customer\s+support|complaint|refund|dispute|legal\s+action)\b/i,
  /\bhuman\s+please\b/i,
  /\bstop\s+sending\s+ai\b/i,
  /\brepresentative\s+required\b/i,
  /\blet\s+me\s+talk\b/i
];

function detectLocalIntent(query: string): 'PERSONAL' | 'HUMAN_REQUEST' | 'BUSINESS_ENQUIRY' {
  const q = query.trim();
  
  // Check Human Request triggers first
  if (HUMAN_PATTERNS.some(p => p.test(q))) {
    return 'HUMAN_REQUEST';
  }

  // Check Personal Chat triggers
  if (PERSONAL_PATTERNS.some(p => p.test(q))) {
    // Exclude explicit product requests from false personal matches
    const isProductQuery = /\b(price|cost|how\s+much|stock|available|buy|order|sell|paracetamol|amoxicillin|solar|cleaning|suite|hotel)\b/i.test(q);
    if (!isProductQuery) {
      return 'PERSONAL';
    }
  }

  return 'BUSINESS_ENQUIRY';
}

// ============================================================================
// 2. LOCAL RESPONSE FORMATTER (Generates WhatsApp Markdown locally)
// ============================================================================
function formatLocalProductResponse(items: any[]): string {
  let hasMedical = false;

  const formattedItems = items.map(item => {
    const isRx = item.metadata?.prescription_required || item.category === 'Antibiotics';
    if (['Pharmaceuticals', 'Healthcare Services', 'Pain Relief', 'Antibiotics'].includes(item.category)) {
      hasMedical = true;
    }

    const rxTag = isRx ? ' *⚠️ Prescription Required*' : '';
    const stockStatus = item.stock_quantity > 0 ? `${item.stock_quantity} available` : 'Out of Stock';

    return `• *${item.name}* (${item.brand})\n  *Price:* $${item.price}${rxTag}\n  *Status:* ${stockStatus}\n  *Description:* ${item.description}`;
  }).join('\n\n');

  let text = `We found the following options in our catalog:\n\n${formattedItems}`;

  if (hasMedical) {
    text += `\n\n_⚠️ Disclaimer: I am an automated assistant, not a medical professional. Please consult a qualified doctor before using any medication._`;
  }

  return text;
}

// ============================================================================
// 3. MAIN LOCAL-FIRST AGENT ENGINE
// ============================================================================
export async function processLocalFirstQuery(
  userQuery: string,
  phoneNumber: string = 'default_user'
): Promise<LocalEngineResponse> {
  try {
    // ------------------------------------------------------------------------
    // STEP 1: LOCAL INTENT REGEX MATCHING (0 ms execution, 0 API calls)
    // ------------------------------------------------------------------------
    const localIntent = detectLocalIntent(userQuery);

    if (localIntent === 'PERSONAL') {
      return { text: null, action: 'MUTE_AI', intent: 'PERSONAL', source: 'LOCAL_INTENT' };
    }

    if (localIntent === 'HUMAN_REQUEST') {
      await supabase.from('conversations').upsert(
        { phone_number: phoneNumber, status: 'human_agent_requested', last_message_at: new Date().toISOString() },
        { onConflict: 'phone_number' }
      );

      return {
        text: `🚨 *HUMAN AGENT HANDOVER ACTIVATED* 🚨\n\nI have paused automated AI responses and alerted our live customer support team. A representative or business owner will join this chat shortly!`,
        action: 'TRANSFER_HUMAN',
        intent: 'HUMAN_REQUEST',
        source: 'LOCAL_INTENT'
      };
    }

    // ------------------------------------------------------------------------
    // STEP 2: CHECK CONVERSATION STATE LOCK (Only for business inquiries)
    // ------------------------------------------------------------------------
    const { data: session } = await supabase
      .from('conversations')
      .select('status')
      .eq('phone_number', phoneNumber)
      .maybeSingle();

    if (session?.status === 'human_agent_requested') {
      return { text: null, action: 'MUTE_AI', intent: 'STATE_LOCKED', source: 'LOCAL_STATE' };
    }

    // ------------------------------------------------------------------------
    // STEP 3: LOCAL EMBEDDING & HYBRID VECTOR SEARCH
    // ------------------------------------------------------------------------
    const extractor = await getExtractor();
    const output = await extractor(userQuery, { pooling: 'mean', normalize: true });
    const queryEmbedding = Array.from(output.data) as number[];

    const { data: retrievedDocs, error: searchError } = await supabase.rpc('match_products_hybrid', {
      query_text: userQuery,
      query_embedding: queryEmbedding,
      match_count: 5,
      rrf_k: 60,
    });

    if (searchError || !retrievedDocs || retrievedDocs.length === 0) {
      return {
        text: "I searched our store database but couldn't find an exact item matching your request. Reply *'agent'* to connect directly with human support!",
        action: 'RESPOND',
        intent: 'BUSINESS_ENQUIRY',
        source: 'LOCAL_TEMPLATE'
      };
    }

    // ------------------------------------------------------------------------
    // STEP 4: FAST LOCAL FORMATTING (Bypasses Cloud LLM API Calls)
    // ------------------------------------------------------------------------
    const localFormattedText = formatLocalProductResponse(retrievedDocs);
    return {
      text: localFormattedText,
      action: 'RESPOND',
      intent: 'BUSINESS_ENQUIRY',
      source: 'LOCAL_TEMPLATE'
    };

  } catch (err: any) {
    console.error('❌ Local Engine Exception:', err.message || err);
    return {
      text: "I encountered a brief processing delay. Reply *'agent'* to speak directly with our team.",
      action: 'RESPOND',
      intent: 'FALLBACK',
      source: 'LOCAL_TEMPLATE'
    };
  }
}