import requests, time, sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://rag-403h.onrender.com/webhook/whatsapp/store-bot'
payload = {
    'event': 'messages.upsert',
    'instance': 'store-bot',
    'data': {
        'key': {'remoteJid': '2348072015725@s.whatsapp.net', 'fromMe': False, 'id': f'TEST-15KVA-{time.time()}'},
        'pushName': 'Store Owner',
        'message': {'conversation': '1.5kva'}
    }
}

t_start = time.time()
try:
    r = requests.post(url, json=payload, timeout=10)
    dur_ms = (time.time() - t_start) * 1000
    print(f"✅ LIVE CLOUD RESPONSE FOR '1.5kva' ({dur_ms:.0f}ms): {r.status_code} | {r.json()}")
except Exception as e:
    print(f"Cloud webhook error: {e}")
