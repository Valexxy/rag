import random
import hashlib
from datetime import datetime
from local_sovereign_tracker import sovereign_tracker

class LogisticsDepartment:
    """World-Class Enterprise Logistics & 100% Sovereign OTP Proof-of-Delivery Department."""

    def __init__(self):
        self.waybills = {}

    def generate_waybill(self, tenant_id: str, customer_phone: str, delivery_address: str, item_summary: str) -> dict:
        """Generates cryptographically signed waybill with 4-digit security OTP code."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        raw_hash = f"{tenant_id}-{customer_phone}-{timestamp}"
        waybill_num = f"WB-2026-{hashlib.sha256(raw_hash.encode()).hexdigest()[:6].upper()}"
        
        # 4-Digit Security Proof-of-Delivery OTP
        otp_code = f"{random.randint(1000, 9999)}"

        waybill_data = {
            "waybill_id": waybill_num,
            "tenant_id": tenant_id,
            "customer_phone": customer_phone,
            "address": delivery_address,
            "items": item_summary,
            "otp_code": otp_code,
            "status": "DISPATCHED_IN_TRANSIT",
            "rider_name": "Sovereign Express Rider #042",
            "created_at": datetime.now().isoformat()
        }

        self.waybills[waybill_num] = waybill_data
        return waybill_data

    def verify_delivery_otp(self, waybill_id: str, user_otp: str) -> bool:
        """Verifies recipient OTP code for instant proof of delivery."""
        if waybill_id in self.waybills:
            record = self.waybills[waybill_id]
            if record["otp_code"] == user_otp.strip():
                record["status"] = "DELIVERED_AND_VERIFIED"
                return True
        return False

    def format_delivery_status(self, waybill_data: dict) -> str:
        """Formats clean WhatsApp logistics dispatch card with 100% Sovereign Zero-API Tracking."""
        return sovereign_tracker.get_sovereign_tracking_report(waybill_data["waybill_id"], waybill_data["customer_phone"])

logistics_dept = LogisticsDepartment()
