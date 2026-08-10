"""
====================================================================
DYNAMIC PROFORMA INVOICE & QUOTATION GENERATOR (v2026)
====================================================================
Generates professional WhatsApp Proforma Invoice / Quotation Cards
when customers request price quotes for custom order packages!
"""

import random
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("QuoteGeneratorEngine")

class QuoteGeneratorEngine:
    """Generates instant WhatsApp Proforma Invoice & Quotation Cards."""

    def generate_quotation(self, query: str, customer_phone: str, tenant: dict) -> Dict[str, str]:
        """Generates an instant formal Proforma Invoice card."""
        biz_name = tenant.get("business_name", "Teeslux Global Store")
        manager_phone = tenant.get("manager_phone", "2348072015725")
        address = tenant.get("store_address", "Onitsha Main Market, Anambra State, Nigeria")
        quote_ref = f"#QT-{random.randint(10000, 99999)}"

        catalog = tenant.get("catalog", [])
        item_lines = []
        total_price = 0.0

        for idx, item in enumerate(catalog[:3], 1):
            if isinstance(item, dict):
                p = float(item.get("price", 0))
                item_lines.append(f"{idx}️⃣ *{item.get('name', 'Item')}* — ₦{p:,.2f}")
                total_price += p

        if not item_lines:
            item_lines.append("1️⃣ *Standard Solar & Electronics Supply Package* — ₦185,000.00")
            total_price = 185000.0

        quote_card = (
            f"📄 *[{biz_name} — OFFICIAL PROFORMA QUOTATION]*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🧾 *Quote Ref:* `{quote_ref}`\n"
            f"👤 *Prepared For:* `+{customer_phone}`\n"
            f"📍 *Store Address:* `{address}`\n\n"
            f"📦 *Itemized Quote Summary:*\n"
            + "\n".join(item_lines) + "\n\n"
            f"💵 *Estimated Total:* ₦{total_price:,.2f}\n"
            f"🚚 *Delivery Terms:* Same-Day Local / 24–48 Hours Waybill\n\n"
            f"📞 Our Store Director (`+{manager_phone}`) is standing by to confirm custom discounts and payment terms!"
        )

        manager_alert = (
            f"📄 *[NEW QUOTATION REQUESTED — {quote_ref}]* 📄\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🏪 *Store:* {biz_name}\n"
            f"👤 *Customer:* `+{customer_phone}`\n"
            f"💵 *Estimated Quote Value:* ₦{total_price:,.2f}\n\n"
            f"⚡ *ACTION REQUIRED:* Please contact customer `+{customer_phone}` to finalize invoice terms!"
        )

        return {
            "type": "formal_quotation",
            "customer_reply": quote_card,
            "manager_alert": manager_alert
        }


quote_generator_engine = QuoteGeneratorEngine()
