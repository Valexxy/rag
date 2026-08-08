import requests, time, sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://rag-403h.onrender.com/webhook/whatsapp/store-bot'
payload = {
    'event': 'messages.upsert',
    'instance': 'store-bot',
    'data': {
        'key': {'remoteJid': '2348072015725@s.whatsapp.net', 'fromMe': False, 'id': f'TEST-GOLD-LIVE-{time.time()}'},
        'pushName': 'Store Owner',
        'message': {'conversation': '24k gold'}
    }
}

t_start = time.time()
try:
    r = requests.post(url, json=payload, timeout=15)
    dur_ms = (time.time() - t_start) * 1000
    print(f"✅ LIVE CLOUD RESPONSE ({dur_ms:.0f}ms): {r.status_code} | {r.json()}")
except Exception as e:
    print(f"Cloud webhook error: {e}")
