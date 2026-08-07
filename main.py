import os
import asyncio
import requests
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from cachetools import TTLCache
from database import (
    get_tenant_by_instance, 
    is_tenant_bot_muted, 
    mute_tenant_bot, 
    add_tenant_product, 
    update_customer_ledger, 
    register_tenant_customer, 
    get_tenant_customer_phones,
    create_tenant_reminder,
    get_due_reminders,
    update_reminder_next_run,
    save_chat_message,
    get_persistent_chat_history
)
from character_engine import generate_live_character_reply
from evolution_interactive import (
    send_whatsapp_presence, 
    send_whatsapp_message, 
    broadcast_whatsapp_message
)
from dotenv import load_dotenv

load_dotenv()

RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://rag-403h.onrender.com").rstrip("/")

async def keep_alive_and_scheduler():
    """Background task: Self-pings Render and dispatches due reminders every 60s."""
    await asyncio.sleep(10)
    counter = 0
    while True:
        try:
            due_list = await asyncio.to_thread(get_due_reminders)
            for r in due_list:
                tenant_info = r.get("tenants", {})
                instance = tenant_info.get("instance_name")
                biz_name = tenant_info.get("business_name", "Our Service")
                owner_phone = tenant_info.get("owner_phone")
                recipient = r["recipient_phone"]
                msg_body = f"⏰ *[Reminder from {biz_name}]*\n\n{r['reminder_text']}"

                if recipient == "OWNER" and owner_phone:
                    send_whatsapp_message(instance, owner_phone, msg_body, buttons=["📊 Daily Audit", "⏰ New Reminder", "📦 View Catalog"])
                elif recipient == "ALL":
                    phones = get_tenant_customer_phones(r["tenant_id"])
                    broadcast_whatsapp_message(instance, phones, msg_body)
                else:
                    send_whatsapp_message(instance, recipient, msg_body, buttons=["📜 View Catalog", "💳 Pay Now", "👤 Support"])

                update_reminder_next_run(r["id"], r["frequency"], r["next_run_at"])

            counter += 60
            if counter >= 600:
                await asyncio.to_thread(requests.get, f"{RENDER_URL}/", timeout=5)
                print("⚡ Keep-alive self-ping sent.")
                counter = 0

        except Exception as e:
            print(f"⚠️ Scheduler error: {e}")

        await asyncio.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(keep_alive_and_scheduler())
    yield

app = FastAPI(title="World-Class AI Executive & Commerce OS Core", lifespan=lifespan)

tenant_cache = TTLCache(maxsize=500, ttl=60)
chat_memory_cache = TTLCache(maxsize=1000, ttl=300)

@app.get("/")
@app.head("/")
async def root():
    return {"status": "online", "system": "World-First Dual Engine AI Commerce OS"}

@app.post("/webhook/whatsapp/store-bot")
@app.post("/webhook/whatsapp/{instance_name}")
async def handle_optimized_whatsapp(request: Request, instance_name: str = "store-bot"):
    try:
        payload = await request.json()
    except Exception:
        return {"status": "invalid_json"}

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
    customer_phone = remote_jid.split("@")[0]

    message_text = (
        message_info.get("conversation")
        or message_info.get("extendedTextMessage", {}).get("text")
        or message_info.get("buttonsResponseMessage", {}).get("selectedDisplayText")
        or ""
    ).strip()

    if not customer_phone or not message_text:
        return {"status": "ignored"}

    owner_phone = (tenant.get("owner_phone") or "").replace("+", "").strip()
    clean_sender = customer_phone.replace("+", "").strip()
    is_owner = bool(is_from_me or (owner_phone and clean_sender == owner_phone))

    # -------------------------------------------------------------
    # 1. IN-CHAT ADMIN COMMAND INTERCEPTOR
    # -------------------------------------------------------------
    if is_owner:
        if message_text.startswith("#add "):
            try:
                parts = [p.strip() for p in message_text.replace("#add ", "").split("|")]
                p_name, p_price = parts[0], float(parts[1])
                p_desc = parts[2] if len(parts) > 2 else "Available in store"
                p_stock = int(parts[3]) if len(parts) > 3 else 100
                
                if add_tenant_product(tenant["id"], p_name, p_price, p_desc, p_stock):
                    reply = f"✅ *Product Successfully Added!*\n\n📦 *Item:* {p_name}\n💰 *Price:* ₦{p_price:,.2f}\n📊 *Stock:* {p_stock} units"
                else:
                    reply = "❌ Database error."
            except Exception:
                reply = "❌ *Format Error!* Use:\n`#add Product Name | Price | Description | Stock`"
            
            send_whatsapp_message(instance_name, customer_phone, reply, buttons=["📦 Stock Check", "⏰ Set Reminder", "📊 Daily Audit"])
            return {"status": "owner_command_processed"}

        elif message_text.startswith("#remind "):
            try:
                parts = [p.strip() for p in message_text.replace("#remind ", "").split("|")]
                target_recipient, freq, time_str, reminder_msg = parts[0], parts[1].upper(), parts[2], parts[3]
                first_run_dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
                
                if create_tenant_reminder(tenant["id"], target_recipient, reminder_msg, freq, first_run_dt.isoformat()):
                    reply = f"⏰ *Reminder Scheduled!*\n\n👤 *Target:* {target_recipient}\n🔄 *Frequency:* {freq}\n📅 *Time:* {time_str} UTC"
                else:
                    reply = "❌ Reminder creation failed."
            except Exception:
                reply = "❌ *Format Error!* Use:\n`#remind Phone/ALL/OWNER | ONCE/DAILY/WEEKLY/MONTHLY | YYYY-MM-DD HH:MM | Message`"

            send_whatsapp_message(instance_name, customer_phone, reply, buttons=["⏰ New Reminder", "📊 Daily Audit", "📦 View Stock"])
            return {"status": "owner_command_processed"}

        elif message_text.startswith("#broadcast "):
            broadcast_text = message_text.replace("#broadcast ", "").strip()
            phone_list = get_tenant_customer_phones(tenant["id"])
            if not phone_list:
                send_whatsapp_message(instance_name, customer_phone, "⚠️ No registered contacts found to broadcast.")
                return {"status": "broadcast_empty"}
            
            count = broadcast_whatsapp_message(instance_name, phone_list, f"📢 *[Announcement from {tenant['business_name']}]*\n\n{broadcast_text}")
            send_whatsapp_message(instance_name, customer_phone, f"🚀 *Broadcast Sent to {count} customer(s)!*")
            return {"status": "owner_broadcast_sent"}

    # -------------------------------------------------------------
    # 2. AI RESPONSE GENERATION & PERSISTENT MEMORY
    # -------------------------------------------------------------
    if not is_owner and is_tenant_bot_muted(tenant["id"], customer_phone):
        return {"status": "bot_muted"}

    send_whatsapp_presence(instance_name, customer_phone, "composing")
    register_tenant_customer(tenant["id"], customer_phone)
    save_chat_message(tenant["id"], customer_phone, role="customer", message=message_text)

    session_key = f"{tenant['id']}_{customer_phone}"
    if session_key not in chat_memory_cache:
        chat_memory_cache[session_key] = get_persistent_chat_history(tenant["id"], customer_phone, limit=10)
    else:
        chat_memory_cache[session_key].append(f"Customer: {message_text}")
        if len(chat_memory_cache[session_key]) > 10:
            chat_memory_cache[session_key] = chat_memory_cache[session_key][-10:]

    context_history = "\n".join(chat_memory_cache[session_key])

    ai_res = generate_live_character_reply(
        tenant=tenant, 
        customer_phone=customer_phone, 
        latest_query=message_text,
        conversation_history=context_history, 
        is_owner=is_owner
    )
    reply_payload = ai_res["reply"]
    buttons = ai_res["buttons"]

    save_chat_message(tenant["id"], customer_phone, role="assistant", message=reply_payload)
    chat_memory_cache[session_key].append(f"AI: {reply_payload}")

    if not is_owner and ai_res["is_human_transfer"]:
        mute_tenant_bot(tenant["id"], customer_phone, minutes=120)

    send_whatsapp_message(instance_name, customer_phone, reply_payload, buttons=buttons)
    return {"status": "success", "tenant": tenant["business_name"]}