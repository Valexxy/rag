import dotenv from 'dotenv';
dotenv.config();

import { processTenantMessage } from './src/enterprise-platform.js';

async function runLocalTest() {
  console.log('🧪 Starting Local AI Engine & Monnify Sandbox Test...\n');

  const testTenantId = '02c7067e-0eae-47f5-907a-9802adf6c000'; // Replace with a test tenant UUID
  const testPhoneNumber = '2349000000000';
  const testQuery = 'I want to buy a 5kW Residential Solar Panel Kit for 250000 NGN. Please send me a payment link. My name is Valentine.';

  try {
    const output = await processTenantMessage(testTenantId, testQuery, testPhoneNumber);
    console.log('\n================ AI OUTPUT REPLY ================');
    console.log(output);
    console.log('=================================================\n');
  } catch (err: any) {
    console.error('❌ Test Failed:', err.message);
  }
}

runLocalTest();