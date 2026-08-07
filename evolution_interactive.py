import os
import requests

EVOLUTION_URL = os.environ.get("EVOLUTION_API_URL", "").rstrip("/")
EVOLUTION_KEY = os.environ.get("EVOLUTION_API_KEY", "")

def send_whatsapp_presence(instance_name: str, phone: str, state: str = "composing"):
    """Triggers 'typing...' indicator on WhatsApp with low latency."""
    url = f"{EVOLUTION_URL}/chat/sendPresence/{instance_name}"
    headers = {"apikey": EVOLUTION_KEY, "Content-Type": "application/json"}
    try:
        requests.post(url, json={"number": phone, "delay": 1200, "presence": state}, headers=headers, timeout=5)
    except Exception as e:
        print(f"⚠️ Presence signal skipped: {e}")

def send_whatsapp_message(instance_name: str, phone: str, text: str, buttons: list = None) -> bool:
    """Delivers clean, perfectly formatted WhatsApp messages with high reliability across all devices."""
    headers = {"apikey": EVOLUTION_KEY, "Content-Type": "application/json"}
    url = f"{EVOLUTION_URL}/message/sendText/{instance_name}"

    final_text = text.strip()

    # Append quick option shortcuts naturally if button options exist
    if buttons and len(buttons) > 0:
        button_options = "\n".join([f"👉 *Reply {idx+1}* for {btn.strip()}" for idx, btn in enumerate(buttons[:3])])
        final_text = f"{final_text}\n\n─────────────────\n{button_options}"

    payload = {
        "number": phone,
        "text": final_text
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        return res.status_code in [200, 201]
    except Exception as e:
        print(f"❌ Error sending WhatsApp message: {e}")
        return False

def broadcast_whatsapp_message(instance_name: str, phone_list: list, text: str) -> int:
    """Dispatches announcement broadcast across registered contacts."""
    successful = 0
    for phone in phone_list:
        if send_whatsapp_message(instance_name, phone, text):
            successful += 1
    return successful