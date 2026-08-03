const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const SUPABASE_URL = process.env.SUPABASE_URL || 'https://emohdirbihcpnnmqtzrs.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY;

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

async function testRealRpcSearch() {
  console.log('🧪 Testing RPC search with a real stored embedding...\n');

  // 1. Fetch 1 real embedding from products table
  const { data: realProduct, error: fetchErr } = await supabase
    .from('products')
    .select('name, embedding')
    .limit(1)
    .single();

  if (fetchErr || !realProduct) {
    console.error('❌ Could not fetch product:', fetchErr);
    return;
  }

  let realVector = realProduct.embedding;
  if (typeof realVector === 'string') {
    realVector = JSON.parse(realVector);
  }

  // 2. Pass real vector into match_products RPC
  const { data: matches, error: rpcErr } = await supabase.rpc('match_products', {
    query_embedding: realVector,
    match_threshold: -1.0, // permissive threshold for test
    match_count: 3
  });

  if (rpcErr) {
    console.error('❌ RPC Call Failed:', rpcErr.message);
  } else {
    console.log(`🎉 SUCCESS! RPC returned ${matches.length} matching product(s):`);
    console.log(`📦 Top Match: "${matches[0]?.name}" (Similarity: ${matches[0]?.similarity})`);
  }
}

testRealRpcSearch();