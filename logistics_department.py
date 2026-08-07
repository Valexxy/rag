import random
import string
from datetime import datetime

class LogisticsDepartment:
    """World-Class Logistics & Supply Chain Management Engine."""

    @staticmethod
    def generate_waybill(tenant_id: str, customer_phone: str, delivery_address: str, items_summary: str) -> dict:
        """Generates a unique Waybill with OTP proof-of-delivery."""
        year = datetime.now().year
        rand_id = ''.join(random.choices(string.digits, k=4))
        waybill_number = f"WB-{year}-{rand_id}"
        otp_code = ''.join(random.choices(string.digits, k=4))

        return {
            "waybill_number": waybill_number,
            "tenant_id": tenant_id,
            "customer_phone": customer_phone,
            "delivery_address": delivery_address,
            "items_summary": items_summary,
            "otp_code": otp_code,
            "status": "DISPATCHED",
            "courier": "SaaS Dispatch Logistics",
            "created_at": datetime.now().isoformat()
        }

    @staticmethod
    def format_delivery_status(waybill: dict) -> str:
        """Formats clean WhatsApp delivery tracking card."""
        wb_num = waybill.get("waybill_number", "N/A")
        status = waybill.get("status", "IN_TRANSIT")
        courier = waybill.get("courier", "Standard Logistics")
        addr = waybill.get("delivery_address", "Destination Address")
        otp = waybill.get("otp_code", "****")

        return f"""🚚 *[WAYBILL LOGISTICS TRACKER]*
---------------------------------------------
📦 *Waybill No:* `{wb_num}`
📍 *Destination:* {addr}
🚚 *Carrier:* {courier}
⚡ *Status:* `{status}`
🔐 *Delivery OTP Code:* `{otp}` *(Give to rider upon arrival)*"""

logistics_dept = LogisticsDepartment()
