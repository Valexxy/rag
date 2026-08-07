import os
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_tenant_by_instance(instance_name: str) -> dict:
    """Retrieves tenant configurations and owner credentials by Evolution instance name."""
    try:
        res = supabase.table("tenants").select("*").eq("instance_name", instance_name).eq("is_active", True).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        print(f"❌ Error fetching tenant profile: {e}")
        return None

def get_tenant_catalog(tenant_id: str) -> str:
    """Fetches real-time catalog from Supabase."""
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

def get_customer_ledger(tenant_id: str, customer_phone: str) -> str:
    """Retrieves custom dynamic parameters (savings balances, appointments, dues) for a specific customer."""
    try:
        res = supabase.table("tenant_custom_ledgers").select("ledger_type, data").eq("tenant_id", tenant_id).eq("customer_phone", customer_phone).execute()
        if not res.data:
            return "No custom account records found for this user."
        
        records = []
        for r in res.data:
            records.append(f"[{r['ledger_type']}] Details: {r['data']}")
        return "\n".join(records)
    except Exception as e:
        print(f"❌ Error fetching custom ledger: {e}")
        return "Custom ledger records unavailable."

def add_tenant_product(tenant_id: str, name: str, price: float, description: str, stock: int = 100) -> bool:
    """Allows business owners to add products directly from WhatsApp."""
    try:
        supabase.table("tenant_products").insert({
            "tenant_id": tenant_id,
            "name": name.strip(),
            "price": price,
            "description": description.strip(),
            "stock_quantity": stock
        }).execute()
        return True
    except Exception as e:
        print(f"❌ Error adding product: {e}")
        return False

def update_customer_ledger(tenant_id: str, customer_phone: str, ledger_type: str, data_dict: dict) -> bool:
    """Updates dynamic customer parameters (e.g. contribution updates, savings balances)."""
    try:
        supabase.table("tenant_custom_ledgers").upsert({
            "tenant_id": tenant_id,
            "customer_phone": customer_phone.strip(),
            "ledger_type": ledger_type.upper(),
            "data": data_dict,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }, on_conflict="tenant_id,customer_phone,ledger_type").execute()
        return True
    except Exception as e:
        print(f"❌ Error updating customer ledger: {e}")
        return False

def register_tenant_customer(tenant_id: str, customer_phone: str):
    """Registers new customer contacts to enable future broadcasts."""
    try:
        supabase.table("tenant_customers").upsert({
            "tenant_id": tenant_id,
            "customer_phone": customer_phone,
            "last_active": datetime.now(timezone.utc).isoformat()
        }, on_conflict="tenant_id,customer_phone").execute()
    except Exception as e:
        print(f"❌ Error registering customer contact: {e}")

def get_tenant_customer_phones(tenant_id: str) -> list:
    """Retrieves all registered customer phone numbers for broadcasting."""
    try:
        res = supabase.table("tenant_customers").select("customer_phone").eq("tenant_id", tenant_id).execute()
        return [c["customer_phone"] for c in res.data]
    except Exception as e:
        print(f"❌ Error fetching broadcast phone list: {e}")
        return []

def is_tenant_bot_muted(tenant_id: str, customer_phone: str) -> bool:
    """Checks if the AI bot is currently muted for human agent takeover."""
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
    """Mutes the AI bot for manual human takeover."""
    try:
        muted_until = (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()
        supabase.table("tenant_bot_mutes").upsert({
            "tenant_id": tenant_id,
            "customer_phone": customer_phone,
            "muted_until": muted_until
        }, on_conflict="tenant_id,customer_phone").execute()
    except Exception as e:
        print(f"❌ Error muting bot: {e}")