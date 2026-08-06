import os
import requests

EVOLUTION_URL = os.environ.get("EVOLUTION_API_URL", "").rstrip("/")
EVOLUTION_KEY = os.environ.get("EVOLUTION_API_KEY", "")

def send_whatsapp_interactive_buttons(instance_name: str, phone: str, body_text: str, buttons: list):
    """Sends native interactive buttons to WhatsApp via Evolution API.
    
    Example buttons list: ["💳 Pay Now", "👤 Human Agent", "📜 Catalog"]
    """
    url = f"{EVOLUTION_URL}/message/sendButtons/{instance_name}"
    headers = {
        "apikey": EVOLUTION_KEY,
        "Content-Type": "application/json"
    }
    
    formatted_buttons = []
    for idx, b_label in enumerate(buttons[:3]):  # WhatsApp supports max 3 quick reply buttons
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
            # Fallback to standard text if button API is unsupported on instance type
            send_fallback_text(instance_name, phone, f"{body_text}\n\n" + "\n".join([f"• {b}" for b in buttons]))
    except Exception as e:
        print(f"❌ Error sending interactive buttons: {e}")

def send_fallback_text(instance_name: str, phone: str, text: str):
    url = f"{EVOLUTION_URL}/message/sendText/{instance_name}"
    headers = {"apikey": EVOLUTION_KEY, "Content-Type": "application/json"}
    requests.post(url, json={"number": phone, "text": text}, headers=headers)