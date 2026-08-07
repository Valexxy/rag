import os
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
# Accept either variable name to prevent configuration crashes
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------------------------------------------------------
# 1. TENANT PROFILE & CATALOG RETRIEVAL
# -----------------------------------------------------------------------------

def get_tenant_by_instance(instance_name: str) -> dict:
    """Retrieves tenant settings, API credentials, and owner info by Evolution instance."""
    try:
        res = supabase.table("tenants").select("*").eq("instance_name", instance_name).eq("is_active", True).execute()
        if res.data:
            return res.data[0]
        return None
    except Exception as e:
        print(f"❌ Error fetching tenant profile: {e}")
        return None

def get_tenant_catalog(tenant_id: str) -> str:
    """Fetches real-time products/services inventory for a tenant from Supabase."""
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
    """Retrieves custom dynamic parameters (savings balances, dues, appointments) for a specific customer."""
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

# -----------------------------------------------------------------------------
# 2. IN-CHAT OWNER DATABASE OPERATIONS
# -----------------------------------------------------------------------------

def add_tenant_product(tenant_id: str, name: str, price: float, description: str, stock: int = 100) -> bool:
    """Allows business owners to insert new catalog items via WhatsApp commands."""
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
    """Upserts dynamic customer account metadata (savings targets, contributions, dues)."""
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

# -----------------------------------------------------------------------------
# 3. CONTACT DIRECTORY & BROADCASTING
# -----------------------------------------------------------------------------

def register_tenant_customer(tenant_id: str, customer_phone: str):
    """Registers or updates customer phone numbers for broadcast delivery."""
    try:
        supabase.table("tenant_customers").upsert({
            "tenant_id": tenant_id,
            "customer_phone": customer_phone,
            "last_active": datetime.now(timezone.utc).isoformat()
        }, on_conflict="tenant_id,customer_phone").execute()
    except Exception as e:
        print(f"❌ Error registering customer contact: {e}")

def get_tenant_customer_phones(tenant_id: str) -> list:
    """Retrieves all registered customer phone numbers for broadcast dispatch."""
    try:
        res = supabase.table("tenant_customers").select("customer_phone").eq("tenant_id", tenant_id).execute()
        return [c["customer_phone"] for c in res.data] if res.data else []
    except Exception as e:
        print(f"❌ Error fetching customer phone list: {e}")
        return []

# -----------------------------------------------------------------------------
# 4. BOT MUTE & HUMAN TAKEOVER CONTROLS
# -----------------------------------------------------------------------------

def is_tenant_bot_muted(tenant_id: str, customer_phone: str) -> bool:
    """Checks if the AI bot is currently muted for a specific customer on a business instance."""
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
    """Mutes the AI bot for human agent takeover."""
    try:
        muted_until = (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()
        supabase.table("tenant_bot_mutes").upsert({
            "tenant_id": tenant_id,
            "customer_phone": customer_phone,
            "muted_until": muted_until
        }, on_conflict="tenant_id,customer_phone").execute()
    except Exception as e:
        print(f"❌ Error setting mute: {e}")

# -----------------------------------------------------------------------------
# 5. SMART AUTOMATED REMINDER ENGINE
# -----------------------------------------------------------------------------

def create_tenant_reminder(tenant_id: str, recipient_phone: str, reminder_text: str, frequency: str, first_run_iso: str) -> bool:
    """Schedules a new recurring or one-time reminder in Supabase."""
    try:
        supabase.table("tenant_reminders").insert({
            "tenant_id": tenant_id,
            "recipient_phone": recipient_phone.strip(),
            "reminder_text": reminder_text.strip(),
            "frequency": frequency.upper(),
            "next_run_at": first_run_iso,
            "is_active": True
        }).execute()
        return True
    except Exception as e:
        print(f"❌ Error creating reminder: {e}")
        return False

def get_due_reminders() -> list:
    """Fetches all active reminders that are due for dispatch."""
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        res = supabase.table("tenant_reminders") \
            .select("*, tenants(instance_name, business_name, owner_phone)") \
            .eq("is_active", True) \
            .lte("next_run_at", now_iso) \
            .execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"❌ Error fetching due reminders: {e}")
        return []

def update_reminder_next_run(reminder_id: str, frequency: str, current_run_iso: str):
    """Recalculates and updates the next trigger time for recurring reminders (DAILY, WEEKLY, MONTHLY)."""
    try:
        if frequency == "ONCE":
            supabase.table("tenant_reminders").update({"is_active": False}).eq("id", reminder_id).execute()
            return

        current_dt = datetime.fromisoformat(current_run_iso.replace("Z", "+00:00"))
        if frequency == "DAILY":
            next_dt = current_dt + timedelta(days=1)
        elif frequency == "WEEKLY":
            next_dt = current_dt + timedelta(weeks=1)
        elif frequency == "MONTHLY":
            next_dt = current_dt + timedelta(days=30)
        else:
            next_dt = current_dt + timedelta(days=1)

        supabase.table("tenant_reminders").update({
            "next_run_at": next_dt.isoformat()
        }).eq("id", reminder_id).execute()
    except Exception as e:
        print(f"❌ Error updating reminder schedule: {e}")