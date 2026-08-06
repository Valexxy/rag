import os
import requests
from fastapi import FastAPI, Request
from database import is_bot_muted, mute_bot_for_owner
from ai_engine import classify_intent, generate_reply
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="WhatsApp AI SaaS")

EVOLUTION_URL = os.environ.get("EVOLUTION_API_URL")
EVOLUTION_KEY = os.environ.get("EVOLUTION_API_KEY")

# Change this line in main.py:
@app.post("/webhook/whatsapp")
@app.post("/webhook/whatsapp/{full_path:path}")
async def handle_whatsapp(request: Request):
    payload = await request.json()
    
    # Extract nested data from the Evolution API payload
    data = payload.get("data", {})
    key_info = data.get("key", {})
    message_info = data.get("message", {})
    
    is_from_me = key_info.get("fromMe", False)
    remote_jid = key_info.get("remoteJid", "")
    customer_phone = remote_jid.replace("@s.whatsapp.net", "")
    
    # Extract text from standard or extended messages
    message_text = message_info.get("conversation") or \
                   message_info.get("extendedTextMessage", {}).get("text", "")

    if not customer_phone or not message_text:
        return {"status": "ignored"}

    # NATIVE OWNER TAKEOVER
    if is_from_me:
        mute_bot_for_owner(customer_phone, minutes=60)
        return {"status": "owner_replied_muted_bot"}

    # CHECK LOCK STATUS
    if is_bot_muted(customer_phone):
        return {"status": "bot_is_muted"}

    # INTENT GUARD
    intent = classify_intent(message_text)

    if "PERSONAL" in intent:
        return {"status": "personal_message_ignored"}

    if "HANDOVER" in intent:
        mute_bot_for_owner(customer_phone, minutes=60)
        send_whatsapp(customer_phone, "🤖 *[Notice]* Transferring you to the business owner now.")
        return {"status": "transferred_to_human"}

    # GENERATE & SEND REPLY
    bot_reply = generate_reply(message_text)
    send_whatsapp(customer_phone, bot_reply)
    return {"status": "success"}

def send_whatsapp(phone: str, text: str):
    """Sends the response back to the customer via Evolution API."""
    url = f"{EVOLUTION_URL}/message/sendText/instance_default"
    headers = {
        "apikey": EVOLUTION_KEY,
        "Content-Type": "application/json"
    }
    requests.post(url, json={"number": phone, "text": text}, headers=headers)