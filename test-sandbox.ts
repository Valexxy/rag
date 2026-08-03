import { handleWhatsAppQuery } from './whatsapp-handler';

async function runProductionTests() {
  console.log('\n================ 🧪 PRODUCTION SAFETY & STATE TEST 🧪 ================ \n');

  const testUserPhone = '+1234567890_test_user';

  // 1. Test Medical Query (Verifies Prescription Warning + Disclaimer + Clean WhatsApp Bullets)
  console.log('💬 Query 1: Prescription & Medical Safety');
  const res1 = await handleWhatsAppQuery('I have a severe infection and fever, what antibiotics or painkillers do you have?', testUserPhone);
  console.log('🤖 Bot Reply:\n', res1);
  console.log('\n----------------------------------------------------\n');

  // 2. Test Human Transfer Trigger (Updates Supabase status to human_agent_requested)
  console.log('💬 Query 2: Requesting Human Agent');
  const res2 = await handleWhatsAppQuery('I want to speak with a human agent please', testUserPhone);
  console.log('🤖 Bot Reply:\n', res2);
  console.log('\n----------------------------------------------------\n');

  // 3. Test Subsequent Query While Handoff Active (Verifies AI Mute/Suppression)
  console.log('💬 Query 3: Follow-up query after human handover trigger');
  const res3 = await handleWhatsAppQuery('Hello? Are you there?', testUserPhone);
  console.log(`🤖 Bot Reply: ${res3 === null ? '[SUPPRESSED / NULL - Handled by Human Agent]' : res3}`);
  console.log('\n====================================================\n');
}

runProductionTests();