import dotenv from 'dotenv';
dotenv.config();

import { GoogleGenerativeAI } from '@google/generative-ai';
import axios from 'axios';
import { searchTenantProducts, supabase } from './search-products.js';
import { createMonnifyPayment } from './monnify-service.js';

// Validate Gemini API Key on load
const geminiApiKey = process.env.GEMINI_API_KEY;
if (!geminiApiKey) {
  console.error('❌ [CRITICAL ERROR]: GEMINI_API_KEY is missing or empty in your .env file!');
}

const genAI = new GoogleGenerativeAI(geminiApiKey || '');

// Define Agentic Tools available to Gemini
const agentTools = {
  functionDeclarations: [
    {
      name: 'search_products',
      description: 'Searches the merchant product catalog for items, pricing, specs, and availability.',
      parameters: {
        type: 'OBJECT',
        properties: {
          query: { type: 'STRING', description: 'Product title or search keywords' }
        },
        required: ['query']
      }
    },
    {
      name: 'monnify_create_payment',
      description: 'Generates a payment checkout link when a customer expresses intent to purchase an item.',
      parameters: {
        type: 'OBJECT',
        properties: {
          customerName: { type: 'STRING', description: 'Full name of the customer' },
          amount: { type: 'NUMBER', description: 'Total transaction amount in NGN (Naira)' },
          paymentDescription: { type: 'STRING', description: 'Description of the item or order being purchased' }
        },
        required: ['customerName', 'amount', 'paymentDescription']
      }
    }
  ]
};

/**
 * Core Multi-Tenant Orchestration Engine
 */
export async function processTenantMessage(
  tenantId: string,
  userQuery: string,
  phoneNumber: string
): Promise<string> {
  try {
    console.log(`🧠 [AI AGENT START] Tenant: ${tenantId} | Phone: ${phoneNumber}`);

    // 1. Safe Memory Load from Supabase
    let formattedHistory: Array<{ role: 'user' | 'model'; parts: Array<{ text: string }> }> = [];

    try {
      const { data: history, error: historyError } = await supabase
        .from('conversations')
        .select('*')
        .eq('tenant_id', tenantId)
        .eq('phone_number', phoneNumber)
        .order('created_at', { ascending: false })
        .limit(6);

      if (!historyError && history) {
        const rawHistory = history.reverse();
        for (const msg of rawHistory) {
          const rawRole = msg.role || msg.sender_type || msg.sender || 'user';
          const role: 'user' | 'model' = rawRole === 'user' ? 'user' : 'model';
          const contentText = msg.content || msg.message || '';

          if (formattedHistory.length === 0 || formattedHistory[formattedHistory.length - 1].role !== role) {
            formattedHistory.push({
              role,
              parts: [{ text: contentText }]
            });
          }
        }
      }
    } catch (memErr: any) {
      console.warn('⚠️ [MEMORY WARNING] Continuing with fresh conversation:', memErr.message);
    }

    // Ensure memory doesn't end on 'user' before sendMessage
    if (formattedHistory.length > 0 && formattedHistory[formattedHistory.length - 1].role === 'user') {
      formattedHistory.pop();
    }

  // 2. Initialize Gemini Model with a valid model endpoint identifier
    const model = genAI.getGenerativeModel({
      model: 'gemini-2.5-flash',
      tools: [agentTools as any]
    });

    const chat = model.startChat({ history: formattedHistory });
    let response = await chat.sendMessage(userQuery);

    // 3. Handle Tool Function Call Loop
    let functionCalls = response.response.functionCalls();

    while (functionCalls && functionCalls.length > 0) {
      const call = functionCalls[0];
      const { name, args } = call;
      console.log(`🛠️ [TOOL EXECUTED]: ${name}`, args);

      let toolResult: any;

      if (name === 'search_products') {
        const rawResult = await searchTenantProducts(tenantId, (args as any).query);
        try {
          toolResult = typeof rawResult === 'string' ? JSON.parse(rawResult) : rawResult;
        } catch {
          toolResult = { data: rawResult };
        }
      } else if (name === 'monnify_create_payment') {
        const { customerName, amount, paymentDescription } = args as any;
        toolResult = await createMonnifyPayment(
          customerName,
          'customer@example.com',
          amount,
          paymentDescription,
          tenantId
        );
      } else {
        toolResult = { error: `Unknown tool: ${name}` };
      }

      // Return tool output to Gemini
      response = await chat.sendMessage([
        {
          functionResponse: {
            name,
            response: typeof toolResult === 'object' && toolResult !== null ? toolResult : { result: toolResult }
          }
        }
      ]);

      functionCalls = response.response.functionCalls();
    }

    // 4. Extract Final Text
    let finalReplyText = '';
    try {
      finalReplyText = response.response.text();
    } catch {
      finalReplyText = 'Your request has been processed successfully.';
    }

    // 5. Save Conversation to Supabase
    try {
      await supabase.from('conversations').insert([
        { tenant_id: tenantId, phone_number: phoneNumber, role: 'user', content: userQuery },
        { tenant_id: tenantId, phone_number: phoneNumber, role: 'assistant', content: finalReplyText }
      ]);
    } catch {
      // Non-blocking if table structure differs slightly
    }

    // 6. Optional Evolution API WhatsApp Dispatch
    const evolutionApiUrl = process.env.EVOLUTION_API_URL;
    const evolutionApiKey = process.env.EVOLUTION_API_KEY;

    if (evolutionApiUrl && evolutionApiKey) {
      try {
        await axios.post(
          `${evolutionApiUrl}/message/sendText/${tenantId}`,
          { number: phoneNumber, text: finalReplyText },
          { headers: { apikey: evolutionApiKey, 'Content-Type': 'application/json' } }
        );
        console.log(`📤 [WHATSAPP DISPATCH] Sent to ${phoneNumber}`);
      } catch (dispatchErr: any) {
        console.error('❌ [WHATSAPP DISPATCH ERROR]:', dispatchErr?.response?.data || dispatchErr.message);
      }
    }

    return finalReplyText;
  } catch (error: any) {
    console.error('❌ [ENTERPRISE PLATFORM ERROR]:', error.message);
    throw error;
  }
}