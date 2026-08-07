import os
import json
from fastapi import FastAPI, Request
from cachetools import TTLCache
from database import (
    get_tenant_by_instance, is_tenant_bot_muted, mute_tenant_bot, 
    add_tenant_entity, update_customer_ledger, get_tenant_customer_phones, 
    register_tenant_customer
)
from character_engine import generate_live_character_reply
from evolution_interactive import (
    send_whatsapp_presence, send_whatsapp_message, broadcast_whatsapp_message
)
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Enterprise Multi-Tenant AI Commerce SaaS Core")

# High-Performance Caching (Prevents database hammering)
tenant_cache = TTLCache(maxsize=500, ttl=60)
chat_memory = {}

@app.get("/")
@app.head("/")
async def root():
    return {"status": "online", "system": "Universal Operations Engine v2.0"}

@app.post("/webhook/whatsapp/{instance_name}")
async def handle_whatsapp_webhook(instance_name: str, request: Request):
    try:
        payload = await request.json()
    except Exception:
        return {"status": "invalid_json"}

    # 1. Fetch Tenant Profile
    tenant = tenant_cache.get(instance_name)
    if not tenant:
        tenant = get_tenant_by_instance(instance_name)
        if not tenant:
            return {"status": "unregistered_instance"}
        tenant_cache[instance_name] = tenant

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

    owner_phone = (tenant.get("owner_phone") or "").replace("+", "").strip()
    clean_sender = customer_phone.replace("+", "").strip()

    # -------------------------------------------------------------
    # 2. OWNER IN-CHAT ADMIN CONTROL FLOW (Universal)
    # -------------------------------------------------------------
    if is_from_me or (owner_phone and clean_sender == owner_phone):
        # A. Owner Add Entity Command: #add Name | Price | Description | {"key":"value"}
        if message_text.startswith("#add "):
            try:
                raw_cmd = message_text.replace("#add ", "").strip()
                parts = [p.strip() for p in raw_cmd.split("|")]
                p_name = parts[0]
                p_price = float(parts[1])
                p_desc = parts[2] if len(parts) > 2 else "Available now"
                
                # Safely parse JSONB metadata if provided
                p_meta = {}
                if len(parts) > 3:
                    try:
                        p_meta = json.loads(parts[3])
                    except json.JSONDecodeError:
                        send_whatsapp_message(instance_name, customer_phone, "⚠️ Warning: Invalid JSON metadata. Adding item without metadata.")
                
                if add_tenant_entity(tenant["id"], p_name, p_price, p_desc, p_meta):
                    reply = f"✅ *Entity Added Successfully!*\n\n📦 *Name:* {p_name}\n💰 *Price:* ₦{p_price:,.2f}\n📝 *Info:* {p_desc}\n⚙️ *Meta:* {p_meta}"
                else:
                    reply = "❌ Failed to add entity. Check database connection."
            except Exception as e:
                reply = f"❌ *Format Error!* Use format:\n`#add Name | Price | Description | {{\"meta\":\"data\"}}`\nExample:\n`#add 30k mAh Power Bank | 25000 | Fast charging | {{\"stock\":20}}`"
            
            send_whatsapp_message(instance_name, customer_phone, reply)
            return {"status": "owner_admin_command_processed"}

        # B. Owner Broadcast Command: #broadcast Your message text here
        elif message_text.startswith("#broadcast "):
            broadcast_text = message_text.replace("#broadcast ", "").strip()
            phone_list = get_tenant_customer_phones(tenant["id"])
            
            if not phone_list:
                send_whatsapp_message(instance_name, customer_phone, "⚠️ No registered customer contacts found for broadcast.")
                return {"status": "broadcast_empty"}
            
            count = broadcast_whatsapp_message(instance_name, phone_list, f"📢 *[Announcement from {tenant['business_name']}]*\n\n{broadcast_text}")
            send_whatsapp_message(instance_name, customer_phone, f"🚀 *Broadcast Sent Successfully!*\n\nDelivered to *{count}* customer(s).")
            return {"status": "owner_broadcast_sent"}

        # C. Regular owner reply to customer -> Mute bot for 120 mins for manual takeover
        else:
            mute_tenant_bot(tenant["id"], customer_phone, minutes=120)
            return {"status": "owner_takeover_muted"}

    # -------------------------------------------------------------
    # 3. CUSTOMER INBOUND PIPELINE
    # -------------------------------------------------------------
    
    if is_tenant_bot_muted(tenant["id"], customer_phone):
        return {"status": "bot_muted"}

    send_whatsapp_presence(instance_name, customer_phone, "composing")
    register_tenant_customer(tenant["id"], customer_phone)

    session_key = f"{tenant['id']}_{customer_phone}"
    if session_key not in chat_memory:
        chat_memory[session_key] = []
    
    history_str = "\n".join(chat_memory[session_key])

    chat_memory[session_key].append(f"Customer: {message_text}")
    if len(chat_memory[session_key]) > 10:
        chat_memory[session_key] = chat_memory[session_key][-10:]

    ai_res = generate_live_character_reply(
        tenant=tenant,
        customer_phone=customer_phone,
        latest_query=message_text,
        conversation_history=history_str,
        is_owner=False
    )
    
    reply_payload = ai_res["reply"]
    chat_memory[session_key].append(f"AI: {reply_payload}")

    if ai_res["is_human_transfer"]:
        mute_tenant_bot(tenant["id"], customer_phone, minutes=120)

    send_whatsapp_message(instance_name, customer_phone, reply_payload)
    return {"status": "success", "tenant": tenant["business_name"]}