import { processLocalFirstQuery } from './local-first-rag';

const SCENARIOS = [
  // 1-15: Personal
  { id: 1, query: "Hey bro, are you free for lunch today?", expectedAction: "MUTE_AI" },
  { id: 2, query: "Did you watch the match last night?", expectedAction: "MUTE_AI" },
  { id: 3, query: "Mum said to tell you to call her back.", expectedAction: "MUTE_AI" },
  { id: 4, query: "Are you home yet?", expectedAction: "MUTE_AI" },
  { id: 5, query: "Good morning boss, hope you slept well?", expectedAction: "MUTE_AI" },
  { id: 6, query: "Who won the premier league match?", expectedAction: "MUTE_AI" },
  { id: 7, query: "Bro, can I borrow your car tomorrow?", expectedAction: "MUTE_AI" },
  { id: 8, query: "Happy birthday my friend! Have a blessed day", expectedAction: "MUTE_AI" },
  { id: 9, query: "Are we still meeting at 4pm?", expectedAction: "MUTE_AI" },
  { id: 10, query: "Where are you?", expectedAction: "MUTE_AI" },
  { id: 11, query: "lol that joke was funny", expectedAction: "MUTE_AI" },
  { id: 12, query: "Goodnight bro, talk tomorrow", expectedAction: "MUTE_AI" },
  { id: 13, query: "Call me when you are driving back", expectedAction: "MUTE_AI" },
  { id: 14, query: "Who won the premier league match?", expectedAction: "MUTE_AI" },
  { id: 15, query: "Are you busy?", expectedAction: "MUTE_AI" },

  // 16-30: Human Handover
  { id: 16, query: "Can I speak to a real person please?", expectedAction: "TRANSFER_HUMAN" },
  { id: 17, query: "I want to talk to the business owner right now", expectedAction: "TRANSFER_HUMAN" },
  { id: 18, query: "I have a severe complaint about my order", expectedAction: "TRANSFER_HUMAN" },
  { id: 19, query: "Your service is terrible, connect me to a manager!", expectedAction: "TRANSFER_HUMAN" },
  { id: 20, query: "I demand a refund immediately", expectedAction: "TRANSFER_HUMAN" },
  { id: 21, query: "Transfer me to an agent", expectedAction: "TRANSFER_HUMAN" },
  { id: 22, query: "Human support please", expectedAction: "TRANSFER_HUMAN" },
  { id: 23, query: "I need customer service representative now", expectedAction: "TRANSFER_HUMAN" },
  { id: 24, query: "Stop sending AI answers, I need a real human!", expectedAction: "TRANSFER_HUMAN" },
  { id: 25, query: "Connect me with someone who can solve my issue", expectedAction: "TRANSFER_HUMAN" },
  { id: 26, query: "Give me the direct line of your manager", expectedAction: "TRANSFER_HUMAN" },
  { id: 27, query: "I am taking legal action, put a human on!", expectedAction: "TRANSFER_HUMAN" },
  { id: 28, query: "Human please", expectedAction: "TRANSFER_HUMAN" },
  { id: 29, query: "Let me talk to the owner", expectedAction: "TRANSFER_HUMAN" },
  { id: 30, query: "Representative required", expectedAction: "TRANSFER_HUMAN" },

  // 31-40: Medical & Business
  { id: 31, query: "How much is paracetamol 500mg and do you have stock?", expectedAction: "RESPOND" },
  { id: 32, query: "Do you sell amoxicillin antibiotics?", expectedAction: "RESPOND" },
  { id: 33, query: "I have a severe fever and headache, what can I take?", expectedAction: "RESPOND" },
  { id: 34, query: "How many tablets of paracetamol are in a pack?", expectedAction: "RESPOND" },
  { id: 35, query: "Is prescription required for amoxicillin?", expectedAction: "RESPOND" },

  // 41-43: Post-Handover State Lock
  { id: 41, query: "Hello is anyone there?", expectedAction: "MUTE_AI", lockUser: true },
  { id: 42, query: "Are you ignoring me?", expectedAction: "MUTE_AI", lockUser: true },
  { id: 43, query: "How much is paracetamol?", expectedAction: "MUTE_AI", lockUser: true }
];

async function runLocalFirstStressSuite() {
  console.log('\n========================================================================');
  console.log('⚡ LOCAL-FIRST RAG BENCHMARK (Clean Isolation)');
  console.log('========================================================================\n');

  let passed = 0;
  let failed = 0;

  for (const item of SCENARIOS) {
    // Assign clean isolated phone numbers per test item
    const testPhone = item.lockUser ? '+234900000000_locked_user' : `+2349000${item.id.toString().padStart(4, '0')}`;
    
    // Set up state lock for 41-43
    if (item.id === 41) {
      await processLocalFirstQuery("Transfer me to an agent please", testPhone);
    }

    const t0 = Date.now();
    const result = await processLocalFirstQuery(item.query, testPhone);
    const latency = Date.now() - t0;

    const isMatch = result.action === item.expectedAction;
    if (isMatch) {
      passed++;
      console.log(`✅ [SCENARIO ${item.id.toString().padStart(3, '0')}] PASS | ${latency}ms | Action: ${result.action} | Source: ${result.source}`);
    } else {
      failed++;
      console.log(`❌ [SCENARIO ${item.id.toString().padStart(3, '0')}] FAIL | Expected: ${item.expectedAction} | Got: ${result.action} | Query: "${item.query}"`);
    }
  }

  console.log('\n========================================================================');
  console.log(`📊 LOCAL BENCHMARK RESULT: ${passed}/${SCENARIOS.length} PASSED (${((passed / SCENARIOS.length) * 100).toFixed(1)}%)`);
  console.log('========================================================================\n');
}

runLocalFirstStressSuite();