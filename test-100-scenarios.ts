import { processAgenticQueryEnterprise } from './agentic-rag-enterprise';

const SCENARIOS = [
  // --------------------------------------------------------------------------
  // CATEGORY 1: PERSONAL & SOCIAL CHAT (Target: MUTE_AI) - 15 Scenarios
  // --------------------------------------------------------------------------
  { id: 1, query: "Hey bro, are you free for lunch today?", expectedAction: "MUTE_AI" },
  { id: 2, query: "Did you watch the match last night?", expectedAction: "MUTE_AI" },
  { id: 3, query: "Mum said to tell you to call her back.", expectedAction: "MUTE_AI" },
  { id: 4, query: "Are you home yet?", expectedAction: "MUTE_AI" },
  { id: 5, query: "Good morning boss, hope you slept well?", expectedAction: "MUTE_AI" },
  { id: 6, query: "Send me the address for the party tonight", expectedAction: "MUTE_AI" },
  { id: 7, query: "Bro, can I borrow your car tomorrow?", expectedAction: "MUTE_AI" },
  { id: 8, query: "Happy birthday my friend! Have a blessed day", expectedAction: "MUTE_AI" },
  { id: 9, query: "Are we still meeting at 4pm?", expectedAction: "MUTE_AI" },
  { id: 10, query: "Where are you?", expectedAction: "MUTE_AI" },
  { id: 11, query: "lol that joke was funny", expectedAction: "MUTE_AI" },
  { id: 12, query: "Goodnight bro, talk tomorrow", expectedAction: "MUTE_AI" },
  { id: 13, query: "Call me when you are driving back", expectedAction: "MUTE_AI" },
  { id: 14, query: "Who won the premier league match?", expectedAction: "MUTE_AI" },
  { id: 15, query: "Are you busy?", expectedAction: "MUTE_AI" },

  // --------------------------------------------------------------------------
  // CATEGORY 2: HUMAN HANDOVER ESCALATIONS (Target: TRANSFER_HUMAN) - 15 Scenarios
  // --------------------------------------------------------------------------
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

  // --------------------------------------------------------------------------
  // CATEGORY 3: PHARMACEUTICAL & MEDICAL SAFETY - 15 Scenarios
  // --------------------------------------------------------------------------
  { id: 31, query: "How much is paracetamol 500mg and do you have stock?", expectedAction: "RESPOND" },
  { id: 32, query: "Do you sell amoxicillin antibiotics?", expectedAction: "RESPOND" },
  { id: 33, query: "I have a severe fever and headache, what can I take?", expectedAction: "RESPOND" },
  { id: 34, query: "How many tablets of paracetamol are in a pack?", expectedAction: "RESPOND" },
  { id: 35, query: "Is prescription required for amoxicillin?", expectedAction: "RESPOND" },
  { id: 36, query: "What painkillers do you have available?", expectedAction: "RESPOND" },
  { id: 37, query: "Can I buy 50 boxes of paracetamol?", expectedAction: "RESPOND" },
  { id: 38, query: "What is the price of telehealth consultation?", expectedAction: "RESPOND" },
  { id: 39, query: "Do you offer doctor GP appointment slots?", expectedAction: "RESPOND" },
  { id: 40, query: "I need antibiotics for a throat infection", expectedAction: "RESPOND" },
  { id: 41, query: "Do you have cough syrup or fever medicine?", expectedAction: "RESPOND" },
  { id: 42, query: "What pharma products do you carry?", expectedAction: "RESPOND" },
  { id: 43, query: "Are antibiotics available for immediate delivery?", expectedAction: "RESPOND" },
  { id: 44, query: "How much does a doctor visit cost?", expectedAction: "RESPOND" },
  { id: 45, query: "Is there any fever reducer in stock?", expectedAction: "RESPOND" },

  // --------------------------------------------------------------------------
  // CATEGORY 4: MULTI-INDUSTRY PRODUCT & SERVICE INQUIRIES - 15 Scenarios
  // --------------------------------------------------------------------------
  { id: 46, query: "Do you have any organic coffee beans with lemon notes?", expectedAction: "RESPOND" },
  { id: 47, query: "How much is an ocean view suite overnight?", expectedAction: "RESPOND" },
  { id: 48, query: "Do you offer 5kW residential solar panel kits?", expectedAction: "RESPOND" },
  { id: 49, query: "What is the cost for deep home cleaning 3 bedroom?", expectedAction: "RESPOND" },
  { id: 50, query: "Do you sell commercial battery storage units?", expectedAction: "RESPOND" },
  { id: 51, query: "Is solar roof audit service available?", expectedAction: "RESPOND" },
  { id: 52, query: "How much is SAT prep 1-on-1 coaching?", expectedAction: "RESPOND" },
  { id: 53, query: "Full stack coding bootcamp price?", expectedAction: "RESPOND" },
  { id: 54, query: "Language immersion class pricing?", expectedAction: "RESPOND" },
  { id: 55, query: "Do you have battery storage units in stock?", expectedAction: "RESPOND" },
  { id: 56, query: "Book a cleaning service for my apartment", expectedAction: "RESPOND" },
  { id: 57, query: "How much is solar installation?", expectedAction: "RESPOND" },
  { id: 58, query: "What hotel room suites are available?", expectedAction: "RESPOND" },
  { id: 59, query: "Tell me about your coding bootcamp", expectedAction: "RESPOND" },
  { id: 60, query: "What solar panel packages do you sell?", expectedAction: "RESPOND" },

  // --------------------------------------------------------------------------
  // CATEGORY 5: EXACT & SEMANTIC CACHING SPEED STRESS - 10 Scenarios
  // --------------------------------------------------------------------------
  { id: 61, query: "How much is paracetamol 500mg and do you have stock?", expectedAction: "RESPOND" }, // L1 Cache Hit
  { id: 62, query: "What is the price of paracetamol 500mg and stock count?", expectedAction: "RESPOND" }, // L2 Cache Hit
  { id: 63, query: "Hey bro, are you free for lunch today?", expectedAction: "MUTE_AI" }, // L1 Cache Hit
  { id: 64, query: "Bro are you free for lunch today?", expectedAction: "MUTE_AI" }, // L2 Cache Hit
  { id: 65, query: "How much is an ocean view suite overnight?", expectedAction: "RESPOND" }, // L1 Cache Hit
  { id: 66, query: "Price for ocean view suite per night?", expectedAction: "RESPOND" }, // L2 Cache Hit
  { id: 67, query: "Do you have any organic coffee beans with lemon notes?", expectedAction: "RESPOND" }, // L1
  { id: 68, query: "Organic coffee beans with lemon tasting notes price?", expectedAction: "RESPOND" }, // L2
  { id: 69, query: "How much is 5kW residential solar panel kit?", expectedAction: "RESPOND" },
  { id: 70, query: "Cost of 5kW solar panel kit?", expectedAction: "RESPOND" },

  // --------------------------------------------------------------------------
  // CATEGORY 6: AMBIGUOUS & HYBRID EDGE CASES - 10 Scenarios
  // --------------------------------------------------------------------------
  { id: 71, query: "Hello, do you have solar panel kit or hotel rooms?", expectedAction: "RESPOND" },
  { id: 72, query: "What services do you provide?", expectedAction: "RESPOND" },
  { id: 73, query: "Are you open on Sundays?", expectedAction: "RESPOND" },
  { id: 74, query: "Where is your store located?", expectedAction: "RESPOND" },
  { id: 75, query: "Do you accept credit card or bank transfer?", expectedAction: "RESPOND" },
  { id: 76, query: "Is there discount on bulk orders?", expectedAction: "RESPOND" },
  { id: 77, query: "Price list please", expectedAction: "RESPOND" },
  { id: 78, query: "Catalog", expectedAction: "RESPOND" },
  { id: 79, query: "Hi", expectedAction: "RESPOND" },
  { id: 80, query: "Hello good day", expectedAction: "RESPOND" },

  // --------------------------------------------------------------------------
  // CATEGORY 7: OUT-OF-SCOPE & SPAM - 10 Scenarios
  // --------------------------------------------------------------------------
  { id: 81, query: "What is the capital of France?", expectedAction: "RESPOND" }, // Out of scope redirect
  { id: 82, query: "Write a python script to calculate fibonacci", expectedAction: "RESPOND" },
  { id: 83, query: "Who is the president of the United States?", expectedAction: "RESPOND" },
  { id: 84, query: "Explain quantum mechanics in simple terms", expectedAction: "RESPOND" },
  { id: 85, query: "asdfghjkl12345", expectedAction: "RESPOND" },
  { id: 86, query: "Tell me a joke", expectedAction: "RESPOND" },
  { id: 87, query: "What is 25 multiplied by 48?", expectedAction: "RESPOND" },
  { id: 88, query: "Crypto bitcoin signals today", expectedAction: "RESPOND" },
  { id: 89, query: "How do I build a rocket?", expectedAction: "RESPOND" },
  { id: 90, query: "Sing me a song", expectedAction: "RESPOND" },

  // --------------------------------------------------------------------------
  // CATEGORY 8: POST-HANDOVER MUTE STATE LOCK - 10 Scenarios
  // --------------------------------------------------------------------------
  { id: 91, query: "Hello is anyone there?", expectedAction: "MUTE_AI", lockUser: true },
  { id: 92, query: "Are you ignoring me?", expectedAction: "MUTE_AI", lockUser: true },
  { id: 93, query: "How much is paracetamol?", expectedAction: "MUTE_AI", lockUser: true },
  { id: 94, query: "Hey bro lunch?", expectedAction: "MUTE_AI", lockUser: true },
  { id: 95, query: "Please reply", expectedAction: "MUTE_AI", lockUser: true },
  { id: 96, query: "Is the owner coming?", expectedAction: "MUTE_AI", lockUser: true },
  { id: 97, query: "I am waiting", expectedAction: "MUTE_AI", lockUser: true },
  { id: 98, query: "Test message", expectedAction: "MUTE_AI", lockUser: true },
  { id: 99, query: "Urgent response needed", expectedAction: "MUTE_AI", lockUser: true },
  { id: 100, query: "Bye", expectedAction: "MUTE_AI", lockUser: true }
];

async function run100ScenarioSuite() {
  console.log('\n========================================================================');
  console.log('🚀 ENTERPRISE STRESS TEST: 100 AUTOMATED SCENARIOS');
  console.log('========================================================================\n');

  let passed = 0;
  let failed = 0;
  const startTime = Date.now();

  for (const item of SCENARIOS) {
    const testPhone = item.lockUser ? '+234900000000_locked_user' : `+23490${item.id.toString().padStart(6, '0')}`;
    
    // Lock state pre-test for Scenarios 91-100
    if (item.id === 91) {
      await processAgenticQueryEnterprise("Transfer me to an agent please", testPhone);
    }

    const t0 = Date.now();
    const result = await processAgenticQueryEnterprise(item.query, testPhone);
    const latency = Date.now() - t0;

    const isMatch = result.action === item.expectedAction;
    if (isMatch) {
      passed++;
      console.log(`✅ [SCENARIO ${item.id.toString().padStart(3, '0')}] PASS | Latency: ${latency}ms | Action: ${result.action} | Source: ${result.source || 'LOCKED'}`);
    } else {
      failed++;
      console.log(`❌ [SCENARIO ${item.id.toString().padStart(3, '0')}] FAIL | Expected: ${item.expectedAction} | Got: ${result.action} | Query: "${item.query}"`);
    }
  }

  const totalTime = ((Date.now() - startTime) / 1000).toFixed(2);
  console.log('\n========================================================================');
  console.log(`📊 FINAL BENCHMARK RESULTS: ${passed}/100 PASSED (${((passed / 100) * 100).toFixed(1)}%)`);
  console.log(`⏱️ Total Execution Time: ${totalTime}s`);
  console.log('========================================================================\n');
}

run100ScenarioSuite();