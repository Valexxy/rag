const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const express = require('express');
const http = require('http');

const app = express();
app.use(express.json());

const PORT = process.env.GATEWAY_PORT || 8081;
const GOLANG_BACKEND = process.env.GOLANG_BACKEND || 'http://127.0.0.1:8080';

let sock = null;

async function connectToWhatsApp() {
    try {
        const { state, saveCreds } = await useMultiFileAuthState('baileys_auth');
        sock = makeWASocket({
            auth: state,
            printQRInTerminal: true,
        });

        sock.ev.on('creds.update', saveCreds);

        sock.ev.on('connection.update', (update) => {
            const { connection, lastDisconnect } = update;
            if (connection === 'close') {
                const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
                console.log('[Baileys Gateway] Connection closed, reconnecting:', shouldReconnect);
                if (shouldReconnect) {
                    setTimeout(connectToWhatsApp, 3000);
                }
            } else if (connection === 'open') {
                console.log('[Baileys Gateway] 🚀 24/7 Embedded WhatsApp Web Socket Connected Successfully!');
            }
        });

        sock.ev.on('messages.upsert', async (m) => {
            if (m.type === 'notify') {
                for (const msg of m.messages) {
                    if (!msg.key.fromMe) {
                        const sender = msg.key.remoteJid.split('@')[0];
                        const text = msg.message?.conversation || msg.message?.extendedTextMessage?.text || '';
                        if (text) {
                            console.log(`[Baileys Gateway] Message from ${sender}: ${text}`);
                            // Forward directly to local Golang backend
                            try {
                                const payload = JSON.stringify({
                                    data: {
                                        key: { remoteJid: msg.key.remoteJid, fromMe: false },
                                        message: { conversation: text },
                                        pushName: msg.pushName || ''
                                    }
                                });
                                const req = http.request(`${GOLANG_BACKEND}/webhook/evolution`, {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                        'Content-Length': Buffer.byteLength(payload)
                                    }
                                }, () => {});
                                req.on('error', (err) => console.error('[Forward Error]', err.message));
                                req.write(payload);
                                req.end();
                            } catch (err) {
                                console.error('[Baileys Forward Error]', err.message);
                            }
                        }
                    }
                }
            }
        });
    } catch (err) {
        console.error('[Baileys Init Error]', err.message);
        setTimeout(connectToWhatsApp, 5000);
    }
}

// Endpoint to send outbound text messages from Golang engine
app.post('/message/sendText/:instance', async (req, res) => {
    const { number, text } = req.body;
    if (sock && number && text) {
        try {
            const jid = number.includes('@') ? number : `${number}@s.whatsapp.net`;
            await sock.sendMessage(jid, { text });
            return res.json({ status: 'sent' });
        } catch (err) {
            return res.status(500).json({ error: err.message });
        }
    }
    return res.status(500).json({ error: 'WhatsApp socket not ready' });
});

// Endpoint to send outbound media image cards from Golang engine
app.post('/message/sendMedia/:instance', async (req, res) => {
    const { number, media, caption } = req.body;
    if (sock && number && media) {
        try {
            const jid = number.includes('@') ? number : `${number}@s.whatsapp.net`;
            await sock.sendMessage(jid, { image: { url: media }, caption: caption || '' });
            return res.json({ status: 'sent' });
        } catch (err) {
            return res.status(500).json({ error: err.message });
        }
    }
    return res.status(500).json({ error: 'WhatsApp socket not ready' });
});

app.get('/health', (req, res) => res.json({ status: 'online', gateway: 'Baileys 24/7 Embedded Gateway' }));

app.listen(PORT, () => {
    console.log(`[Baileys Gateway] Express server listening on port ${PORT}`);
    connectToWhatsApp();
});
