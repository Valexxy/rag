import os
import requests

def get_evolution_credentials():
    url = os.environ.get("EVOLUTION_API_URL", "https://evolution-api-latest-gxue.onrender.com").rstrip("/")
    key = os.environ.get("EVOLUTION_API_KEY", "F84B4F845BC6-464A-AD0E-553FD1046981")
    return url, key

def send_whatsapp_presence(instance_name: str, phone: str, state: str = "composing"):
    """Triggers 'typing...' indicator on WhatsApp with low latency."""
    url_base, key = get_evolution_credentials()
    url = f"{url_base}/chat/sendPresence/{instance_name}"
    headers = {"apikey": key, "Content-Type": "application/json"}
    try:
        requests.post(url, json={"number": phone, "delay": 1200, "presence": state}, headers=headers, timeout=5)
    except Exception as e:
        print(f"[WARNING] Presence signal skipped: {e}")

BOT_SENT_MSG_IDS = set()

def is_bot_sent_message(msg_id: str) -> bool:
    return bool(msg_id and msg_id in BOT_SENT_MSG_IDS)

def record_bot_sent_message(msg_id: str):
    if msg_id:
        BOT_SENT_MSG_IDS.add(msg_id)
        if len(BOT_SENT_MSG_IDS) > 2000:
            BOT_SENT_MSG_IDS.clear()

def send_whatsapp_message(instance_name: str, phone: str, text: str, buttons: list = None) -> bool:
    """Delivers clean, perfectly formatted WhatsApp messages with quick option shortcuts."""
    url_base, key = get_evolution_credentials()
    headers = {"apikey": key, "Content-Type": "application/json"}
    url = f"{url_base}/message/sendText/{instance_name}"

    clean_phone = "".join(filter(str.isdigit, str(phone)))
    final_text = text.strip()

    if buttons and len(buttons) > 0:
        button_options = "\n".join([f"👉 *Reply {idx+1}* for {btn.strip()}" for idx, btn in enumerate(buttons[:3])])
        final_text = f"{final_text}\n\n─────────────────\n{button_options}"

    payload = {
        "number": clean_phone,
        "text": final_text
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        if res.status_code in [200, 201]:
            try:
                res_json = res.json()
                msg_id = res_json.get("key", {}).get("id") or res_json.get("messageId")
                record_bot_sent_message(msg_id)
            except Exception:
                pass
            return True
        return False
    except Exception as e:
        print(f"[ERROR] Error sending WhatsApp message: {e}")
        return False

def broadcast_whatsapp_message(instance_name: str, phone_list: list, text: str) -> int:
    """Dispatches announcement broadcast across registered contacts."""
    successful = 0
    for phone in phone_list:
        if send_whatsapp_message(instance_name, phone, text):
            successful += 1
    return successful