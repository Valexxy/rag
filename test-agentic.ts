import { processAgenticQuery } from './agentic-rag';

async function runWorldClassTests() {
  console.log('\n================ 🚀 REASONING & INTENT AGENTIC TEST 🚀 ================ \n');

  const testPhone = '+2349012345678_val_test';

  // Test 1: Personal Family/Friend Chat (Should MUTE AI)
  console.log('💬 Query 1: "Hey bro, are you free for lunch today?"');
  const res1 = await processAgenticQuery('Hey bro, are you free for lunch today?', testPhone);
  console.log('🤖 Action:', res1.action);
  console.log('🤖 Intent:', res1.intent);
  console.log('🤖 Text Reply:', res1.text === null ? '[MUTED - AI Stayed Silent for Personal Chat]' : res1.text);
  console.log('\n----------------------------------------------------\n');

  // Test 2: Business Inquiry (Should RAG & RESPOND)
  console.log('💬 Query 2: "How much is paracetamol 500mg and do you have stock?"');
  const res2 = await processAgenticQuery('How much is paracetamol 500mg and do you have stock?', testPhone);
  console.log('🤖 Action:', res2.action);
  console.log('🤖 Intent:', res2.intent);
  console.log('🤖 Text Reply:\n', res2.text);
  console.log('\n----------------------------------------------------\n');

  // Test 3: Human Agent Request (Should TRANSFER_HUMAN & Lock State)
  console.log('💬 Query 3: "I want to talk to the business owner right now"');
  const res3 = await processAgenticQuery('I want to talk to the business owner right now', testPhone);
  console.log('🤖 Action:', res3.action);
  console.log('🤖 Intent:', res3.intent);
  console.log('🤖 Text Reply:\n', res3.text);
  console.log('\n----------------------------------------------------\n');

  // Test 4: Subsequent message after Handover Lock (Should MUTE_AI)
  console.log('💬 Query 4: "Hello? Is anyone there?"');
  const res4 = await processAgenticQuery('Hello? Is anyone there?', testPhone);
  console.log('🤖 Action:', res4.action);
  console.log('🤖 Text Reply:', res4.text === null ? '[MUTED - Handover Active]' : res4.text);
  console.log('\n====================================================\n');
}

runWorldClassTests();