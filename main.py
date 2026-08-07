import os
import asyncio
import requests
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from cachetools import TTLCache
from database import get_tenant_by_instance, is_tenant_bot_muted, mute_tenant_bot, supabase
from character_engine import generate_live_character_reply
from dotenv import load_dotenv

load_dotenv()

# App URL detection (Uses Render's environment variable or defaults to your app domain)
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://rag-403h.onrender.com").rstrip("/")

async def keep_alive():
    """Background task: Pings self every 10 minutes to prevent Render free tier spin-down."""
    await asyncio.sleep(10)  # Wait for server to finish booting
    while True:
        try:
            # Runs blocking requests in a thread pool to avoid blocking the FastAPI event loop
            await asyncio.to_thread(requests.get, f"{RENDER_URL}/", timeout=5)
            print("⚡ Keep-alive self-ping sent to maintain warm server status.")
        except Exception as e:
            print(f"⚠️ Keep-alive ping skipped: {e}")
        await asyncio.sleep(600)  # Repeat every 10 minutes (600 seconds)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background keep-alive task on server startup
    asyncio.create_task(keep_alive())
    yield

app = FastAPI(
    title="Enterprise Multi-Tenant AI Commerce SaaS Core",
    lifespan=lifespan
)

EVOLUTION_URL = os.environ.get("EVOLUTION_API_URL", "").rstrip("/")
EVOLUTION_KEY = os.environ.get("EVOLUTION_API_KEY", "")

# ⚡ High-Performance TTL Caching (Prevents database hammering - 60s expiration)
tenant_cache = TTLCache(maxsize=500, ttl=60)
chat_memory = {}  # Short-term sliding window memory per user session

@app.get("/")
async def root():
    return {"status": "online", "system": "Optimized Multi-Tenant AI Commerce Engine"}

@app.post("/webhook/whatsapp/{instance_name}")
async def handle_optimized_whatsapp(instance_name: str, request: Request):
    try:
        payload = await request.json()
    except Exception:
        return {"status": "invalid_json"}

    # 1. Fetch Tenant Profile with In-Memory Caching
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

    # 2. Owner Mute & Takeover Control (mutes bot for 60 mins if owner replies)
    if is_from_me:
        mute_tenant_bot(tenant["id"], customer_phone, minutes=60)
        return {"status": "owner_takeover_muted"}

    # 3. Check Bot Mute Status
    if is_tenant_bot_muted(tenant["id"], customer_phone):
        return {"status": "bot_muted"}

    # 4. Manage Short-Term Conversation Memory (Sliding window: last 10 messages / 5 turns)
    session_key = f"{tenant['id']}_{customer_phone}"
    if session_key not in chat_memory:
        chat_memory[session_key] = []
    
    chat_memory[session_key].append(f"Customer: {message_text}")
    if len(chat_memory[session_key]) > 10:
        chat_memory[session_key] = chat_memory[session_key][-10:]

    # 5. Generate Live Character Response with Context History
    context_history = "\n".join(chat_memory[session_key])
    ai_res = generate_live_character_reply(tenant, context_history, persona_key="street_smart")
    reply_payload = ai_res["reply"]
    
    # Save AI response into session memory history
    chat_memory[session_key].append(f"AI: {reply_payload}")

    # 6. Handle Action Tags (e.g., Human Transfer Mute)
    if ai_res["is_human_transfer"]:
        mute_tenant_bot(tenant["id"], customer_phone, minutes=120)

    # 7. Send Outbound Response via Evolution API
    send_whatsapp_message(instance_name, customer_phone, reply_payload)
    return {"status": "success", "tenant": tenant["business_name"]}

def send_whatsapp_message(instance_name: str, phone: str, text: str):
    """Sends outbound text message via Evolution API."""
    url = f"{EVOLUTION_URL}/message/sendText/{instance_name}"
    headers = {"apikey": EVOLUTION_KEY, "Content-Type": "application/json"}
    try:
        requests.post(url, json={"number": phone, "text": text}, headers=headers, timeout=5)
    except Exception as e:
        print(f"❌ Error sending outbound message: {e}")