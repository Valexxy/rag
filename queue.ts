// queue.ts
import { Queue, Worker } from 'bullmq';
import Redis from 'ioredis';
import { processTenantMessage } from './enterprise-platform.js';

const getRedisConnection = () => {
  if (process.env.REDIS_URL) {
    return new Redis(process.env.REDIS_URL, {
      maxRetriesPerRequest: null,
      tls: process.env.REDIS_URL.startsWith('rediss://')
        ? { rejectUnauthorized: false }
        : undefined,
    });
  }

  return new Redis({
    host: process.env.REDIS_HOST || '127.0.0.1',
    port: Number(process.env.REDIS_PORT) || 6379,
    username: process.env.REDIS_USERNAME || undefined,
    password: process.env.REDIS_PASSWORD || undefined,
    maxRetriesPerRequest: null,
    tls: process.env.REDIS_TLS === 'true' ? { rejectUnauthorized: false } : undefined,
  });
};

export const connection = getRedisConnection();

export const messageQueue = new Queue('enterprise-multitenant-messages', { connection });

const worker = new Worker(
  'enterprise-multitenant-messages',
  async (job) => {
    const { tenantId, phoneNumber, userQuery } = job.data;
    console.log(`⚡ [REDIS WORKER] Processing message | Tenant: ${tenantId} | Phone: ${phoneNumber}`);
    
    const result = await processTenantMessage(tenantId, userQuery, phoneNumber);
    return result;
  },
  { connection }
);

worker.on('completed', (job) => {
  console.log(`✅ [JOB SUCCESS] ID: ${job.id}`);
});

worker.on('failed', (job, err) => {
  console.error(`❌ [JOB FAILURE] ID: ${job?.id} | Error: ${err.message}`);
});