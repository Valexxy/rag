import Redis from 'ioredis';
import dotenv from 'dotenv';

dotenv.config();

const redisUrl = process.env.REDIS_URL;

// Automatically uses Layerbase (cloud) when deployed on Render, 
// and falls back to localhost when running on your PC.
export const connection = redisUrl
  ? new Redis(redisUrl, {
      maxRetriesPerRequest: null,
      enableReadyCheck: false,
    })
  : new Redis({
      host: '127.0.0.1',
      port: 6379,
      maxRetriesPerRequest: null,
    });

connection.on('connect', () => {
  console.log('Successfully connected to Redis!');
});

connection.on('error', (err) => {
  console.error('Redis connection error:', err);
});