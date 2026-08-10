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

    def generate_customer_order_handover(
        self,
        receipt_id: str,
        business_name: str,
        customer_phone: str,
        product_name: str,
        price: float,
        manager_phone: str
    ) -> str:
        """Formats an order handover card for the customer with zero loose ends."""
        return (
            f"🛍️ *[{business_name} — Order Inquiry Received]*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Thank you for your order request!\n\n"
            f"📦 *Item Selected:* *{product_name}*\n"
            f"💵 *Estimated Price:* ₦{price:,.2f}\n"
            f"🧾 *Reference ID:* `{receipt_id}`\n\n"
            f"📞 *Store Manager Connecting:* Our store manager (`+{manager_phone}`) is joining this chat right now to assist you directly with:\n"
            f"  • Quantity & Color selection\n"
            f"  • Custom specifications & Quality options\n"
            f"  • Exact delivery address & Payment details\n\n"
            f"💬 Please hold on for a moment while our manager replies!"
        )

    def generate_manager_sales_lead_alert(
        self,
        receipt_id: str,
        business_name: str,
        customer_phone: str,
        product_name: str,
        price: float
    ) -> str:
        """Formats an urgent hot sales lead alert for the store manager."""
        return (
            f"🚨 *[HOT SALES LEAD — ACTION REQUIRED]* 🚨\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🏪 *Store:* {business_name}\n"
            f"🧾 *Order Ref:* `{receipt_id}`\n"
            f"👤 *Customer:* `+{customer_phone}`\n"
            f"📦 *Interested In:* *{product_name}* (₦{price:,.2f})\n\n"
            f"⚡ *ACTION REQUIRED:* Please reply to customer `+{customer_phone}` directly to finalize quantity, color, quality specs, delivery address, and payment terms!"
        )

    def process_buy_command(self, text: str, customer_phone: str, tenant: dict) -> Dict[str, str]:
        """Processes #buy or #order triggers and returns customer handover + manager notification."""
        receipt_num = f"#TSX-{random.randint(10000, 99999)}"
        biz_name = tenant.get("business_name", "Teeslux Global Electronics & Solar")
        manager_phone = tenant.get("manager_phone", "2348072015725")
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

        customer_handover = self.generate_customer_order_handover(
            receipt_id=receipt_num,
            business_name=biz_name,
            customer_phone=customer_phone,
            product_name=product_name,
            price=price,
            manager_phone=manager_phone
        )

        manager_alert = self.generate_manager_sales_lead_alert(
            receipt_id=receipt_num,
            business_name=biz_name,
            customer_phone=customer_phone,
            product_name=product_name,
            price=price
        )

        return {
            "receipt_id": receipt_num,
            "customer_reply": customer_handover,
            "manager_alert": manager_alert,
            "manager_phone": manager_phone
        }


order_placement_engine = OrderPlacementEngine()
