"""
====================================================================
RICH WHATSAPP UI FORMATTER & CAROUSEL CARD ENGINE (v2030)
====================================================================
Generates visually stunning, ground-breaking WhatsApp Markdown UI Cards:
- Product Detail Cards
- Disambiguation Carousels
- High-Priority Manager Handover Cards
- Order Tracking Cards
- Payment & Bank Transfer Cards
- Store Operations & FAQ Cards
"""

from typing import Dict, List, Any


class WhatsAppUIFormatter:
    """Ground-breaking WhatsApp UI Card Formatter Engine."""

    @staticmethod
    def format_product_card(item: Dict[str, Any], biz_name: str = "Teeslux Global Electronics & Solar") -> str:
        name = item.get("name", "Product")
        price = item.get("price", 0)
        desc = item.get("desc") or item.get("description") or "High quality item"
        status = item.get("status", "In Stock")

        return (
            f"🛍️ *[{biz_name} — Product Specification]*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✅ *Product:* `{name}`\n"
            f"💰 *Price:* `₦{price:,.0f}.00` *(Fixed Rate)*\n"
            f"📦 *Availability:* `{status}`\n"
            f"📝 *Description:* {desc}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💬 *Quick Actions:*\n"
            f"• Reply `1` or `#buy` to place an instant order\n"
            f"• Reply `#human` to speak with our Store Manager"
        )

    @staticmethod
    def format_disambiguation_carousel(options: List[Dict[str, Any]], category: str, biz_name: str = "Teeslux Global Store") -> str:
        lines = []
        icons = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        for i, opt in enumerate(options[:5]):
            icon = icons[i] if i < len(icons) else f"{i+1}️⃣"
            price = opt.get("price", 0)
            lines.append(f"{icon} *{opt.get('name')}*\n   └ 💰 Price: `₦{price:,.0f}.00`")

        opts_text = "\n\n".join(lines)
        cat_title = category.upper()

        return (
            f"🤔 *[{biz_name} — {cat_title} Options Available]*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"I found multiple top-quality items matching *'{category}'*:\n\n"
            f"{opts_text}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💬 *Reply with 1, 2, or 3* to inspect full specs & order!"
        )

    @staticmethod
    def format_manager_handover(query: str, biz_name: str = "Teeslux Global Store", owner_phone: str = "2348072015725") -> str:
        return (
            f"🚨 *[{biz_name} — High-Priority Executive Transfer]*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Thank you for your inquiry regarding:\n"
            f"❓ *'{query}'*\n\n"
            f"⚡ *Status:* Transferred to Store Manager on **HIGHEST PRIORITY**\n"
            f"⏱️ *Response Time:* Manager will reply directly to your chat shortly!\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📞 *Direct Escalation:* Call/WhatsApp `+{owner_phone}`"
        )

    @staticmethod
    def format_payment_card(biz_name: str = "Teeslux Global Store", owner_phone: str = "2348072015725") -> str:
        return (
            f"💳 *[{biz_name} — Payment & Bank Transfer Details]*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"We accept all verified payment methods:\n\n"
            f"🏦 *Bank Account:* `GTBank / First Bank`\n"
            f"💵 *Cash:* Accepted on delivery or in-store\n"
            f"💳 *POS Terminal:* Available at Onitsha Main Market Depot\n"
            f"📱 *USSD:* `*737#` (GTB) | `*894#` (FirstBank)\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💬 Reply `#buy` to generate invoice or `#human` for assistance!"
        )

    @staticmethod
    def format_delivery_card(biz_name: str = "Teeslux Global Store") -> str:
        return (
            f"🚚 *[{biz_name} — Delivery & Shipping Network]*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"We deliver nationwide across Nigeria 🇳🇬\n\n"
            f"📍 *Onitsha & Anambra State:* Same-Day Delivery (`₦500 – ₦2,000`)\n"
            f"✈️ *Lagos, Abuja, PH, Enugu:* 24–48 Hours via ABC / GIG Logistics\n"
            f"📦 *Nationwide (Any State):* 2–4 Business Days\n\n"
            f"🔐 *Verification:* Every delivery includes an OTP verification code!\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💬 Reply `#3` to track order or `#human` for custom logistics!"
        )


whatsapp_ui = WhatsAppUIFormatter()
