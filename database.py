import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def get_tenant_by_instance(instance_name: str) -> dict:
    """Fetches tenant profile by WhatsApp instance name."""
    try:
        res = supabase.table("tenants").select("*").eq("instance_name", instance_name).single().execute()
        return res.data
    except Exception as e:
        print(f"❌ Error fetching tenant by instance: {e}")
        return None

def is_tenant_bot_muted(tenant_id: str, customer_phone: str) -> bool:
    """Checks if the bot is temporarily muted for a customer due to human takeover."""
    try:
        res = supabase.table("bot_mutes").select("*").eq("tenant_id", tenant_id).eq("phone_number", customer_phone).execute()
        if res.data:
            return True
        return False
    except Exception as e:
        return False

def mute_tenant_bot(tenant_id: str, customer_phone: str, minutes: int = 120):
    """Mutes the bot for a specific customer."""
    try:
        supabase.table("bot_mutes").upsert({
            "tenant_id": tenant_id,
            "phone_number": customer_phone,
            "muted": True
        }).execute()
    except Exception as e:
        print(f"❌ Error muting bot: {e}")

def add_tenant_entity(tenant_id: str, name: str, price: float, description: str, metadata: dict = None) -> bool:
    """Universal function to add ANY business offering with dynamic metadata."""
    try:
        supabase.table("tenant_entities").insert({
            "tenant_id": tenant_id,
            "name": name,
            "price": price,
            "description": description,
            "metadata": metadata or {}
        }).execute()
        return True
    except Exception as e:
        print(f"❌ DB Insert Error: {e}")
        return False

def get_tenant_catalog(tenant: dict, search_query: str = "") -> str:
    """Dynamically formats the business offerings based on their niche."""
    try:
        res = supabase.table("tenant_entities").select("*").eq("tenant_id", tenant["id"]).execute()
        entities = res.data or []
        if not entities:
            return "No offerings currently listed."
        
        niche = tenant.get("business_niche", "retail").lower()
        lines = []
        
        for e in entities:
            name = e.get('name', 'Item')
            price_str = f"₦{e.get('price', 0):,.2f}" if e.get('price', 0) > 0 else "Custom Quote"
            desc = e.get('description', '')
            meta = e.get('metadata', {})
            
            # Deterministic formatting based on business type
            if niche == "real_estate":
                loc = meta.get("location", "Contact for location")
                lines.append(f"🏠 *{name}* - {price_str}\n  📍 {loc}\n  _{desc}_")
            elif niche == "salon" or niche == "service":
                dur = meta.get("duration", "")
                dur_str = f" ({dur})" if dur else ""
                lines.append(f"✂️ *{name}*{dur_str} - {price_str}\n  _{desc}_")
            else: # Default Retail/Importation
                lines.append(f"📦 *{name}* - {price_str}\n  _{desc}_")
                
        return "\n\n".join(lines)
    except Exception as e:
        return "Catalog temporarily unavailable."

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
        print(f"❌ Error updating customer ledger: {e}")
        return False

def get_tenant_customer_phones(tenant_id: str) -> list:
    """Gets all unique customer phone numbers for broadcasts."""
    try:
        res = supabase.table("tenant_customers").select("phone_number").eq("tenant_id", tenant_id).execute()
        return [item["phone_number"] for item in res.data] if res.data else []
    except Exception as e:
        return []

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
        res = supabase.table("tenant_customers").select("*").eq("tenant_id", tenant_id).eq("phone_number", customer_phone).single().execute()
        return res.data or {}
    except Exception as e:
        return {}