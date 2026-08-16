process.on('uncaughtException', (err) => {
    console.error('[Baileys Uncaught Exception]', err.stack || err.message);
});

process.on('unhandledRejection', (reason) => {
    console.error('[Baileys Unhandled Rejection]', reason);
});

const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const express = require('express');
const http = require('http');
const QRCode = require('qrcode');
const fs = require('fs');
const pino = require('pino');

const app = express();
app.use(express.json());

const PORT = 8081;
const GOLANG_BACKEND = 'http://127.0.0.1:8080';


const logger = pino({ level: 'silent' });

let sock = null;
let latestDataUrl = '';
let isConnected = false;

function buildHTMLPage(qrDataUrl, pairingCodeMsg = '') {
    if (isConnected) {
        return `<!DOCTYPE html>
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
        <h1>🚀 24/7 WHATSAPP ENGINE IS CONNECTED & LIVE!</h1>
        <p>Your WhatsApp account is linked and running 24/7 with zero sleep. All customer messages are processed instantly by your Golang AI Engine.</p>
    </div>
</body>
</html>`;
    }

    const qrBlock = qrDataUrl ? `<img src="${qrDataUrl}" alt="WhatsApp QR Code">` : `<div style="padding:30px;color:#8b949e;">Initializing socket... Auto-refreshing in 3 seconds...</div>`;
    
    const pairingBlock = pairingCodeMsg ? `<div style="background:#1f6feb;color:white;padding:15px;border-radius:10px;font-size:20px;font-weight:bold;margin:15px 0;">${pairingCodeMsg}</div>` : '';

    return `<!DOCTYPE html>
<html>
<head>
    <title>WhatsApp 24/7 Pair Portal</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="6">
    <style>
        body { background: #0d1117; color: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 20px; text-align: center; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 16px; padding: 30px; max-width: 420px; width: 100%; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { color: #58a6ff; font-size: 22px; margin-bottom: 8px; }
        p { color: #8b949e; font-size: 14px; margin-top: 0; }
        img { width: 250px; height: 250px; border-radius: 12px; border: 4px solid #238636; margin: 15px 0; padding: 8px; background: white; }
        .divider { border-top: 1px solid #30363d; margin: 20px 0; }
        input { width: 80%; padding: 12px; border-radius: 8px; border: 1px solid #30363d; background: #0d1117; color: white; font-size: 16px; text-align: center; margin-bottom: 10px; }
        button { background: #238636; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-size: 15px; font-weight: bold; cursor: pointer; width: 85%; }
        button:hover { background: #2ea043; }
        .steps { text-align: left; background: #0d1117; border-radius: 8px; padding: 15px; font-size: 13px; color: #8b949e; margin-top: 15px; }
        .steps ol { margin: 0; padding-left: 20px; }
        .steps li { margin-bottom: 6px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>📲 Pair WhatsApp 24/7</h1>
        <p>Method 1: Scan QR Code with Phone Camera</p>
        ${qrBlock}
        ${pairingBlock}

        <div class="divider"></div>
        <p style="color:#58a6ff;font-weight:bold;">Method 2: Link via 8-Digit Code (No Camera Needed)</p>
        <form action="/pair-submit" method="GET">
            <input type="text" name="phone" placeholder="e.g. 2348072015725" value="2348072015725" required />
            <br>
            <button type="submit">Get 8-Digit Pairing Code ⚡</button>
        </form>

        <div class="steps">
            <ol>
                <li>Open WhatsApp on your phone</li>
                <li>Tap <b>Menu (⋮)</b> or <b>Settings</b> $\rightarrow$ <b>Linked Devices</b></li>
                <li>Tap <b>Link a Device</b> $\rightarrow$ Tap <b>Link with phone number instead</b></li>
                <li>Enter the 8-digit code shown above!</li>
            </ol>
        </div>
    </div>
</body>
</html>`;
}

let activePairingCode = '';

async function connectToWhatsApp() {
    try {
        let authResult;
        try {
            if (!fs.existsSync('baileys_auth')) {
                fs.mkdirSync('baileys_auth', { recursive: true });
            }
            authResult = await useMultiFileAuthState('baileys_auth');
        } catch (e) {
            console.error('[Baileys Self-Healing] Clearing corrupted auth session:', e.message);
            try { fs.rmSync('baileys_auth', { recursive: true, force: true }); } catch (rmErr) {}
            fs.mkdirSync('baileys_auth', { recursive: true });
            authResult = await useMultiFileAuthState('baileys_auth');
        }
        const { state, saveCreds } = authResult;

        sock = makeWASocket({
            auth: state,
            logger: logger,
            printQRInTerminal: true,
            browser: ['Ubuntu', 'Chrome', '120.0.0.0']
        });

        sock.ev.on('creds.update', saveCreds);


        sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;
            console.log('[Baileys Connection Update]', connection || '', qr ? 'QR Code Available' : '');

            if (qr) {
                try {
                    latestDataUrl = await QRCode.toDataURL(qr);
                } catch (e) {
                    console.error('[QR DataURL Error]', e.message);
                }
            }

            if (connection === 'close') {
                isConnected = false;
                const statusCode = lastDisconnect?.error?.output?.statusCode;
                const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
                console.log('[Baileys Socket Closed] Status Code:', statusCode, 'Reconnect:', shouldReconnect);
                if (shouldReconnect) {
                    setTimeout(connectToWhatsApp, 3000);
                }
            } else if (connection === 'open') {
                isConnected = true;
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
    res.send(buildHTMLPage(latestDataUrl, activePairingCode));
});

app.get('/pair-json', async (req, res) => {
    const phone = req.query.phone || '2348072015725';
    const cleanPhone = phone.replace(/[^0-9]/g, '');
    if (!sock) {
        return res.status(503).json({ status: 'initializing', message: 'Baileys socket starting... Retry in 3 seconds' });
    }
    try {
        const code = await sock.requestPairingCode(cleanPhone);
        return res.json({
            status: 'success',
            phone: cleanPhone,
            pairingCode: code,
            instructions: `Open WhatsApp on phone ${cleanPhone} -> Linked Devices -> Link with phone number instead -> Enter 8-digit code: ${code}`
        });
    } catch (err) {
        return res.status(500).json({ status: 'error', error: err.message });
    }
});

app.get('/pair-submit', async (req, res) => {
    const phone = req.query.phone || '2348072015725';
    const cleanPhone = phone.replace(/[^0-9]/g, '');
    if (sock && cleanPhone) {
        try {
            const code = await sock.requestPairingCode(cleanPhone);
            activePairingCode = `🔑 YOUR PAIRING CODE: ${code}`;
            console.log(`[Baileys Pairing Code] Generated code for ${cleanPhone}: ${code}`);
        } catch (err) {
            activePairingCode = `⚠️ Pairing Error: ${err.message}`;
        }
    }
    res.setHeader('Content-Type', 'text/html');
    res.send(buildHTMLPage(latestDataUrl, activePairingCode));
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

app.listen(PORT, '0.0.0.0', () => {
    console.log(`[Baileys Gateway] Express server listening on 0.0.0.0:${PORT}`);
    connectToWhatsApp();
});

