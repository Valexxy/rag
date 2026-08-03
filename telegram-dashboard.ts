// telegram-dashboard.ts
import express from 'express';
import { unmuteUserViaTelegram } from './enterprise-platform';

const telegramToken = process.env.TELEGRAM_BOT_TOKEN;
const adminChatId = process.env.TELEGRAM_ADMIN_CHAT_ID;

export async function sendTelegramHandoverWithButtons(phoneNumber: string, userQuery: string) {
  if (!telegramToken || !adminChatId) return;

  const alertMsg = `🚨 *HUMAN AGENT HANDOVER REQUESTED* 🚨\n\n📱 *User*: \`${phoneNumber}\`\n💬 *Query*: "${userQuery}"\n\n⚠️ AI responses are currently *MUTED*.`;

  // Telegram Inline Keyboard with Callback Buttons
  const inlineKeyboard = {
    inline_keyboard: [
      [
        { text: '🔓 Unmute AI', callback_data: `unmute:${phoneNumber}` },
        { text: '💬 View Details', callback_data: `details:${phoneNumber}` }
      ]
    ]
  };

  try {
    await fetch(`https://api.telegram.org/bot${telegramToken}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: adminChatId,
        text: alertMsg,
        parse_mode: 'Markdown',
        reply_markup: inlineKeyboard
      })
    });
  } catch (err) {
    console.error('❌ Failed to send Telegram alert with buttons:', err);
  }
}

// Telegram Webhook Handler for Button Click Callbacks
export function registerTelegramWebhookListener(app: express.Application) {
  app.post('/telegram-webhook', async (req, res) => {
    const { callback_query } = req.body;

    if (callback_query) {
      const data = callback_query.data; // e.g. "unmute:+23480000000"
      const [action, phoneNumber] = data.split(':');

      if (action === 'unmute') {
        await unmuteUserViaTelegram(phoneNumber);

        // Acknowledge Telegram callback
        await fetch(`https://api.telegram.org/bot${telegramToken}/answerCallbackQuery`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            callback_query_id: callback_query.id,
            text: `AI has been unmuted for ${phoneNumber}`
          })
        });

        // Edit original Telegram alert message
        await fetch(`https://api.telegram.org/bot${telegramToken}/editMessageText`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            chat_id: callback_query.message.chat.id,
            message_id: callback_query.message.message_id,
            text: `✅ *RESOLVED / UNMUTED*\n\n📱 *User*: \`${phoneNumber}\`\nAI conversation active.`,
            parse_mode: 'Markdown'
          })
        });
      }
    }

    res.sendStatus(200);
  });
}