import os
import re
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------------------------------------------------------
# 1. TENANT & CATALOG RETRIEVAL
# -----------------------------------------------------------------------------

def get_tenant_by_instance(instance_name: str) -> dict:
    """Retrieves tenant profile by Evolution API instance name."""
    try:
        res = supabase.table("tenants").select("*").eq("instance_name", instance_name).eq("is_active", True).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        print(f"❌ Error fetching tenant profile: {e}")
        return None

def get_tenant_catalog(tenant_id: str, search_query: str = None) -> str:
    """Fetches real-time catalog items from Supabase."""
    try:
        query = supabase.table("tenant_products").select("name, description, price, stock_quantity").eq("tenant_id", tenant_id)
        if search_query and len(search_query.strip()) > 2:
            query = query.ilike("name", f"%{search_query.strip()}%")
            
        res = query.execute()
        products = res.data or []
        
        if not products:
            res = supabase.table("tenant_products").select("name, description, price, stock_quantity").eq("tenant_id", tenant_id).execute()
            products = res.data or []

        if not products:
            return "No inventory listed in database."
        
        catalog = [f"- *{p['name']}*: ₦{p['price']:,.2f} | Stock: {p['stock_quantity']} units | Info: {p.get('description', 'N/A')}" for p in products]
        return "\n".join(catalog)
    except Exception as e:
        print(f"❌ Error fetching catalog: {e}")
        return "Catalog details currently unavailable."

def get_customer_ledger(tenant_id: str, customer_phone: str) -> str:
    """Retrieves customer account balances, dues, or savings entries."""
    try:
        res = supabase.table("tenant_custom_ledgers").select("ledger_type, data").eq("tenant_id", tenant_id).eq("customer_phone", customer_phone).execute()
        if not res.data:
            return "No specific account balance or ledger records found."
        
        records = [f"[{r['ledger_type']}] Details: {r['data']}" for r in res.data]
        return "\n".join(records)
    except Exception as e:
        print(f"❌ Error fetching customer ledger: {e}")
        return "Custom ledger records unavailable."

# -----------------------------------------------------------------------------
# 2. PERSISTENT CHAT HISTORY & PROFILE MEMORY
# -----------------------------------------------------------------------------

def save_chat_message(tenant_id: str, customer_phone: str, role: str, message: str):
    """Saves every inbound and outbound message in Supabase for cold-start recovery."""
    try:
        supabase.table("tenant_chat_history").insert({
            "tenant_id": tenant_id,
            "customer_phone": customer_phone.strip(),
            "role": role,
            "message": message.strip()
        }).execute()
    except Exception as e:
        print(f"❌ Error saving chat history: {e}")

def get_persistent_chat_history(tenant_id: str, customer_phone: str, limit: int = 10) -> list:
    """Retrieves past turns across server restarts."""
    try:
        res = supabase.table("tenant_chat_history") \
            .select("role, message, created_at") \
            .eq("tenant_id", tenant_id) \
            .eq("customer_phone", customer_phone.strip()) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        
        if not res.data:
            return []
        
        history = list(reversed(res.data))
        return [f"{'Customer' if h['role'] == 'customer' else 'AI'}: {h['message']}" for h in history]
    except Exception as e:
        print(f"❌ Error retrieving chat history: {e}")
        return []

def get_customer_profile(tenant_id: str, customer_phone: str) -> dict:
    """Fetches long-term customer profile memory."""
    try:
        res = supabase.table("tenant_customer_profiles").select("*").eq("tenant_id", tenant_id).eq("customer_phone", customer_phone.strip()).execute()
        return res.data[0] if res.data else {}
    except Exception as e:
        print(f"❌ Error fetching customer profile: {e}")
        return {}

def upsert_customer_profile(tenant_id: str, customer_phone: str, full_name: str = None, notes: str = None):
    """Updates customer profile facts learned during conversation."""
    try:
        data = {"tenant_id": tenant_id, "customer_phone": customer_phone.strip(), "updated_at": datetime.now(timezone.utc).isoformat()}
        if full_name: data["full_name"] = full_name.strip()
        if notes: data["notes"] = notes.strip()
        supabase.table("tenant_customer_profiles").upsert(data, on_conflict="tenant_id,customer_phone").execute()
    except Exception as e:
        print(f"❌ Error updating customer profile: {e}")

# -----------------------------------------------------------------------------
# 3. OWNER ADMIN & REMINDER OPERATIONS
# -----------------------------------------------------------------------------

def add_tenant_product(tenant_id: str, name: str, price: float, description: str, stock: int = 100) -> bool:
    try:
        supabase.table("tenant_products").insert({
            "tenant_id": tenant_id, "name": name.strip(), "price": price, "description": description.strip(), "stock_quantity": stock
        }).execute()
        return True
    except Exception as e:
        print(f"❌ Error adding product: {e}")
        return False

def update_customer_ledger(tenant_id: str, customer_phone: str, ledger_type: str, data_dict: dict) -> bool:
    try:
        supabase.table("tenant_custom_ledgers").upsert({
            "tenant_id": tenant_id, "customer_phone": customer_phone.strip(), "ledger_type": ledger_type.upper(),
            "data": data_dict, "updated_at": datetime.now(timezone.utc).isoformat()
        }, on_conflict="tenant_id,customer_phone,ledger_type").execute()
        return True
    except Exception as e:
        print(f"❌ Error updating ledger: {e}")
        return False

def create_tenant_reminder(tenant_id: str, recipient_phone: str, reminder_text: str, frequency: str, first_run_iso: str) -> bool:
    try:
        supabase.table("tenant_reminders").insert({
            "tenant_id": tenant_id, "recipient_phone": recipient_phone.strip(), "reminder_text": reminder_text.strip(),
            "frequency": frequency.upper(), "next_run_at": first_run_iso, "is_active": True
        }).execute()
        return True
    except Exception as e:
        print(f"❌ Error creating reminder: {e}")
        return False

def get_due_reminders() -> list:
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        res = supabase.table("tenant_reminders").select("*, tenants(instance_name, business_name, owner_phone)").eq("is_active", True).lte("next_run_at", now_iso).execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"❌ Error fetching due reminders: {e}")
        return []

def update_reminder_next_run(reminder_id: str, frequency: str, current_run_iso: str):
    try:
        if frequency == "ONCE":
            supabase.table("tenant_reminders").update({"is_active": False}).eq("id", reminder_id).execute()
            return

        current_dt = datetime.fromisoformat(current_run_iso.replace("Z", "+00:00"))
        days_add = 1 if frequency == "DAILY" else (7 if frequency == "WEEKLY" else 30)
        next_dt = current_dt + timedelta(days=days_add)

        supabase.table("tenant_reminders").update({"next_run_at": next_dt.isoformat()}).eq("id", reminder_id).execute()
    except Exception as e:
        print(f"❌ Error updating reminder schedule: {e}")

# -----------------------------------------------------------------------------
# 4. CONTACTS & MUTE CONTROL
# -----------------------------------------------------------------------------

def register_tenant_customer(tenant_id: str, customer_phone: str):
    try:
        supabase.table("tenant_customers").upsert({"tenant_id": tenant_id, "customer_phone": customer_phone, "last_active": datetime.now(timezone.utc).isoformat()}, on_conflict="tenant_id,customer_phone").execute()
    except Exception as e:
        print(f"❌ Error registering customer: {e}")

def get_tenant_customer_phones(tenant_id: str) -> list:
    try:
        res = supabase.table("tenant_customers").select("customer_phone").eq("tenant_id", tenant_id).execute()
        return [c["customer_phone"] for c in res.data] if res.data else []
    except Exception as e:
        print(f"❌ Error fetching customer phone list: {e}")
        return []

def is_tenant_bot_muted(tenant_id: str, customer_phone: str) -> bool:
    try:
        now = datetime.now(timezone.utc).isoformat()
        res = supabase.table("tenant_bot_mutes").select("*").eq("tenant_id", tenant_id).eq("customer_phone", customer_phone).gt("muted_until", now).execute()
        return len(res.data) > 0
    except Exception as e:
        print(f"❌ Error checking mute status: {e}")
        return False

def mute_tenant_bot(tenant_id: str, customer_phone: str, minutes: int = 60):
    try:
        muted_until = (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()
        supabase.table("tenant_bot_mutes").upsert({"tenant_id": tenant_id, "customer_phone": customer_phone, "muted_until": muted_until}, on_conflict="tenant_id,customer_phone").execute()
    except Exception as e:
        print(f"❌ Error muting bot: {e}")