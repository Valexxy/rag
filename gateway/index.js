const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const express = require('express');
const http = require('http');
const QRCode = require('qrcode');

const app = express();
app.use(express.json());

const PORT = 8081;
const GOLANG_BACKEND = 'http://127.0.0.1:8080';


let sock = null;
let currentQRCodeHTML = `<html style="background:#0d1117;color:white;font-family:sans-serif;text-align:center;padding:50px;">
  <h2>📱 WhatsApp Web Engine Initializing...</h2>
  <p>Please refresh this page in 3 seconds to scan the QR code.</p>
  <script>setTimeout(() => location.reload(), 3000);</script>
</html>`;

async function connectToWhatsApp() {
    try {
        const { state, saveCreds } = await useMultiFileAuthState('baileys_auth');
        sock = makeWASocket({
            auth: state,
            printQRInTerminal: true,
        });

        sock.ev.on('creds.update', saveCreds);

        sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;
            
            if (qr) {
                try {
                    const dataUrl = await QRCode.toDataURL(qr);
                    currentQRCodeHTML = `<!DOCTYPE html>
<html>
<head>
    <title>WhatsApp 24/7 QR Pair Portal</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="15">
    <style>
        body { background: #0d1117; color: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; text-align: center; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 16px; padding: 30px; max-width: 400px; width: 100%; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { color: #58a6ff; font-size: 22px; margin-bottom: 8px; }
        p { color: #8b949e; font-size: 14px; margin-top: 0; }
        img { width: 260px; height: 260px; border-radius: 12px; border: 4px solid #238636; margin: 20px 0; padding: 10px; background: white; }
        .steps { text-align: left; background: #0d1117; border-radius: 8px; padding: 15px; font-size: 13px; color: #8b949e; margin-top: 15px; }
        .steps ol { margin: 0; padding-left: 20px; }
        .steps li { margin-bottom: 6px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>📲 Pair WhatsApp Web 24/7</h1>
        <p>Scan this QR code with WhatsApp to connect your bot</p>
        <img src="${dataUrl}" alt="WhatsApp QR Code">
        <div class="steps">
            <ol>
                <li>Open WhatsApp on your phone</li>
                <li>Tap <b>Menu (⋮)</b> or <b>Settings</b></li>
                <li>Select <b>Linked Devices</b></li>
                <li>Tap <b>Link a Device</b> and scan this QR code</li>
            </ol>
        </div>
    </div>
</body>
</html>`;
                } catch (e) {
                    console.error('[QR Error]', e);
                }
            }

            if (connection === 'close') {
                const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
                console.log('[Baileys Gateway] Connection closed, reconnecting:', shouldReconnect);
                if (shouldReconnect) {
                    setTimeout(connectToWhatsApp, 3000);
                }
            } else if (connection === 'open') {
                console.log('[Baileys Gateway] 🚀 24/7 Embedded WhatsApp Web Socket Connected Successfully!');
                currentQRCodeHTML = `<!DOCTYPE html>
<html>
<head>
    <title>WhatsApp 24/7 Engine Live</title>
    <style>
        body { background: #0d1117; color: #3fb950; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; text-align: center; }
        .card { background: #161b22; border: 1px solid #238636; border-radius: 16px; padding: 40px; max-width: 450px; width: 100%; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { color: #3fb950; font-size: 24px; margin-bottom: 12px; }
        p { color: #c9d1d9; font-size: 15px; line-height: 1.5; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🚀 24/7 WhatsApp Engine CONNECTED & LIVE!</h1>
        <p>Your WhatsApp account is paired and running 24/7 with zero sleep. All incoming customer messages are processed instantly by your Golang AI Engine.</p>
    </div>
</body>
</html>`;
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

app.get('/qr', (req, res) => {
    res.setHeader('Content-Type', 'text/html');
    res.send(currentQRCodeHTML);
});

// Outbound text message endpoint
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

// Outbound media image card endpoint
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
