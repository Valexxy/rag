const { supabase } = require('./supabaseClient');

/**
 * Searches for products using vector similarity.
 * @param {Array<number>} queryEmbedding - The embedding vector of the customer's query.
 * @param {number} matchThreshold - Minimum similarity score.
 * @param {number} matchCount - Maximum number of results to return.
 */
async function searchProducts(queryEmbedding, matchThreshold = 0.7, matchCount = 5) {
  try {
    const { data, error } = await supabase.rpc('match_products', {
      query_embedding: queryEmbedding,
      match_threshold: matchThreshold,
      match_count: matchCount
    });

    if (error) {
      console.error('Error searching products:', error.message);
      return [];
    }

    return data;
  } catch (err) {
    console.error('Unexpected search error:', err.message);
    return [];
  }
}

module.exports = { searchProducts };