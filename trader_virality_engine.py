import random
from datetime import datetime

class TraderViralityEngine:
    """Viral Word-of-Mouth Engagement Engine for Nigerian Informal Markets."""

    TRADER_NUGGETS = [
        "💡 *NIGERIAN TRADER MORNING NUGGET:* Customer relationship is better than 1-day profit. Treat every customer like royalty today and watch your business double!",
        "🚀 *BUSINESS WISDOM:* Fast delivery + honest pricing = lifetime loyal customers. May your store experience massive sales and zero debt today!",
        "⚡ *MARKET INSIGHT:* In business, credit is good but cash is king! Keep your debt book updated and follow up politely with your debtors today."
    ]

    def get_daily_morning_nugget(self) -> str:
        """Returns viral morning business wisdom card traders love posting on WhatsApp Status."""
        nugget = random.choice(self.TRADER_NUGGETS)
        date_str = datetime.now().strftime("%A, %B %d, %Y")

        return f"""✨ *[DAILY TRADER BUSINESS NUGGET]*
📅 _{date_str}_
---------------------------------------------
{nugget}

---------------------------------------------
📲 *Share on WhatsApp Status to inspire fellow market traders today!*"""

    def generate_escrow_trust_badge(self, buyer_phone: str, seller_name: str, amount: float) -> str:
        """Generates 100% Escrow Guarantee Card building instant trust between inter-state buyers & sellers."""
        return f"""🛡️ *[100% ESCROW TRUST GUARANTEE]*
---------------------------------------------
🏢 *Merchant:* {seller_name}
📱 *Buyer:* `{buyer_phone}`
💰 *Order Value:* ₦{amount:,.2f}
🔐 *Escrow Protection:* `ACTIVE & GUARANTEED`

This transaction is protected by our Sovereign Escrow Guarantee. Funds are held safely until buyer confirms receipt of waybill package!"""

trader_virality = TraderViralityEngine()
