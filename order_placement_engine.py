"""
====================================================================
AUTOMATED WHATSAPP ORDER PLACEMENT & RECEIPT ENGINE (v2026)
====================================================================
Handles customer order placement (#buy / #order), state management,
itemized WhatsApp receipt generation, and real-time manager notifications.
"""

import time
import random
import logging
from typing import Dict, Optional

logger = logging.getLogger("OrderPlacementEngine")

class OrderPlacementEngine:
    """Manages order creation, receipt formatting, and manager notifications."""

    def generate_receipt(
        self,
        receipt_id: str,
        business_name: str,
        customer_phone: str,
        product_name: str,
        price: float,
        delivery_address: str = "Pending Confirmation",
        delivery_fee: float = 5000.0
    ) -> str:
        """Formats an itemized WhatsApp receipt card for the customer."""
        total = price + delivery_fee
        return (
            f"🛍️ *[{business_name} — Official Order Receipt]*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🧾 *Receipt ID:* `{receipt_id}`\n"
            f"👤 *Customer:* `+{customer_phone}`\n"
            f"📦 *Item:* *{product_name}*\n"
            f"💰 *Item Price:* ₦{price:,.2f}\n"
            f"🚚 *Delivery Fee:* ₦{delivery_fee:,.2f}\n"
            f"💵 *Total Payable:* *₦{total:,.2f}*\n"
            f"📍 *Delivery Address:* `{delivery_address}`\n\n"
            f"💳 *Payment Options:*\n"
            f"• *Bank Transfer:* Zenith Bank | `1012345678` | Teeslux Global\n"
            f"• *Pay on Delivery:* Available within Onitsha & Environs\n\n"
            f"📲 *Manager Alert:* Our store manager has been notified and will confirm delivery details with you shortly!"
        )

    def generate_manager_alert(
        self,
        receipt_id: str,
        business_name: str,
        customer_phone: str,
        product_name: str,
        price: float,
        delivery_fee: float = 5000.0
    ) -> str:
        """Formats a real-time order alert for the store manager."""
        total = price + delivery_fee
        return (
            f"🚨 *[NEW ORDER RECEIVED — MANAGER ALERT]* 🚨\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🏪 *Store:* {business_name}\n"
            f"🧾 *Order ID:* `{receipt_id}`\n"
            f"👤 *Customer Phone:* `+{customer_phone}`\n"
            f"📦 *Item Purchased:* *{product_name}*\n"
            f"💵 *Total Order Amount:* *₦{total:,.2f}*\n\n"
            f"💬 Please reach out to customer `+{customer_phone}` to finalize delivery & payment!"
        )

    def process_buy_command(self, text: str, customer_phone: str, tenant: dict) -> Dict[str, str]:
        """Processes #buy or #order triggers and returns customer receipt + manager notification."""
        receipt_num = f"#TSX-{random.randint(10000, 99999)}"
        biz_name = tenant.get("business_name", "Teeslux Global Electronics & Solar")
        catalog = tenant.get("catalog", [])

        # Default item if not specified
        selected_item = catalog[1] if len(catalog) > 1 else catalog[0] if catalog else {
            "name": "1.5kVA Dual Solar Generator", "price": 185000.0
        }

        # Check if customer specified product in text (e.g. #buy 1 or #buy solar)
        q = text.lower()
        for item in catalog:
            if item.get("id") in q or item.get("name", "").lower() in q:
                selected_item = item
                break

        product_name = selected_item.get("name", "1.5kVA Dual Solar Generator")
        price = float(selected_item.get("price", 185000.0))

        customer_receipt = self.generate_receipt(
            receipt_id=receipt_num,
            business_name=biz_name,
            customer_phone=customer_phone,
            product_name=product_name,
            price=price
        )

        manager_alert = self.generate_manager_alert(
            receipt_id=receipt_num,
            business_name=biz_name,
            customer_phone=customer_phone,
            product_name=product_name,
            price=price
        )

        return {
            "receipt_id": receipt_num,
            "customer_reply": customer_receipt,
            "manager_alert": manager_alert,
            "manager_phone": tenant.get("manager_phone", "2348072015725")
        }


order_placement_engine = OrderPlacementEngine()
