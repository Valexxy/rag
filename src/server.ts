import express from 'express';
import dotenv from 'dotenv';
dotenv.config();

import { processTenantMessage } from './enterprise-platform.js';

const app = express();
app.use(express.json());

/**
 * Endpoint called by n8n HTTP Request node ("Send to Local Enterprise Queue")
 */
app.post('/api/agent/chat', async (req, res) => {
  try {
    const { tenantId, userMessage, senderPhoneNumber } = req.body;

    // Validate incoming payload from n8n
    if (!tenantId || !userMessage || !senderPhoneNumber) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: tenantId, userMessage, or senderPhoneNumber'
      });
    }

    console.log(`📥 [INCOMING WEBHOOK] Tenant: ${tenantId} | From: ${senderPhoneNumber}`);

    // Process message through Gemini 2.5/Flash + Monnify + Supabase memory
    const reply = await processTenantMessage(tenantId, userMessage, senderPhoneNumber);

    // Return response back to n8n
    return res.status(200).json({
      success: true,
      tenantId,
      senderPhoneNumber,
      reply
    });
  } catch (error: any) {
    console.error('❌ [WEBHOOK ERROR]:', error.message);
    return res.status(500).json({ success: false, error: error.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Enterprise AI Server listening on port ${PORT}`);
});