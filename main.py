import os
import requests
from fastapi import FastAPI, Request
from database import get_tenant_by_instance, is_tenant_bot_muted, mute_tenant_bot, supabase
from ai_engine import process_multitenant_message
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Multi-Tenant Commerce AI SaaS Platform")

EVOLUTION_URL = os.environ.get("EVOLUTION_API_URL", "").rstrip("/")
EVOLUTION_KEY = os.environ.get("EVOLUTION_API_KEY", "")

@app.get("/")
async def root():
    return {"status": "online", "platform": "Enterprise Multi-Tenant AI Engine"}

@app.post("/webhook/whatsapp/{instance_name}")
async def handle_multitenant_whatsapp(instance_name: str, request: Request):
    try:
        payload = await request.json()
    except Exception:
        return {"status": "invalid_json"}

    # 1. Fetch Tenant Context
    tenant = get_tenant_by_instance(instance_name)
    if not tenant:
        return {"status": "unregistered_tenant_instance"}

    data = payload.get("data", {})
    key_info = data.get("key", {})
    message_info = data.get("message", {})

    is_from_me = key_info.get("fromMe", False)
    remote_jid = key_info.get("remoteJid", "")
    customer_phone = remote_jid.replace("@s.whatsapp.net", "")

    message_text = (
        message_info.get("conversation")
        or message_info.get("extendedTextMessage", {}).get("text", "")
        or message_info.get("imageMessage", {}).get("caption", "")
    )

    if not customer_phone or not message_text:
        return {"status": "ignored"}

    # 2. Native Owner Mute/Takeover
    if is_from_me:
        mute_tenant_bot(tenant["id"], customer_phone, minutes=60)
        return {"status": "owner_takeover_bot_muted"}

    # 3. Check Mute Status
    if is_tenant_bot_muted(tenant["id"], customer_phone):
        return {"status": "tenant_bot_muted"}

    # 4. Process Multi-Tenant Response
    ai_result = process_multitenant_message(tenant, customer_phone, message_text)
    
    # 5. Log transaction draft if payment link created
    if ai_result["payment_ref"]:
        supabase.table("tenant_transactions").insert({
            "tenant_id": tenant["id"],
            "customer_phone": customer_phone,
            "payment_reference": ai_result["payment_ref"],
            "amount": ai_result["amount"],
            "status": "PENDING"
        }).execute()

    # 6. Send Response back via instance
    send_whatsapp_message(instance_name, customer_phone, ai_result["reply"])
    return {"status": "success", "tenant": tenant["business_name"]}


@app.post("/webhook/monnify")
async def handle_monnify_global_webhook(request: Request):
    """Processes global Monnify payment notifications across all tenants."""
    try:
        payload = await request.json()
        event_type = payload.get("eventType")
        event_data = payload.get("eventData", {})

        if event_type == "SUCCESSFUL_TRANSACTION":
            payment_ref = event_data.get("paymentReference")
            amount_paid = event_data.get("amountPaid")
            
            # Fetch transaction & tenant info
            tx_res = supabase.table("tenant_transactions").select("*, tenants(*)").eq("payment_reference", payment_ref).execute()
            
            if tx_res.data:
                tx = tx_res.data[0]
                tenant = tx["tenants"]
                
                # Update status
                supabase.table("tenant_transactions").update({"status": "PAID"}).eq("payment_reference", payment_ref).execute()
                
                # Send confirmation via tenant's instance
                send_whatsapp_message(
                    tenant["instance_name"],
                    tx["customer_phone"],
                    f"✅ *Payment Receipt - {tenant['business_name']}*\n\nPayment of *₦{amount_paid:,.2f}* confirmed! Your reference is `{payment_ref}`. Thank you for your business!"
                )

        return {"status": "success"}
    except Exception as e:
        print(f"❌ Webhook Error: {e}")
        return {"status": "error", "message": str(e)}


def send_whatsapp_message(instance_name: str, phone: str, text: str):
    """Sends outbound WhatsApp message using tenant instance."""
    url = f"{EVOLUTION_URL}/message/sendText/{instance_name}"
    headers = {"apikey": EVOLUTION_KEY, "Content-Type": "application/json"}
    payload = {"number": phone, "text": text}
    try:
        requests.post(url, json=payload, headers=headers, timeout=5)
    except Exception as e:
        print(f"❌ Error sending outbound message: {e}")