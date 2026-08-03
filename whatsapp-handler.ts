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

/**
 * Checks and updates conversation state in Supabase
 */
async function checkAndSetConversationState(phoneNumber: string, userQuery: string): Promise<{ isMuted: boolean; shouldHandover: boolean }> {
  // Fetch existing user session
  const { data: conversation } = await supabase
    .from('conversations')
    .select('status')
    .eq('phone_number', phoneNumber)
    .maybeSingle();

  // 1. If chat is already assigned to a human agent, mute AI completely
  if (conversation?.status === 'human_agent_requested') {
    return { isMuted: true, shouldHandover: false };
  }

  // 2. Detect explicit human request keywords
  const humanKeywords = ['agent', 'human', 'representative', 'real person', 'speak to someone', 'customer support', 'complaint', 'manager'];
  const isHumanRequested = humanKeywords.some(keyword => userQuery.toLowerCase().includes(keyword));

  if (isHumanRequested) {
    // Lock database state so AI stops replying until resolved by human team
    await supabase
      .from('conversations')
      .upsert({
        phone_number: phoneNumber,
        status: 'human_agent_requested',
        updated_at: new Date().toISOString()
      });

    return { isMuted: false, shouldHandover: true };
  }

  return { isMuted: false, shouldHandover: false };
}

export async function handleWhatsAppQuery(userQuery: string, phoneNumber: string = 'default_test_user'): Promise<string | null> {
  try {
    // ----------------------------------------------------------------------
    // GUARDRAIL 1: HUMAN HANDOFF DATABASE STATE MANAGEMENT
    // ----------------------------------------------------------------------
    const { isMuted, shouldHandover } = await checkAndSetConversationState(phoneNumber, userQuery);

    // If chat is locked in 'human_agent_requested' status, return null (AI suppressed)
    if (isMuted) {
      console.log(`🔇 AI Suppressed: User ${phoneNumber} is currently waiting for or speaking with a human agent.`);
      return null;
    }

    if (shouldHandover) {
      return `🚨 *TRANSFERRING TO HUMAN AGENT* 🚨\n\nI have handed your chat over to our live support team. An agent will reply directly in this chat shortly.\n\n*(Automated AI responses are now paused for this session)*`;
    }

    // ----------------------------------------------------------------------
    // STEP 2: GENERATE LOCAL 384-DIM EMBEDDING
    // ----------------------------------------------------------------------
    const extractor = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
    const output = await extractor(userQuery, { pooling: 'mean', normalize: true });
    const queryEmbedding = Array.from(output.data);

    // ----------------------------------------------------------------------
    // STEP 3: VECTOR DB SEARCH IN SUPABASE
    // ----------------------------------------------------------------------
    const { data: matchedItems, error } = await supabase.rpc('match_products', {
      query_embedding: queryEmbedding,
      match_threshold: 0.15,
      match_count: 4,
    });

    if (error) {
      console.error('❌ Supabase RPC Error:', error.message);
      return "I encountered a minor database issue. Reply *'agent'* to connect with human support.";
    }

    if (!matchedItems || matchedItems.length === 0) {
      return "I couldn't find an exact match in our store. Reply *'agent'* if you would like me to connect you with a human representative!";
    }

    // Determine if any retrieved item belongs to medical/pharmaceutical categories
    const containsMedicalItems = matchedItems.some((item: any) => 
      ['Pharmaceuticals', 'Pain Relief', 'Antibiotics', 'Healthcare Services'].includes(item.category)
    );

    // ----------------------------------------------------------------------
    // STEP 4: CONTEXT FORMATTING
    // ----------------------------------------------------------------------
    const context = matchedItems
      .map(
        (p: any) => `
- Item: ${p.name}
  Brand/Provider: ${p.brand}
  Category: ${p.category}
  Price: $${p.price}
  Availability: ${p.stock_quantity > 0 ? `${p.stock_quantity} available/open` : 'Out of Stock'}
  Details/Specs: ${JSON.stringify(p.metadata || {})}
  Description: ${p.description}
`
      )
      .join('\n');

    // ----------------------------------------------------------------------
    // GUARDRAILS 2 & 3: PROMPT CONSTRAINTS & CLEAN WHATSAPP FORMATTING
    // ----------------------------------------------------------------------
    const systemInstruction = `
You are an AI customer support assistant for a WhatsApp shop.

CRITICAL MEDICAL SAFETY RULES:
1. PRESCRIPTION WARNING: If any recommended item requires a prescription (check details/metadata for prescription_required = true or antibiotic status), you MUST explicitly state in bold: "*⚠️ Prescription Required*".
2. DISCLAIMER: If answering a medical or health query, ALWAYS append this exact disclaimer at the end of your message:
"_\n\n⚠️ Disclaimer: I am an AI, not a doctor. Please consult a qualified healthcare professional before taking any medication._"

WHATSAPP FORMATTING RULES:
1. Use clean WhatsApp formatting (*bold* for product names/prices, _italics_ for disclaimers).
2. Bullet points MUST use clean bullet symbols (•) on single lines. NEVER use double-indented or nested bullets like "* **Item**".
3. Keep responses concise, mobile-scannable, and easy to read on smartphones.
4. If the requested product is unavailable, clearly suggest alternative matches from the context or offer human agent handover.

DATABASE CONTEXT:
${context}
`;

    // ----------------------------------------------------------------------
    // STEP 5: GENERATE RESPONSE WITH GEMINI
    // ----------------------------------------------------------------------
    const chatModel = genAI.getGenerativeModel({
      model: 'gemini-3.1-flash-lite',
      systemInstruction: systemInstruction,
      generationConfig: { temperature: 0.1 },
    });

    const result = await chatModel.generateContent(userQuery);
    let reply = result.response.text();

    // Secondary safety check: Ensure disclaimer is attached for health queries
    if (containsMedicalItems && !reply.includes('Disclaimer')) {
      reply += "\n\n_⚠️ Disclaimer: I am an AI, not a doctor. Please consult a qualified healthcare professional for medical advice._";
    }

    return reply;

  } catch (err: any) {
    console.error('❌ Error handling query:', err.message || err);
    return "I'm having trouble processing your query right now. Reply *'agent'* to speak directly with a live support team member.";
  }
}