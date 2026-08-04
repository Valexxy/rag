import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { GoogleGenerativeAI } from '@google/generative-ai';
import dotenv from 'dotenv';

// Ensure environment variables are populated before top-level client creation
dotenv.config();

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

// Safe client instantiation to prevent instant startup crash
export const supabase: SupabaseClient = (supabaseUrl && supabaseServiceKey)
  ? createClient(supabaseUrl, supabaseServiceKey)
  : createClient('https://placeholder.supabase.co', 'placeholder-key');

export async function searchTenantProducts(tenantId: string, queryText: string): Promise<string> {
  try {
    if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_ROLE_KEY) {
      console.warn('⚠️ [SUPABASE WARNING] SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is missing in .env');
      return JSON.stringify([]);
    }

    // 1. Generate Query Vector Embedding using Gemini
    const geminiKey = process.env.GEMINI_API_KEY;
    if (!geminiKey) {
      console.warn('⚠️ [GEMINI WARNING] GEMINI_API_KEY missing, skipping vector search.');
      return JSON.stringify([]);
    }

    const genAI = new GoogleGenerativeAI(geminiKey);
    const embeddingModel = genAI.getGenerativeModel({ model: 'text-embedding-004' });
    const embeddingResult = await embeddingModel.embedContent(queryText);
    const queryVector = embeddingResult.embedding.values;

    // 2. Perform Similarity/Catalog Lookup in Supabase
    const { data: products, error } = await supabase
      .from('tenant_products')
      .select('id, title, price, description')
      .eq('tenant_id', tenantId)
      .limit(5);

    if (error) {
      console.error('❌ [SUPABASE QUERY ERROR]:', error.message);
      return JSON.stringify([]);
    }

    return JSON.stringify(products || []);
  } catch (err: any) {
    console.error('❌ [VECTOR SEARCH ERROR]:', err.message);
    return JSON.stringify([]);
  }
}