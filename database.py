import os
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def format_naira(amount: float | Decimal) -> str:
    """Formats figures into precise Nigerian Naira currency strings with zero float drift."""
    d_amount = Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return f"₦{d_amount:,.2f}"

def get_tenant_by_instance(instance_name: str) -> dict:
    """Retrieves tenant profile by Evolution API instance name."""
    try:
        res = supabase.table("tenants").select("*").eq("instance_name", instance_name).eq("is_active", True).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        print(f"❌ Error fetching tenant profile: {e}")
        return None

def get_tenant_catalog(tenant_id: str, search_query: str = None) -> str:
    """Fetches real-time catalog items from Supabase with precise decimal pricing."""
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
        
        catalog = []
        for p in products:
            price_str = format_naira(p['price'])
            stock = p['stock_quantity']
            status = f"{stock} units available" if stock > 0 else "Out of stock (Available for Pre-order / Sourcing)"
            catalog.append(f"- *{p['name']}*: {price_str} | Status: {status} | Info: {p.get('description', 'Standard item')}")
        return "\n".join(catalog)
    except Exception as e:
        print(f"❌ Error fetching catalog: {e}")
        return "Catalog details currently unavailable."

def update_enterprise_ledger(tenant_id: str, customer_phone: str, ledger_type: str, amount: float, metadata: dict) -> tuple[bool, bool]:
    """
    Updates enterprise ledgers (Esusu, Wholesale, Bulk Orders) with strict Decimal math.
    Returns: (success_bool, is_high_value_bool)
    """
    try:
        precise_amount = Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        is_high_value = precise_amount >= Decimal('1000000.00') # 1 Million Naira threshold

        payload = {
            "tenant_id": tenant_id,
            "customer_phone": customer_phone.strip(),
            "ledger_type": ledger_type.upper(),
            "amount": float(precise_amount),
            "metadata": metadata,
            "is_high_value": is_high_value,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        supabase.table("tenant_enterprise_ledgers").upsert(payload, on_conflict="tenant_id,customer_phone,ledger_type").execute()
        return True, is_high_value
    except Exception as e:
        print(f"❌ Enterprise ledger error: {e}")
        return False, False

def get_customer_ledger(tenant_id: str, customer_phone: str) -> str:
    """Retrieves customer account balances and ledger entries."""
    try:
        res = supabase.table("tenant_enterprise_ledgers").select("ledger_type, amount, metadata").eq("tenant_id", tenant_id).eq("customer_phone", customer_phone).execute()
        if not res.data:
            return "No active financial ledgers or savings accounts on file."
        
        records = []
        for r in res.data:
            amt = format_naira(r['amount'])
            records.append(f"[{r['ledger_type']}] Value: {amt} | Details: {r['metadata']}")
        return "\n".join(records)
    except Exception as e:
        print(f"❌ Error fetching ledger: {e}")
        return "Ledger records unavailable."

def save_chat_message(tenant_id: str, customer_phone: str, role: str, message: str):
    """Persists chat history to Supabase."""
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
    """Retrieves past conversation turns across server restarts."""
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
        print(f"❌ Error retrieving history: {e}")
        return []

def register_tenant_customer(tenant_id: str, customer_phone: str):
    """Registers contact for tracking and broadcasting."""
    try:
        supabase.table("tenant_customers").upsert({
            "tenant_id": tenant_id,
            "customer_phone": customer_phone,
            "last_active": datetime.now(timezone.utc).isoformat()
        }, on_conflict="tenant_id,customer_phone").execute()
    except Exception as e:
        print(f"❌ Error registering customer: {e}")

def get_tenant_customer_phones(tenant_id: str) -> list:
    """Retrieves all registered customer phone numbers for broadcasts."""
    try:
        res = supabase.table("tenant_customers").select("customer_phone").eq("tenant_id", tenant_id).execute()
        return [c["customer_phone"] for c in res.data] if res.data else []
    except Exception as e:
        print(f"❌ Error fetching customer phone list: {e}")
        return []

def is_tenant_bot_muted(tenant_id: str, customer_phone: str) -> bool:
    """Checks if bot is muted for a contact (manual takeover or blacklist)."""
    try:
        now = datetime.now(timezone.utc).isoformat()
        res = supabase.table("tenant_bot_mutes").select("*").eq("tenant_id", tenant_id).eq("customer_phone", customer_phone).gt("muted_until", now).execute()
        return len(res.data) > 0
    except Exception as e:
        print(f"❌ Error checking mute: {e}")
        return False

def mute_tenant_bot(tenant_id: str, customer_phone: str, minutes: int = 60):
    """Mutes the bot for a specific contact."""
    try:
        muted_until = (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()
        supabase.table("tenant_bot_mutes").upsert({"tenant_id": tenant_id, "customer_phone": customer_phone, "muted_until": muted_until}, on_conflict="tenant_id,customer_phone").execute()
    except Exception as e:
        print(f"❌ Error muting bot: {e}")

def add_tenant_product(tenant_id: str, name: str, price: float, description: str, stock: int = 100) -> bool:
    """Adds a new product to store inventory."""
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

def create_tenant_reminder(tenant_id: str, recipient_phone: str, reminder_text: str, frequency: str, first_run_iso: str) -> bool:
    """Creates a scheduled operational reminder."""
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
    """Fetches reminders that are currently due."""
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        res = supabase.table("tenant_reminders").select("*, tenants(instance_name, business_name, owner_phone)").eq("is_active", True).lte("next_run_at", now_iso).execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"❌ Error fetching due reminders: {e}")
        return []

def update_reminder_next_run(reminder_id: str, frequency: str, current_run_iso: str):
    """Updates the next run timestamp for repeating reminders."""
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