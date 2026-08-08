import sys, os, time
sys.stdout.reconfigure(encoding='utf-8')

from database import get_tenant_by_instance
from main import _process_whatsapp_message_sync

payload = {
    "event": "messages.upsert",
    "instance": "store-bot",
    "data": {
        "key": {
            "remoteJid": "2348072015725@s.whatsapp.net",
            "fromMe": True,
            "id": f"TEST-FLOW-{time.time()}"
        },
        "pushName": "Store Owner",
        "message": {
            "conversation": "1.5kva"
        }
    }
}

print("Executing _process_whatsapp_message_sync locally...")
res = _process_whatsapp_message_sync("store-bot", payload)
print("RESULT:", res)
