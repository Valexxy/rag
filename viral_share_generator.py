import random
from datetime import datetime

class ViralShareGeneratorEngine:
    """Gen Z & Entrepreneur Viral Status Card Generator Engine."""

    GENZ_SLANG_CAPTIONS = [
        "🔥 No cap! My store is running 100% on AI autopilot while I sleep!",
        "⚡ Stop stressing in Lagos/Onitsha market traffic! Query live market prices in 0.1s!",
        "💎 Main character energy! Secured top wholesale prices from China to Nigeria without leaving my house!"
    ]

    def generate_trader_flex_card(self, business_name: str, city: str = "Lagos") -> str:
        """Generates a high-aesthetic Gen Z flex status card traders love posting on Instagram/WhatsApp."""
        caption = random.choice(self.GENZ_SLANG_CAPTIONS)
        date_str = datetime.now().strftime("%d %b %Y")

        return f"""🏆 *[OFFICIAL TRADER FLEX CARD]*
📅 _{date_str}_
---------------------------------------------
🏬 *Merchant:* {business_name}
📍 *Location Hub:* {city}
⚡ *Autopilot Status:* `100% AI DRIVEN`
🚗 *Market Traffic Saved Today:* `3.5 Hours Saved`
💰 *Transport Cost Saved:* `₦5,000.00`

💬 _{caption}_

---------------------------------------------
📲 *Share on WhatsApp Status & Instagram to show your business is operating on 2030 Sovereign AI!*"""

    def generate_daily_savings_infographic(self, customer_phone: str) -> str:
        """Generates a viral savings card proving why using the bot beats going to the market daily."""
        clean_p = "".join(filter(str.isdigit, str(customer_phone)))

        return f"""💸 *[MY DAILY MARKET SAVINGS REPORT]*
---------------------------------------------
📱 *Trader:* `+{clean_p}`
⛽ *Transport/Fuel Cost Saved:* ₦4,500.00
⏳ *Market Traffic Time Saved:* 3 Hours 20 Mins
📦 *Wholesale Deal Secured:* Saved ₦3,500.00 on Spot Price

---------------------------------------------
💡 *Why go to the market daily when you can check live market prices & waybill delivery from your phone?*

👉 *Query Live Prices:* Type `#market-price solar Onitsha`"""

viral_share_gen = ViralShareGeneratorEngine()
