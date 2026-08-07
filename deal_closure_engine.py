from datetime import datetime
from whatsapp_ui import format_currency

class DealClosureEngine:
    """Zero-Customer-Loss Sales Pipeline & Closed Deal Receipt Generator."""

    @staticmethod
    def generate_closed_deal_receipt(tenant: dict, customer_phone: str, item_name: str, amount: float, reference: str) -> str:
        """Generates an official Certificate of Purchase / Digital WhatsApp Receipt."""
        b_name = tenant.get("business_name", "Valexxy Global Store")
        currency = tenant.get("currency", "NGN")
        amount_str = format_currency(amount, currency)
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M UTC")

        return f"""🧾 *[CERTIFICATE OF PURCHASE - OFFICIAL RECEIPT]*
---------------------------------------------
🏢 *Merchant:* {b_name}
📱 *Customer:* {customer_phone}
📦 *Item/Service:* {item_name}
💰 *Amount Paid:* {amount_str}
🏷️ *Txn Reference:* `{reference}`
📅 *Date:* {date_str}
⚡ *Status:* `CLOSED & SETTLED`

Thank you for your business! Your order is being processed by our logistics department."""

deal_closure = DealClosureEngine()
