import os
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

def mute_tenant_bot(tenant_id: str, customer_phone: str, minutes: int = 60):
    """Mutes the bot for a specific customer."""
    try:
        supabase.table("bot_mutes").upsert({
            "tenant_id": tenant_id,
            "phone_number": customer_phone,
            "muted": True
        }).execute()
    except Exception as e:
        print(f"❌ Error muting bot: {e}")

def add_tenant_product(tenant_id: str, title: str, price: float, description: str, stock: int) -> bool:
    """Adds or updates a product in tenant inventory."""
    try:
        supabase.table("tenant_products").insert({
            "tenant_id": tenant_id,
            "title": title,
            "price": price,
            "description": description,
            "stock": stock
        }).execute()
        return True
    except Exception as e:
        print(f"❌ Error adding product: {e}")
        return False

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
        print(f"❌ Error fetching customer phones: {e}")
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

def get_tenant_catalog(tenant_id: str, search_query: str = "") -> str:
    """Fetches formatted tenant catalog string supporting both title and name columns."""
    try:
        res = supabase.table("tenant_products").select("*").eq("tenant_id", tenant_id).execute()
        products = res.data or []
        if not products:
            return "No products currently listed in our catalog."
        
        catalog_lines = []
        for p in products:
            # Check both 'title' and 'name' columns to prevent None display
            p_name = p.get('title') or p.get('name') or 'Product Item'
            p_price = p.get('price', 0)
            p_stock = p.get('stock', 0)
            p_desc = p.get('description', '')
            catalog_lines.append(f"• *{p_name}* - ₦{p_price:,.2f} (Stock: {p_stock})\n  _{p_desc}_")
        return "\n\n".join(catalog_lines)
    except Exception as e:
        return "Catalog temporarily unavailable."

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