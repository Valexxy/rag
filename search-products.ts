import { createClient } from '@supabase/supabase-js';
import { pipeline, env } from '@xenova/transformers';
import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(__dirname, '.env') });

// Allow downloading from mirror / cached files
env.allowLocalModels = true;

const supabaseUrl = process.env.SUPABASE_URL!;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;

const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: {
    persistSession: false,
    autoRefreshToken: false,
  },
});

async function searchProducts(userQuery: string) {
  console.log(`🔎 User Query: "${userQuery}"`);
  console.log('⏳ Generating query embedding...');

  try {
    // 1. Convert user search query into a 384-dim vector locally
    const extractor = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
    const output = await extractor(userQuery, { pooling: 'mean', normalize: true });
    const queryEmbedding = Array.from(output.data);

    console.log('📡 Searching Supabase vector store...');

    // 2. Call the RPC function in Supabase
    const { data: results, error } = await supabase.rpc('match_products', {
      query_embedding: queryEmbedding,
      match_threshold: 0.1, // Lower threshold to ensure matches appear
      match_count: 5,
    });

    if (error) {
      console.error('❌ Search error:', error.message);
      return;
    }

    console.log('\n🎯 Top Semantic Match Results:');
    console.table(results);
  } catch (err: any) {
    console.error('❌ Embedding generation error:', err.message || err);
  }
}

// Test query
searchProducts('I have a headache and fever, what should I take?');