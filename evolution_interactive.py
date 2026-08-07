import os
import requests

EVOLUTION_URL = os.environ.get("EVOLUTION_API_URL", "").rstrip("/")
EVOLUTION_KEY = os.environ.get("EVOLUTION_API_KEY", "")

def send_whatsapp_presence(instance_name: str, phone: str, state: str = "composing"):
    """Triggers 'typing...' indicator on WhatsApp."""
    url = f"{EVOLUTION_URL}/chat/sendPresence/{instance_name}"
    headers = {"apikey": EVOLUTION_KEY, "Content-Type": "application/json"}
    try:
        requests.post(url, json={"number": phone, "delay": 1200, "presence": state}, headers=headers, timeout=5)
    except Exception as e:
        print(f"⚠️ Presence signal skipped: {e}")

def send_whatsapp_message(instance_name: str, phone: str, text: str, buttons: list = None):
    """Sends outbound text message with optional interactive quick action buttons via Evolution API."""
    headers = {"apikey": EVOLUTION_KEY, "Content-Type": "application/json"}
    
    # If buttons are provided, send interactive button payload
    if buttons and len(buttons) > 0:
        url = f"{EVOLUTION_URL}/message/sendButtons/{instance_name}"
        formatted_buttons = []
        for idx, btn_text in enumerate(buttons[:3]):  # WhatsApp allows max 3 quick action buttons
            formatted_buttons.append({
                "type": "reply",
                "displayText": btn_text,
                "id": f"btn_{idx+1}"
            })
            
        payload = {
            "number": phone,
            "title": "Quick Action Options",
            "description": text,
            "footer": "Tap a button below for instant selection",
            "buttons": formatted_buttons
        }
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            if res.status_code in [200, 201]:
                return True
        except Exception as e:
            print(f"⚠️ Interactive button failed, falling back to standard text: {e}")

    # Fallback to standard text message if buttons are unavailable
    url = f"{EVOLUTION_URL}/message/sendText/{instance_name}"
    try:
        requests.post(url, json={"number": phone, "text": text}, headers=headers, timeout=10)
        return True
    except Exception as e:
        print(f"❌ Error sending text message: {e}")
        return False

def broadcast_whatsapp_message(instance_name: str, phone_list: list, text: str) -> int:
    """Dispatches announcement broadcast across registered contacts."""
    successful = 0
    for phone in phone_list:
        if send_whatsapp_message(instance_name, phone, text):
            successful += 1
    return successful