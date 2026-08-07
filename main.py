import os
import logging
from typing import Optional, Dict, Any
import httpx
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client

# Initialize Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("whatsapp_bot")

# Environment Variables
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY", "")
EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL", "")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY", "")

# Initialize Supabase Client
supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")

app = FastAPI(title="WhatsApp Store Bot RAG API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.head("/")
async def root():
    return {"status": "live", "message": "WhatsApp Bot RAG Service is Running"}

async def send_whatsapp_message(instance_name: str, number: str, text: str):
    """Sends reply back via Evolution API with extended timeout."""
    if not EVOLUTION_API_URL:
        logger.error("EVOLUTION_API_URL is not set in environment variables.")
        return

    url = f"{EVOLUTION_API_URL.rstrip('/')}/message/sendText/{instance_name}"
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "number": number,
        "options": {
            "delay": 1200,
            "presence": "composing",
            "linkPreview": True
        },
        "text": text
    }

    # Increased timeout from 2s to 10s to prevent Render connection timeouts
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"Message sent successfully to {number}")
        except Exception as e:
            logger.error(f"Error sending WhatsApp message via Evolution API: {e}")

async def process_and_respond(
    customer_phone: str,
    message_text: str,
    tenant: Dict[str, Any],
    instance_name: str
):
    """Background task to process customer message and generate bot reply."""
    try:
        tenant_id = tenant.get("id")
        
        # Safely fetch chat history
        chat_history = []
        if supabase and tenant_id:
            try:
                res = supabase.table("tenant_chat_history") \
                    .select("*") \
                    .eq("tenant_id", tenant_id) \
                    .eq("customer_phone", customer_phone) \
                    .order("created_at", desc=True) \
                    .limit(5) \
                    .execute()
                chat_history = res.data or []
            except Exception as db_err:
                logger.error(f"Error fetching chat history: {db_err}")

        # Safely extract owner_phone (Guards against None / NULL)
        owner_phone = (tenant.get("owner_phone") or "").replace("+", "").strip()
        clean_sender = customer_phone.replace("+", "").strip()

        # Check if sender is owner or customer
        is_owner = bool(owner_phone and clean_sender == owner_phone)

        # Bot response generation logic
        business_name = tenant.get("business_name") or "Valexxy Global Store"
        reply_text = f"Good day! Welcome to {business_name}. How can we assist you today?"

        # Safely log chat history
        if supabase and tenant_id:
            try:
                supabase.table("tenant_chat_history").insert({
                    "tenant_id": tenant_id,
                    "customer_phone": customer_phone,
                    "role": "user",
                    "message": message_text
                }).execute()

                supabase.table("tenant_chat_history").insert({
                    "tenant_id": tenant_id,
                    "customer_phone": customer_phone,
                    "role": "assistant",
                    "message": reply_text
                }).execute()
            except Exception as save_err:
                logger.error(f"Error saving chat history: {save_err}")

        # Send response back to customer
        await send_whatsapp_message(instance_name, customer_phone, reply_text)

    except Exception as err:
        logger.error(f"Error processing response: {err}")

@app.post("/webhook/whatsapp/store-bot")
async def handle_optimized_whatsapp(request: Request, background_tasks: BackgroundTasks):
    try:
        payload = await request.json()
        
        data = payload.get("data", {})
        event = payload.get("event")
        instance_name = payload.get("instance", "default")

        # Ignore events that are not new incoming messages
        if event and event != "messages.upsert":
            return {"status": "ignored_event"}

        key = data.get("key", {})
        from_me = key.get("fromMe", False)
        if from_me:
            return {"status": "ignored_from_me"}

        remote_jid = key.get("remoteJid", "")
        if not remote_jid or "@g.us" in remote_jid:  # Ignore empty or group messages
            return {"status": "ignored_group"}

        customer_phone = remote_jid.split("@")[0]
        message = data.get("message", {})
        
        message_text = (
            message.get("conversation") or
            message.get("extendedTextMessage", {}).get("text") or
            ""
        ).strip()

        if not message_text:
            return {"status": "empty_message"}

        # Fetch Tenant Safely
        tenant = {}
        if supabase:
            try:
                res = supabase.table("tenants").select("*").limit(1).execute()
                if res.data and len(res.data) > 0:
                    tenant = res.data[0]
            except Exception as tenant_err:
                logger.error(f"Error fetching tenant: {tenant_err}")

        # SAFE EXTRACTION (Line 122 Fix)
        # Prevents AttributeError: 'NoneType' object has no attribute 'replace'
        owner_phone = (tenant.get("owner_phone") or "").replace("+", "").strip()

        # Add background processing task so WhatsApp webhook gets an instant 200 OK
        background_tasks.add_task(
            process_and_respond,
            customer_phone=customer_phone,
            message_text=message_text,
            tenant=tenant,
            instance_name=instance_name
        )

        return {"status": "processing"}

    except Exception as e:
        logger.error(f"Error handling WhatsApp webhook: {e}")
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)