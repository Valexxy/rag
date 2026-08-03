// enterprise-master-rag.ts (Ensure correct query handling)
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL || '',
  process.env.SUPABASE_SERVICE_ROLE_KEY || ''
);

export async function logCatalogGap(tenantId: string, query: string) {
  const { error } = await supabase
    .from('telemetry_logs')
    .insert({
      tenant_id: tenantId,
      user_query: query,
      ai_response: 'CATALOG_GAP_DETECTED'
    });

  if (error) {
    console.error('Error logging catalog gap:', error.message);
  }
}