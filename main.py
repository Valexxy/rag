import os
from fastapi import FastAPI, Request
from cachetools import TTLCache
from database import (
    get_tenant_by_instance, is_tenant_bot_muted, mute_tenant_bot, 
    add_tenant_product, update_customer_ledger, get_tenant_customer_phones, 
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
async def root():
    return {"status": "online", "system": "Enterprise Multi-Tenant AI Operations Engine"}

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

    owner_phone = tenant.get("owner_phone", "").replace("+", "").strip()
    clean_sender = customer_phone.replace("+", "").strip()

    # -------------------------------------------------------------
    # 2. OWNER IN-CHAT ADMIN CONTROL FLOW
    # -------------------------------------------------------------
    if is_from_me or clean_sender == owner_phone:
        # A. Owner Add Product Command: #add Name | Price | Description | Stock
        if message_text.startswith("#add "):
            try:
                raw_cmd = message_text.replace("#add ", "").strip()
                parts = [p.strip() for p in raw_cmd.split("|")]
                p_name = parts[0]
                p_price = float(parts[1])
                p_desc = parts[2] if len(parts) > 2 else "Available in store"
                p_stock = int(parts[3]) if len(parts) > 3 else 100
                
                if add_tenant_product(tenant["id"], p_name, p_price, p_desc, p_stock):
                    reply = f"✅ *Product Added Successfully!*\n\n📦 *Item:* {p_name}\n💰 *Price:* ₦{p_price:,.2f}\n📝 *Info:* {p_desc}\n📊 *Stock:* {p_stock} units"
                else:
                    reply = "❌ Failed to add product. Check database connection."
            except Exception as e:
                reply = f"❌ *Format Error!* Use format:\n`#add Product Name | Price | Description | Stock`\nExample:\n`#add 20k mAh Power Bank | 19000 | Fast charging | 20`"
            
            send_whatsapp_message(instance_name, customer_phone, reply)
            return {"status": "owner_admin_command_processed"}

        # B. Owner Update Customer Ledger Command: #ledger Phone | LedgerType | Key=Value, Key2=Value2
        elif message_text.startswith("#ledger "):
            try:
                raw_cmd = message_text.replace("#ledger ", "").strip()
                parts = [p.strip() for p in raw_cmd.split("|")]
                target_phone = parts[0]
                l_type = parts[1]
                
                kv_pairs = parts[2].split(",")
                data_dict = {}
                for kv in kv_pairs:
                    k, v = kv.split("=")
                    data_dict[k.strip()] = v.strip()

                if update_customer_ledger(tenant["id"], target_phone, l_type, data_dict):
                    reply = f"✅ *Ledger Updated for {target_phone}!*\n\n📋 *Type:* {l_type}\n📊 *Data:* {data_dict}"
                else:
                    reply = "❌ Failed to update ledger record."
            except Exception as e:
                reply = "❌ *Format Error!* Use:\n`#ledger CustomerPhone | LedgerType | Key=Value, Key=Value`\nExample:\n`#ledger 2348012345678 | SAVINGS_SCHEME | contributed=₦250,000, target=₦600,000`"

            send_whatsapp_message(instance_name, customer_phone, reply)
            return {"status": "owner_admin_command_processed"}

        # C. Owner Broadcast Command: #broadcast Your message text here
        elif message_text.startswith("#broadcast "):
            broadcast_text = message_text.replace("#broadcast ", "").strip()
            phone_list = get_tenant_customer_phones(tenant["id"])
            
            if not phone_list:
                send_whatsapp_message(instance_name, customer_phone, "⚠️ No registered customer contacts found for broadcast.")
                return {"status": "broadcast_empty"}
            
            count = broadcast_whatsapp_message(instance_name, phone_list, f"📢 *[Announcement from {tenant['business_name']}]*\n\n{broadcast_text}")
            send_whatsapp_message(instance_name, customer_phone, f"🚀 *Broadcast Sent Successfully!*\n\nDelivered to *{count}* customer(s).")
            return {"status": "owner_broadcast_sent"}

        # D. Regular owner reply to customer -> Mute bot for 60 mins for manual takeover
        else:
            mute_tenant_bot(tenant["id"], customer_phone, minutes=60)
            return {"status": "owner_takeover_muted"}

    # -------------------------------------------------------------
    # 3. CUSTOMER INBOUND AI FLOW
    # -------------------------------------------------------------
    
    # Check if bot is muted for this customer
    if is_tenant_bot_muted(tenant["id"], customer_phone):
        return {"status": "bot_muted"}

    # Trigger 'typing...' status on WhatsApp immediately
    send_whatsapp_presence(instance_name, customer_phone, "composing")

    # Register contact for future broadcasts
    register_tenant_customer(tenant["id"], customer_phone)

    # Manage sliding conversation memory (Last 10 turns)
    session_key = f"{tenant['id']}_{customer_phone}"
    if session_key not in chat_memory:
        chat_memory[session_key] = []
    
    # Extract prior history before appending the new message
    history_str = "\n".join(chat_memory[session_key])

    # Append current turn to memory buffer
    chat_memory[session_key].append(f"Customer: {message_text}")
    if len(chat_memory[session_key]) > 10:
        chat_memory[session_key] = chat_memory[session_key][-10:]

    # Generate clean Groq AI reply using correct parameter mapping
    ai_res = generate_live_character_reply(
        tenant=tenant,
        customer_phone=customer_phone,
        latest_query=message_text,
        conversation_history=history_str,
        is_owner=False
    )
    
    reply_payload = ai_res["reply"]
    
    # Save AI response into session memory
    chat_memory[session_key].append(f"AI: {reply_payload}")

    # Mute bot if customer requests human transfer
    if ai_res["is_human_transfer"]:
        mute_tenant_bot(tenant["id"], customer_phone, minutes=120)

    # Dispatch response back via Evolution API
    send_whatsapp_message(instance_name, customer_phone, reply_payload)
    return {"status": "success", "tenant": tenant["business_name"]}