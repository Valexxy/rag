import os
import requests
from fastapi import FastAPI, Request
from database import is_bot_muted, mute_bot_for_owner
from ai_engine import classify_intent, generate_reply
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="WhatsApp AI SaaS")

# Environment variables
EVOLUTION_URL = os.environ.get("EVOLUTION_API_URL", "").rstrip("/")
EVOLUTION_KEY = os.environ.get("EVOLUTION_API_KEY", "")
INSTANCE_NAME = os.environ.get("INSTANCE_NAME", "store-bot")

@app.get("/")
async def root():
    """Health check endpoint for Render."""
    return {"status": "online", "system": "WhatsApp AI Engine"}

@app.post("/webhook/whatsapp")
@app.post("/webhook/whatsapp/{full_path:path}")
async def handle_whatsapp(request: Request):
    try:
        payload = await request.json()
    except Exception:
        return {"status": "invalid_json"}
    
    # Extract nested data from the Evolution API payload
    data = payload.get("data", {})
    key_info = data.get("key", {})
    message_info = data.get("message", {})
    
    is_from_me = key_info.get("fromMe", False)
    remote_jid = key_info.get("remoteJid", "")
    customer_phone = remote_jid.replace("@s.whatsapp.net", "")
    
    # Extract text from standard, extended, or image caption messages
    message_text = (
        message_info.get("conversation") 
        or message_info.get("extendedTextMessage", {}).get("text", "")
        or message_info.get("imageMessage", {}).get("caption", "")
    )

    if not customer_phone or not message_text:
        return {"status": "ignored"}

    # NATIVE OWNER TAKEOVER (If you send a manual message from your business phone)
    if is_from_me:
        print(f"👤 Owner manually messaged {customer_phone}. Muting bot for 60 mins.")
        mute_bot_for_owner(customer_phone, minutes=60)
        return {"status": "owner_replied_muted_bot"}

    # CHECK LOCK STATUS
    if is_bot_muted(customer_phone):
        print(f"🔒 Bot is currently muted for {customer_phone}.")
        return {"status": "bot_is_muted"}

    # INTENT GUARD
    intent = classify_intent(message_text)
    print(f"📩 Incoming from {customer_phone}: '{message_text}' | Classified Intent: {intent}")

    if "PERSONAL" in intent:
        print(f"🙈 Personal chat detected from {customer_phone}. Ignored.")
        return {"status": "personal_message_ignored"}

    if "HANDOVER" in intent:
        print(f"🤝 Handover requested by {customer_phone}.")
        mute_bot_for_owner(customer_phone, minutes=60)
        send_whatsapp(customer_phone, "🤖 *[Notice]* Transferring you to the business owner now.")
        return {"status": "transferred_to_human"}

    # GENERATE & SEND REPLY
    bot_reply = generate_reply(message_text)
    print(f"🤖 Sending AI Reply to {customer_phone}: {bot_reply}")
    send_whatsapp(customer_phone, bot_reply)
    
    return {"status": "success"}


@app.post("/webhook/monnify")
async def handle_monnify_webhook(request: Request):
    """Processes incoming payment notifications from Monnify."""
    try:
        payload = await request.json()
        event_type = payload.get("eventType")
        event_data = payload.get("eventData", {})
        
        if event_type == "SUCCESSFUL_TRANSACTION":
            payment_ref = event_data.get("paymentReference")
            amount_paid = event_data.get("amountPaid")
            customer_email = event_data.get("customer", {}).get("email", "")
            
            print(f"💳 Monnify Payment Received! Ref: {payment_ref}, Amount: ₦{amount_paid:,.2f}")
            
            # Extract customer phone if email format is '2348000000000@customer.com'
            if "@customer.com" in customer_email:
                phone = customer_email.replace("@customer.com", "")
                send_whatsapp(
                    phone, 
                    f"✅ *Payment Confirmed!*\n\nWe received your payment of *₦{amount_paid:,.2f}*. Your order is now being processed. Thank you!"
                )
            
        return {"status": "success"}
    except Exception as e:
        print(f"❌ Error processing Monnify webhook: {e}")
        return {"status": "error", "message": str(e)}


def send_whatsapp(phone: str, text: str):
    """Sends the response back to the customer via Evolution API."""
    if not EVOLUTION_URL or not EVOLUTION_KEY:
        print("❌ EVOLUTION_API_URL or EVOLUTION_API_KEY environment variables are missing.")
        return
        
    url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {
        "apikey": EVOLUTION_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "number": phone,
        "text": text
    }
    
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code not in [200, 201]:
            print(f"❌ Outbound WhatsApp Failed! Code: {res.status_code}, Response: {res.text}")
    except Exception as e:
        print(f"❌ Exception in send_whatsapp: {e}")