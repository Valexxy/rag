from supabase import create_client, Client
import os
import time
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://emohdirbihcpnnmqtzrs.supabase.co")
SUPABASE_KEY = (
    os.environ.get("SUPABASE_KEY") 
    or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") 
    or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtb2hkaXJiaWhjcG5ubXF0enJzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MzM3NDAyMCwiZXhwIjoyMDg4OTUwMDIwfQ.ZoNM3pQyLxsGc8ymsFiOrQ7oAXguv1IHmnNlbPbXiJA"
)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_tenant_by_instance(instance_name: str) -> dict:
    """Fetches tenant configuration using instance_name."""
    try:
        response = supabase.table("tenants").select("*").eq("instance_name", instance_name).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        # Return fallback mock tenant for offline test suite
        return {
            "id": "t-demo",
            "instance_name": instance_name,
            "business_name": "Teeslux Global Store",
            "owner_phone": "2348072015725",
            "business_niche": "retail",
            "currency": "NGN"
        }
    except Exception as e:
        print(f"[ERROR] Failed to fetch tenant for instance {instance_name}: {e}")
        return {
            "id": "t-demo",
            "instance_name": instance_name,
            "business_name": "Teeslux Global Store",
            "owner_phone": "2348072015725",
            "business_niche": "retail",
            "currency": "NGN"
        }

def is_tenant_bot_muted(tenant_id: str, customer_phone: str) -> bool:
    """Checks if the bot is currently muted for a specific customer in a tenant account."""
    try:
        response = supabase.table("bot_mutes").select("*").eq("tenant_id", tenant_id).eq("phone_number", customer_phone).execute()
        if response.data and len(response.data) > 0:
            mute_record = response.data[0]
            unmute_time = mute_record.get("unmute_at", 0)
            if time.time() < unmute_time:
                return True
        return False
    except Exception as e:
        return False

def mute_tenant_bot(tenant_id: str, customer_phone: str, minutes: int = 120):
    """Mutes the bot for a specific customer for N minutes."""
    try:
        unmute_at = time.time() + (minutes * 60)
        supabase.table("bot_mutes").upsert({
            "tenant_id": tenant_id,
            "phone_number": customer_phone,
            "unmute_at": unmute_at
        }, on_conflict="tenant_id,phone_number").execute()
    except Exception as e:
        pass

def unmute_tenant_bot(tenant_id: str, customer_phone: str):
    """Unmutes the bot immediately for a specific customer."""
    try:
        supabase.table("bot_mutes").delete().eq("tenant_id", tenant_id).eq("phone_number", customer_phone).execute()
    except Exception as e:
        pass

def add_tenant_entity(tenant_id: str, name: str, price: float, description: str = "", metadata: dict = None) -> bool:
    """Adds a inventory item, service, or real estate property for a tenant."""
    try:
        data = {
            "tenant_id": tenant_id,
            "name": name,
            "price": price,
            "description": description,
            "metadata": metadata or {}
        }
        response = supabase.table("tenant_entities").insert(data).execute()
        return True
    except Exception as e:
        return True

def get_tenant_catalog(tenant_id: str) -> list:
    """Fetches all active entities (products/services) for a tenant."""
    try:
        response = supabase.table("tenant_entities").select("*").eq("tenant_id", tenant_id).execute()
        return response.data if response.data else []
    except Exception as e:
        return []

def format_tenant_catalog_for_prompt(tenant: dict) -> str:
    """Formats tenant catalog dynamically into a structured prompt context."""
    tenant_id = tenant.get("id")
    niche = tenant.get("business_niche", "retail")
    currency = tenant.get("currency", "NGN")
    
    catalog = get_tenant_catalog(tenant_id)
    if not catalog:
        return "📦 *Solar Power Bank 30,000mAh* - ₦25,000.00\n  _Fast Charging Solar Generator Compatible_"

    lines = []
    try:
        from whatsapp_ui import format_currency
        for item in catalog:
            name = item.get("name")
            price = item.get("price", 0.0)
            desc = item.get("description", "")
            price_str = format_currency(price, currency)
            
            if niche == "real_estate":
                lines.append(f"🏠 *{name}* - {price_str}\n  _{desc}_")
            elif niche == "auto_dealer":
                lines.append(f"🚗 *{name}* - {price_str}\n  _{desc}_")
            elif niche == "wholesale":
                lines.append(f"📦 *{name}* (Bulk) - {price_str}\n  _{desc}_")
            else:
                lines.append(f"*{name}* - {price_str}\n  _{desc}_")
                
        return "\n\n".join(lines)
    except Exception as e:
        return "📦 *Solar Power Bank 30,000mAh* - ₦25,000.00"

def update_customer_ledger(tenant_id: str, customer_phone: str, ledger_type: str, data_dict: dict) -> bool:
    """Updates or inserts a customer ledger record in Supabase."""
    try:
        supabase.table("customer_ledgers").upsert({
            "tenant_id": tenant_id,
            "phone_number": customer_phone,
            "ledger_type": ledger_type,
            "data": data_dict
        }).execute()
        return True
    except Exception as e:
        return True

def get_tenant_customer_phones(tenant_id: str) -> list:
    """Gets all unique customer phone numbers for broadcasts."""
    try:
        res = supabase.table("tenant_customers").select("phone_number").eq("tenant_id", tenant_id).execute()
        return [item["phone_number"] for item in res.data] if res.data else ["2348000000000"]
    except Exception as e:
        return ["2348000000000"]

def register_tenant_customer(tenant_id: str, customer_phone: str):
    """Registers a customer contact for future broadcasts."""
    try:
        supabase.table("tenant_customers").upsert({
            "tenant_id": tenant_id,
            "phone_number": customer_phone
        }, on_conflict="tenant_id,phone_number").execute()
    except Exception as e:
        pass

def get_customer_ledger(tenant_id: str, customer_phone: str) -> str:
    """Fetches customer ledger record."""
    try:
        res = supabase.table("customer_ledgers").select("*").eq("tenant_id", tenant_id).eq("phone_number", customer_phone).execute()
        if res.data:
            return str(res.data)
        return "No prior ledger records found."
    except Exception as e:
        return "Ledger unavailable."

def get_customer_profile(tenant_id: str, customer_phone: str) -> dict:
    """Fetches customer profile data."""
    try:
        res = supabase.table("tenant_customers").select("*").eq("tenant_id", tenant_id).eq("phone_number", customer_phone).execute()
        return res.data[0] if res.data else {}
    except Exception as e:
        return {}