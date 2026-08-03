// server.ts
import express, { Request, Response } from 'express';
import { messageQueue } from './queue.js';

const app = express(); // 👈 Initialized first!

// 1. Mandatory Middleware: Parse JSON incoming requests
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Root health check route
app.get('/', (req, res) => {
  res.json({ status: 'online', message: 'RAG Backend API is running successfully!' });
});

// 2. Health check route (useful for verifying ngrok/server health)
app.get('/health', (_req: Request, res: Response) => {
  res.status(200).json({ status: 'OK', timestamp: new Date().toISOString() });
});

// 3. Webhook Route for incoming multi-tenant WhatsApp messages
app.post('/webhook/whatsapp/:tenantId', async (req: Request, res: Response) => {
  const { tenantId } = req.params;

  // Safely extract req.body with fallback to prevent destructuring crashes
  const body = req.body || {};
  const phoneNumber = body.phoneNumber || body.phone || 'unknown';
  const userQuery = body.userQuery || body.message || body.text;

  // Validate required inputs
  if (!tenantId) {
    return res.status(400).json({ error: 'Missing tenantId in URL parameter.' });
  }

  if (!userQuery) {
    console.warn(`⚠️ [BAD REQUEST] Missing userQuery parameter from tenant: ${tenantId}`);
    return res.status(400).json({ 
      error: 'Missing userQuery payload parameter.', 
      receivedBody: body 
    });
  }

  try {
    // Add message job to BullMQ Redis Queue
    const job = await messageQueue.add('tenant-message-job', {
      tenantId,
      phoneNumber,
      userQuery,
      timestamp: Date.now()
    });

    console.log(`📥 [JOB QUEUED] ID: ${job.id} | Tenant: ${tenantId} | Phone: ${phoneNumber}`);

    return res.status(200).json({
      status: 'queued',
      jobId: job.id,
      tenantId,
      phoneNumber
    });
  } catch (err: any) {
    console.error('❌ [SERVER ERROR] Webhook queue dispatch error:', err?.message || err);
    return res.status(500).json({ error: 'Internal gateway processing error.' });
  }
});

// 4. Fallback route for unmatched endpoints
app.use((req: Request, res: Response) => {
  res.status(404).json({ error: `Cannot ${req.method} ${req.originalUrl}` });
});

// 5. Start Express Listener
const PORT = Number(process.env.PORT) || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});