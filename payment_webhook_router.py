"""
====================================================================
PAYMENT WEBHOOK ROUTER v2026
====================================================================
Handles verified, HMAC-signed inbound payment events from:
  1. Monnify   — POST /api/v1/payments/monnify-webhook
  2. Paystack  — POST /api/v1/payments/paystack-webhook

For each verified payment:
  - Calls process_atomic_purchase() PostgreSQL stored procedure
  - Handles underpayment (cumulative ledger)
  - Handles overpayment (store credit)
  - Sets status = PENDING_HUMAN_VERIFICATION
  - Alerts Store Manager (+2348072015725) on WhatsApp
  - Sends holding message to customer
====================================================================
"""

import json
import logging
import uuid

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks

from security_fortress import security_fortress
from high_performance_cache import idempotency_manager, nibss_queue
from supabase_db import call_atomic_purchase, get_order_by_reference, update_order_status
from meta_whatsapp_sender import send_whatsapp_text

logger = logging.getLogger("PaymentWebhookRouter")
router = APIRouter()


# ── FORMAT HUMAN VERIFICATION ALERT ──────────────────────────────────────
def _manager_verification_alert(order_ref: str, amount: float, customer_phone: str, product_name: str, tenant: dict) -> str:
    return (
        f"🔔 *[PAYMENT RECEIVED — HUMAN VERIFICATION REQUIRED]*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🏪 *Store:* {tenant.get('business_name', 'Your Store')}\n"
        f"👤 *Customer:* +{customer_phone}\n"
        f"📦 *Product:* {product_name}\n"
        f"💰 *Amount Received:* ₦{amount:,.2f}\n"
        f"🔖 *Order Ref:* #{order_ref}\n\n"
        f"⚡ *ACTION REQUIRED:* Reply `#approve {order_ref}` to verify payment and authorize dispatch!"
    )


def _customer_pending_message(amount: float, order_ref: str, manager_phone: str, business_name: str) -> str:
    return (
        f"💳 *[Payment Received — Final Verification Pending]*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"We have received your payment of *₦{amount:,.2f}* for Order *#{order_ref}*.\n\n"
        f"🛡️ *Security Verification:* Our Store Manager (+{manager_phone}) is confirming your payment now.\n\n"
        f"✅ Once verified, your formal dispatch receipt and waybill tracking will be sent here immediately!"
    )


def _underpaid_message(amount_paid: float, amount_expected: float, balance_due: float, account_number: str, bank_name: str, account_name: str) -> str:
    return (
        f"⚠️ *[Partial Payment Received]*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"We received *₦{amount_paid:,.2f}* of your required *₦{amount_expected:,.2f}*.\n\n"
        f"💵 *Outstanding Balance:* ₦{balance_due:,.2f}\n\n"
        f"Please transfer the remaining balance to the same official account:\n"
        f"🏦 *Bank:* {bank_name}\n"
        f"🔢 *Account:* `{account_number}`\n"
        f"👤 *Name:* {account_name}\n\n"
        f"⚠️ Stock is reserved for you until balance is cleared. Do NOT pay to any other account."
    )


def _overpaid_message(amount_paid: float, amount_expected: float, surplus: float, order_ref: str) -> str:
    return (
        f"🎉 *[Payment Complete — Overpayment Detected]*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"We received *₦{amount_paid:,.2f}* for Order *#{order_ref}* (expected ₦{amount_expected:,.2f}).\n\n"
        f"💵 *Surplus:* ₦{surplus:,.2f} has been added to your *Store Credit Wallet*.\n\n"
        f"Reply `#refund` to request an instant bank refund, or use the credit on your next order!"
    )


# ── MONNIFY WEBHOOK ───────────────────────────────────────────────────────
@router.post("/api/v1/payments/monnify-webhook")
async def monnify_webhook(request: Request, background_tasks: BackgroundTasks):
    payload_bytes = await request.body()
    signature = request.headers.get("monnify-signature", "")

    # Get tenant monnify secret (use env fallback for now)
    import os
    monnify_secret = os.environ.get("MONNIFY_SECRET_KEY", "")

    # 1. Verify HMAC SHA-256 Signature
    if not security_fortress.verify_monnify_signature(payload_bytes.decode(), signature, monnify_secret):
        logger.warning("[Monnify] ❌ Invalid HMAC signature — rejecting webhook")
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        payload = json.loads(payload_bytes)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event_type = payload.get("eventType", "")
    event_data = payload.get("eventData", {})
    payment_ref = event_data.get("paymentReference", "")
    event_id = f"monnify:{payment_ref}:{event_type}"

    # 2. Redis Idempotency Lock — Prevent Duplicate Processing
    if not idempotency_manager.check_and_lock(event_id):
        logger.info(f"[Monnify] Duplicate event dropped: {event_id}")
        return {"status": "duplicate_ignored"}

    # 3. Handle Payment Events
    if event_type not in ("SUCCESSFUL_TRANSACTION", "PAID"):
        if event_type == "PENDING_SETTLEMENT":
            # NIBSS Network Delay — Queue for polling
            nibss_queue.enqueue(payment_ref, event_data)
            logger.info(f"[Monnify] NIBSS pending queue: {payment_ref}")
        return {"status": "event_noted"}

    amount_paid = float(event_data.get("amountPaid", 0))
    customer_phone = event_data.get("customer", {}).get("phone", "").replace("+", "")
    product_name = event_data.get("paymentDescription", "Your Order")
    account_number = event_data.get("destinationAccountNumber", "")
    bank_name = event_data.get("destinationBankName", "")
    account_name = event_data.get("destinationAccountName", "")

    # 4. Resolve order from DB
    existing_order = get_order_by_reference(payment_ref)
    if not existing_order:
        logger.warning(f"[Monnify] Order not found for reference: {payment_ref}")
        return {"status": "order_not_found"}

    tenant_id = existing_order["tenant_id"]
    product_id = existing_order["product_id"]
    quantity = existing_order["quantity"]
    amount_expected = float(existing_order["amount_expected"])

    # Import tenant lookup (late to avoid circular)
    from supabase_db import get_client
    db = get_client()
    tenant = {}
    if db:
        try:
            r = db.table("tenants").select("*").eq("id", tenant_id).single().execute()
            tenant = r.data or {}
        except Exception:
            pass

    manager_phone = tenant.get("owner_phone", "2348072015725").replace("+", "")

    # 5. Call Atomic Purchase Stored Procedure
    result = call_atomic_purchase(
        tenant_id=tenant_id,
        product_id=product_id,
        quantity=quantity,
        customer_phone=customer_phone,
        reference=payment_ref,
        amount_received=amount_paid
    )

    # 6. Handle Result: Underpaid
    if not result.get("success") and result.get("reason") == "UNDERPAID":
        balance_due = float(result.get("balance_due", 0))
        background_tasks.add_task(
            send_whatsapp_text,
            f"+{customer_phone}",
            _underpaid_message(amount_paid, amount_expected, balance_due, account_number, bank_name, account_name)
        )
        return {"status": "underpaid_noted"}

    # 7. Handle Result: Out of Stock
    if not result.get("success") and result.get("reason") == "OUT_OF_STOCK":
        background_tasks.add_task(
            send_whatsapp_text,
            f"+{customer_phone}",
            f"⚠️ We're sorry — the item you ordered just went out of stock. Our manager (+{manager_phone}) will contact you to arrange a full refund or substitute product!"
        )
        return {"status": "out_of_stock"}

    # 8. Payment Complete (Full or Overpaid) → PENDING_HUMAN_VERIFICATION
    if result.get("success"):
        surplus = float(result.get("surplus", 0))

        # Customer holding message
        background_tasks.add_task(
            send_whatsapp_text,
            f"+{customer_phone}",
            _customer_pending_message(amount_paid, payment_ref, manager_phone, tenant.get("business_name", "our store"))
        )

        # Overpayment notification
        if result.get("overpaid") and surplus > 0:
            background_tasks.add_task(
                send_whatsapp_text,
                f"+{customer_phone}",
                _overpaid_message(amount_paid, amount_expected, surplus, payment_ref)
            )

        # Manager verification alert
        background_tasks.add_task(
            send_whatsapp_text,
            f"+{manager_phone}",
            _manager_verification_alert(payment_ref, amount_paid, customer_phone, product_name, tenant)
        )

        logger.info(f"[Monnify] ✅ Payment verified → PENDING_HUMAN_VERIFICATION for {payment_ref}")
        return {"status": "pending_human_verification"}

    return {"status": "processing_error"}


# ── PAYSTACK WEBHOOK ──────────────────────────────────────────────────────
@router.post("/api/v1/payments/paystack-webhook")
async def paystack_webhook(request: Request, background_tasks: BackgroundTasks):
    payload_bytes = await request.body()
    signature = request.headers.get("x-paystack-signature", "")

    import os
    paystack_secret = os.environ.get("PAYSTACK_SECRET_KEY", "")

    # 1. Verify HMAC SHA-512
    if not security_fortress.verify_paystack_signature(payload_bytes, signature, paystack_secret):
        logger.warning("[Paystack] ❌ Invalid HMAC signature — rejecting webhook")
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        payload = json.loads(payload_bytes)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if payload.get("event") != "charge.success":
        return {"status": "event_noted"}

    data = payload.get("data", {})
    reference = data.get("reference", "")
    amount_paid = float(data.get("amount", 0)) / 100  # Paystack sends in kobo
    customer_phone = data.get("metadata", {}).get("customer_phone", "").replace("+", "")
    event_id = f"paystack:{reference}"

    # 2. Redis Idempotency Check
    if not idempotency_manager.check_and_lock(event_id):
        return {"status": "duplicate_ignored"}

    # 3. Resolve order
    existing_order = get_order_by_reference(reference)
    if not existing_order:
        return {"status": "order_not_found"}

    result = call_atomic_purchase(
        tenant_id=existing_order["tenant_id"],
        product_id=existing_order["product_id"],
        quantity=existing_order["quantity"],
        customer_phone=customer_phone,
        reference=reference,
        amount_received=amount_paid
    )

    if result.get("success"):
        # Fetch tenant for manager notification
        from supabase_db import get_client
        db = get_client()
        tenant = {}
        if db:
            try:
                r = db.table("tenants").select("*").eq("id", existing_order["tenant_id"]).single().execute()
                tenant = r.data or {}
            except Exception:
                pass

        manager_phone = tenant.get("owner_phone", "2348072015725").replace("+", "")

        background_tasks.add_task(
            send_whatsapp_text,
            f"+{customer_phone}",
            _customer_pending_message(amount_paid, reference, manager_phone, tenant.get("business_name", "our store"))
        )
        background_tasks.add_task(
            send_whatsapp_text,
            f"+{manager_phone}",
            _manager_verification_alert(reference, amount_paid, customer_phone, "Order Item", tenant)
        )
        return {"status": "pending_human_verification"}

    return {"status": "processing_error"}
