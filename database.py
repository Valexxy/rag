import os
from datetime import datetime, timezone
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_tenant_by_instance(instance_name: str) -> dict:
    """Retrieves tenant settings, API keys, and business details by Evolution instance."""
    try:
        res = supabase.table("tenants").select("*").eq("instance_name", instance_name).eq("is_active", True).execute()
        if res.data:
            return res.data[0]
        return None
    except Exception as e:
        print(f"❌ Error fetching tenant profile: {e}")
        return None

def get_tenant_catalog(tenant_id: str) -> str:
    """Fetches real-time products/services for a specific tenant."""
    try:
        res = supabase.table("tenant_products").select("name, description, price, stock_quantity").eq("tenant_id", tenant_id).execute()
        products = res.data
        if not products:
            return "No inventory listed."
        
        catalog = []
        for p in products:
            catalog.append(f"- {p['name']}: ₦{p['price']:,.2f} | Stock: {p['stock_quantity']} units | Info: {p.get('description', 'N/A')}")
        return "\n".join(catalog)
    except Exception as e:
        print(f"❌ Error fetching catalog: {e}")
        return "Catalog details currently unavailable."

def is_tenant_bot_muted(tenant_id: str, customer_phone: str) -> bool:
    """Checks if the bot is currently muted for a specific customer on a specific tenant."""
    try:
        now = datetime.now(timezone.utc).isoformat()
        res = supabase.table("tenant_bot_mutes") \
            .select("*") \
            .eq("tenant_id", tenant_id) \
            .eq("customer_phone", customer_phone) \
            .gt("muted_until", now) \
            .execute()
        return len(res.data) > 0
    except Exception as e:
        print(f"❌ Error checking mute status: {e}")
        return False

def mute_tenant_bot(tenant_id: str, customer_phone: str, minutes: int = 60):
    """Mutes the bot for human agent takeover."""
    try:
        muted_until = (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()
        supabase.table("tenant_bot_mutes").upsert({
            "tenant_id": tenant_id,
            "customer_phone": customer_phone,
            "muted_until": muted_until
        }, on_conflict="tenant_id,customer_phone").execute()
    except Exception as e:
        print(f"❌ Error setting mute: {e}")