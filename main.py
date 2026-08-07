import os
import json
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from cachetools import TTLCache
from dotenv import load_dotenv

from database import (
    get_tenant_by_instance, is_tenant_bot_muted, mute_tenant_bot, 
    add_tenant_entity, get_tenant_customer_phones, register_tenant_customer
)
from character_engine import generate_live_character_reply
from evolution_interactive import (
    send_whatsapp_presence, send_whatsapp_message, broadcast_whatsapp_message
)

# World-Class Enterprise Modules
from local_ai_brain import local_brain
from whatsapp_ui import render_executive_whatsapp_dashboard, render_role_based_menu, format_currency
from logistics_department import logistics_dept
from financial_trust_engine import financial_trust
from zero_hallucination_guard import zero_guard
from deal_closure_engine import deal_closure
from owner_alert_protocol import owner_alert
from reminder_scheduler import reminder_scheduler
from loyalty_rewards import loyalty_engine

# Sovereign Compliance & Security Fortress
from sovereign_compliance import sovereign_compliance
from security_fortress import security_fortress
from audit_vault import audit_vault

load_dotenv()

app = FastAPI(title="Sovereign AI Commerce & Financial SaaS Platform 2030")

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

tenant_cache = TTLCache(maxsize=500, ttl=60)
chat_memory = {}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(reminder_scheduler.start_background_loop())

@app.get("/")
@app.head("/")
async def root():
    return {"status": "online", "system": "Sovereign AI Commerce & Financial Platform v2030"}

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serves the Executive Web SaaS Dashboard."""
    if os.path.exists("static/dashboard.html"):
        return FileResponse("static/dashboard.html")
    return HTMLResponse("<h2>Dashboard Initializing...</h2>")

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
    is_owner = is_from_me or (owner_phone and clean_sender == owner_phone)

    # -------------------------------------------------------------
    # 🔐 PROMPT INJECTION & SECURITY DEFENSE SHIELD
    # -------------------------------------------------------------
    is_malicious, security_reply = security_fortress.inspect_prompt_injection(message_text)
    if is_malicious:
        audit_vault.create_audit_record(tenant["id"], customer_phone, "PROMPT_INJECTION_ATTEMPT", {"input": message_text})
        send_whatsapp_message(instance_name, customer_phone, security_reply)
        owner_alert.send_urgent_owner_alert(instance_name, owner_phone, customer_phone, "PROMPT INJECTION DEFENSE TRIGGERED", message_text)
        return {"status": "security_attack_blocked"}

    # -------------------------------------------------------------
    # 2. OWNER EXECUTIVE COMMANDS & DASHBOARD CONTROL
    # -------------------------------------------------------------
    if is_owner:
        cmd = message_text.strip().lower()

        # A. Executive Dashboard Command
        if cmd in ["#admin", "#dash", "#dashboard", "!menu", "#kpi"]:
            dashboard_text = render_executive_whatsapp_dashboard(tenant)
            send_whatsapp_message(instance_name, customer_phone, dashboard_text)
            return {"status": "owner_dashboard_sent"}

        # B. Owner Quick Add Entity
        elif message_text.startswith("#add "):
            try:
                raw_cmd = message_text.replace("#add ", "").strip()
                parts = [p.strip() for p in raw_cmd.split("|")]
                p_name = parts[0]
                p_price = float(parts[1])
                p_desc = parts[2] if len(parts) > 2 else "Available now"
                p_meta = json.loads(parts[3]) if len(parts) > 3 else {}

                if add_tenant_entity(tenant["id"], p_name, p_price, p_desc, p_meta):
                    audit_vault.create_audit_record(tenant["id"], "OWNER", "ADD_ENTITY", {"name": p_name, "price": p_price})
                    reply = f"✅ *[ITEM ADDED TO CATALOG]*\n\n📦 *Name:* {p_name}\n💰 *Price:* {format_currency(p_price, tenant.get('currency'))}\n📝 *Info:* {p_desc}"
                else:
                    reply = "❌ DB Error adding item."
            except Exception:
                reply = "❌ *Format Error!* Use:\n`#add Name | Price | Description`"

            send_whatsapp_message(instance_name, customer_phone, reply)
            return {"status": "owner_add_processed"}

        # C. Compliance Data Export & Erase Commands (#data-export, #data-erase)
        elif message_text.startswith("#data-export "):
            target_phone = message_text.replace("#data-export ", "").strip()
            export_data = sovereign_compliance.export_customer_data(tenant["id"], target_phone)
            audit_vault.create_audit_record(tenant["id"], "OWNER", "GDPR_DATA_EXPORT", {"target_phone": target_phone})
            reply = f"📄 *[GDPR/NDPA DATA EXPORT]*\n\n`{json.dumps(export_data, indent=2)[:1000]}`"
            send_whatsapp_message(instance_name, customer_phone, reply)
            return {"status": "data_exported"}

        elif message_text.startswith("#data-erase "):
            target_phone = message_text.replace("#data-erase ", "").strip()
            if sovereign_compliance.erase_customer_data(tenant["id"], target_phone):
                audit_vault.create_audit_record(tenant["id"], "OWNER", "GDPR_RIGHT_TO_BE_FORGOTTEN", {"target_phone": target_phone})
                reply = f"🗑️ *[GDPR RIGHT TO BE FORGOTTEN]*\n\nCustomer `{target_phone}` data successfully erased from server."
            else:
                reply = "❌ Data erasure failed."
            send_whatsapp_message(instance_name, customer_phone, reply)
            return {"status": "data_erased"}

        # D. Owner Broadcast Command
        elif message_text.startswith("#broadcast "):
            broadcast_text = message_text.replace("#broadcast ", "").strip()
            phone_list = get_tenant_customer_phones(tenant["id"])
            if phone_list:
                count = broadcast_whatsapp_message(instance_name, phone_list, f"📢 *[{tenant['business_name']}]*\n\n{broadcast_text}")
                audit_vault.create_audit_record(tenant["id"], "OWNER", "BROADCAST_SENT", {"recipient_count": count})
                reply = f"🚀 *Broadcast delivered to {count} customers!*"
            else:
                reply = "⚠️ No registered customers found for broadcast."

            send_whatsapp_message(instance_name, customer_phone, reply)
            return {"status": "broadcast_processed"}

        # E. Regular owner manual reply -> Auto-mute bot for 120 mins
        else:
            mute_tenant_bot(tenant["id"], customer_phone, minutes=120)
            return {"status": "owner_takeover_muted"}

    # -------------------------------------------------------------
    # 3. CUSTOMER INBOUND PIPELINE & LOCAL AI ROUTING
    # -------------------------------------------------------------
    if is_tenant_bot_muted(tenant["id"], customer_phone):
        return {"status": "bot_muted"}

    send_whatsapp_presence(instance_name, customer_phone, "composing")
    register_tenant_customer(tenant["id"], customer_phone)

    intent, confidence = local_brain.classify_intent(message_text)

    if message_text.strip() in ["menu", "1", "2", "3", "4", "5", "hi", "hello", "help"]:
        reply_payload = render_role_based_menu("CLIENT", tenant, customer_phone)
        send_whatsapp_message(instance_name, customer_phone, reply_payload)
        return {"status": "menu_sent"}

    if intent == "LOGISTICS":
        wb_sample = logistics_dept.generate_waybill(tenant["id"], customer_phone, "Customer Address", "Order Package")
        reply_payload = logistics_dept.format_delivery_status(wb_sample)
        send_whatsapp_message(instance_name, customer_phone, reply_payload)
        return {"status": "waybill_sent"}

    if intent == "PURCHASE":
        reply_payload = financial_trust.format_trust_verified_payment_instructions(tenant, 25000.0, f"TRX-{customer_phone[-4:]}")
        send_whatsapp_message(instance_name, customer_phone, reply_payload)
        return {"status": "payment_instructions_sent"}

    session_key = f"{tenant['id']}_{customer_phone}"
    history_str = "\n".join(chat_memory.get(session_key, []))

    ai_res = generate_live_character_reply(
        tenant=tenant,
        customer_phone=customer_phone,
        latest_query=message_text,
        conversation_history=history_str,
        is_owner=False
    )
    
    reply_payload = ai_res["reply"]

    is_valid, verified_payload = zero_guard.verify_response_facts(reply_payload, "")
    if not is_valid:
        mute_tenant_bot(tenant["id"], customer_phone, minutes=120)
        owner_alert.send_urgent_owner_alert(instance_name, owner_phone, customer_phone, "Unverified inquiry - Manager Handoff", message_text)

    if ai_res.get("is_human_transfer"):
        mute_tenant_bot(tenant["id"], customer_phone, minutes=120)
        owner_alert.send_urgent_owner_alert(instance_name, owner_phone, customer_phone, "Customer requested Human Agent", message_text)

    send_whatsapp_message(instance_name, customer_phone, reply_payload)
    return {"status": "success", "tenant": tenant["business_name"]}