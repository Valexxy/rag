import os
import requests

EVOLUTION_URL = os.environ.get("EVOLUTION_API_URL", "").rstrip("/")
EVOLUTION_KEY = os.environ.get("EVOLUTION_API_KEY", "")

def send_whatsapp_presence(instance_name: str, phone: str, presence: str = "composing"):
    """Sends a presence signal ('composing' shows 'typing...' on WhatsApp)."""
    url = f"{EVOLUTION_URL}/chat/sendPresence/{instance_name}"
    headers = {"apikey": EVOLUTION_KEY, "Content-Type": "application/json"}
    payload = {
        "number": phone,
        "presence": presence,
        "delay": 1200
    }
    try:
        requests.post(url, json=payload, headers=headers, timeout=2)
    except Exception as e:
        print(f"⚠️ Presence signal skipped: {e}")

def send_whatsapp_message(instance_name: str, phone: str, text: str):
    """Sends standard outbound WhatsApp text message."""
    url = f"{EVOLUTION_URL}/message/sendText/{instance_name}"
    headers = {"apikey": EVOLUTION_KEY, "Content-Type": "application/json"}
    payload = {"number": phone, "text": text}
    try:
        requests.post(url, json=payload, headers=headers, timeout=5)
    except Exception as e:
        print(f"❌ Error sending outbound message: {e}")

def send_whatsapp_interactive_buttons(instance_name: str, phone: str, body_text: str, buttons: list):
    """Sends native interactive buttons with fallback to standard formatted text."""
    url = f"{EVOLUTION_URL}/message/sendButtons/{instance_name}"
    headers = {"apikey": EVOLUTION_KEY, "Content-Type": "application/json"}
    
    formatted_buttons = []
    for idx, b_label in enumerate(buttons[:3]):
        formatted_buttons.append({
            "id": f"btn_{idx + 1}",
            "displayText": b_label
        })

    payload = {
        "number": phone,
        "title": "⚡ Quick Options",
        "description": body_text,
        "footer": "Powered by AI Operations Engine",
        "buttons": formatted_buttons
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=5)
        if res.status_code not in [200, 201]:
            send_whatsapp_message(instance_name, phone, f"{body_text}\n\n" + "\n".join([f"• {b}" for b in buttons]))
    except Exception as e:
        print(f"❌ Error sending buttons, falling back: {e}")
        send_whatsapp_message(instance_name, phone, f"{body_text}\n\n" + "\n".join([f"• {b}" for b in buttons]))

def broadcast_whatsapp_message(instance_name: str, phones: list, text: str) -> int:
    """Dispatches a WhatsApp broadcast to a list of customer phone numbers."""
    successful = 0
    for phone in phones:
        try:
            send_whatsapp_message(instance_name, phone, text)
            successful += 1
        except Exception as e:
            print(f"❌ Broadcast failed for {phone}: {e}")
    return successful