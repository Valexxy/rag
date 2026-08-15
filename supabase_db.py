"""
====================================================================
SUPABASE DATABASE ENGINE v2026
====================================================================
Connects to Supabase PostgreSQL and provides all data operations:
- Tenant resolution by phone_number_id
- Atomic stock purchase via process_atomic_purchase() stored proc
- Order status updates
- Customer credit ledger management
====================================================================
"""

import os
import logging
from typing import Optional

logger = logging.getLogger("SupabaseDB")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://emohdirbihcpnnmqtzrs.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

_supabase_client = None


def get_client():
    global _supabase_client
    if _supabase_client:
        return _supabase_client
    try:
        from supabase import create_client
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("[SupabaseDB] ✅ Supabase client initialized")
        return _supabase_client
    except Exception as e:
        logger.error(f"[SupabaseDB] Failed to initialize: {e}")
        return None


# ── TENANT RESOLUTION ─────────────────────────────────────────────────────
def get_tenant_by_phone_number_id(phone_number_id: str) -> Optional[dict]:
    """Resolves a tenant from an incoming Meta phone_number_id."""
    db = get_client()
    if not db:
        return None
    try:
        res = db.table("tenants").select("*").eq("phone_number_id", phone_number_id).eq("is_active", True).single().execute()
        return res.data
    except Exception as e:
        logger.warning(f"[SupabaseDB] get_tenant_by_phone_number_id: {e}")
        return None


def get_tenant_by_instance(instance_name: str) -> Optional[dict]:
    """Resolves a tenant from Evolution API instance name."""
    db = get_client()
    if not db:
        return None
    try:
        res = db.table("tenants").select("*").eq("instance_name", instance_name).eq("is_active", True).single().execute()
        return res.data
    except Exception as e:
        logger.warning(f"[SupabaseDB] get_tenant_by_instance: {e}")
        return None


def get_tenant_by_owner_phone(owner_phone: str) -> Optional[dict]:
    """Resolves tenant from store manager phone (for #approve / #dispatch commands)."""
    db = get_client()
    if not db:
        return None
    try:
        res = db.table("tenants").select("*").eq("owner_phone", owner_phone).eq("is_active", True).single().execute()
        return res.data
    except Exception as e:
        logger.warning(f"[SupabaseDB] get_tenant_by_owner_phone: {e}")
        return None


# ── PRODUCT CATALOG ───────────────────────────────────────────────────────
def get_products(tenant_id: str) -> list:
    """Returns all products for a tenant."""
    db = get_client()
    if not db:
        return []
    try:
        res = db.table("products").select("*").eq("tenant_id", tenant_id).gt("stock", 0).execute()
        return res.data or []
    except Exception as e:
        logger.warning(f"[SupabaseDB] get_products: {e}")
        return []


def search_product(tenant_id: str, name_query: str) -> Optional[dict]:
    """Case-insensitive product search by name for a given tenant."""
    db = get_client()
    if not db:
        return None
    try:
        res = db.table("products").select("*").eq("tenant_id", tenant_id).ilike("name", f"%{name_query}%").limit(1).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        logger.warning(f"[SupabaseDB] search_product: {e}")
        return None


# ── ATOMIC PURCHASE (PostgreSQL Stored Procedure) ─────────────────────────
def call_atomic_purchase(
    tenant_id: str,
    product_id: int,
    quantity: int,
    customer_phone: str,
    reference: str,
    amount_received: float
) -> dict:
    """
    Calls the process_atomic_purchase() PostgreSQL stored procedure.
    This is the ONLY way stock is deducted — pessimistic lock prevents overselling.
    Returns a result dict with success, status, and balance_due if underpaid.
    """
    db = get_client()
    if not db:
        return {"success": False, "reason": "DB_UNAVAILABLE"}
    try:
        res = db.rpc("process_atomic_purchase", {
            "p_tenant_id": tenant_id,
            "p_product_id": str(product_id),
            "p_quantity": quantity,
            "p_customer_phone": customer_phone,
            "p_reference": reference,
            "p_amount_received": amount_received
        }).execute()

        return res.data if res.data else {"success": False, "reason": "RPC_EMPTY_RESPONSE"}
    except Exception as e:
        logger.error(f"[SupabaseDB] call_atomic_purchase error: {e}")
        return {"success": False, "reason": str(e)}


# ── ORDER MANAGEMENT ──────────────────────────────────────────────────────
def get_order_by_reference(reference: str) -> Optional[dict]:
    db = get_client()
    if not db:
        return None
    try:
        res = db.table("orders").select("*").eq("payment_reference", reference).single().execute()
        return res.data
    except Exception as e:
        logger.warning(f"[SupabaseDB] get_order_by_reference: {e}")
        return None


def update_order_status(reference: str, status: str, extra: dict = None):
    db = get_client()
    if not db:
        return
    try:
        payload = {"status": status, "updated_at": "now()"}
        if extra:
            payload.update(extra)
        db.table("orders").update(payload).eq("payment_reference", reference).execute()
        logger.info(f"[SupabaseDB] Order {reference} → {status}")
    except Exception as e:
        logger.error(f"[SupabaseDB] update_order_status error: {e}")


# ── CUSTOMER CREDIT LEDGER ────────────────────────────────────────────────
def get_customer_credit(tenant_id: str, phone: str) -> float:
    """Returns the STORE_CREDIT balance for a customer."""
    db = get_client()
    if not db:
        return 0.0
    try:
        res = db.table("customer_ledgers").select("balance").eq("tenant_id", tenant_id).eq("phone_number", phone).eq("ledger_type", "STORE_CREDIT").single().execute()
        return float(res.data["balance"]) if res.data else 0.0
    except Exception:
        return 0.0


# ── BOT MUTE MANAGEMENT ───────────────────────────────────────────────────
def is_bot_muted(tenant_id: str, phone: str) -> bool:
    db = get_client()
    if not db:
        return False
    try:
        res = db.table("bot_mutes").select("muted").eq("tenant_id", tenant_id).eq("phone_number", phone).single().execute()
        return res.data.get("muted", False) if res.data else False
    except Exception:
        return False


def set_bot_mute(tenant_id: str, phone: str, muted: bool):
    db = get_client()
    if not db:
        return
    try:
        db.table("bot_mutes").upsert({
            "tenant_id": tenant_id,
            "phone_number": phone,
            "muted": muted,
            "reason": "HUMAN_TAKEOVER" if muted else "AI_RESTORED"
        }).execute()
    except Exception as e:
        logger.error(f"[SupabaseDB] set_bot_mute error: {e}")
