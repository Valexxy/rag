from whatsapp_ui import format_currency

class NigerianMarketEngine:
    """Solves Informal Nigerian Market Pain Points: Gbese Debt Tracking & Local Dialect AI."""

    @staticmethod
    def record_customer_debt(customer_phone: str, amount: float, item: str, currency: str = "NGN") -> str:
        """Logs customer credit / Gbese record."""
        amount_str = format_currency(amount, currency)
        return f"""📋 *[CREDIT / GBESE RECORD LOGGED]*
---------------------------------------------
📱 *Customer:* `{customer_phone}`
📦 *Item:* {item}
💰 *Debt Balance:* {amount_str}
⚡ *Status:* `UNPAID / ON TRUST`

_Reply `#debt remind {customer_phone}` to send a polite automated WhatsApp payment reminder!_"""

    @staticmethod
    def format_polite_debt_reminder(business_name: str, customer_phone: str, amount: float, item: str, currency: str = "NGN") -> str:
        """Generates a polite WhatsApp payment reminder for credit customers."""
        amount_str = format_currency(amount, currency)
        return f"""🤝 *[GENTLE PAYMENT REMINDER FROM {business_name.upper()}]*
---------------------------------------------
Good day Chief!

This is a gentle reminder regarding your outstanding balance of *{amount_str}* for `*{item}*`.

🏦 *Bank Transfer Details:*
• *Bank:* Moniepoint MFB / GTBank
• *Account:* {business_name}
• *Account No:* 0252796240

Thank you for your continued patronage! 🙏"""

    @staticmethod
    def translate_to_pidgin(text: str) -> str:
        """Localizes standard customer service responses into Nigerian Pidgin."""
        pidgin_map = {
            "welcome": "How far boss! Welcome to our store.",
            "price": "the price dey cost",
            "bank details": "make you pay enter our account here:",
            "thank you": "We appreciate boss! Make your day smooth.",
            "human agent": "Abeg hold on, management dey come answer you now."
        }
        res = text
        for k, v in pidgin_map.items():
            res = res.replace(k, v)
        return res

nigerian_market = NigerianMarketEngine()
