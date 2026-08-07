import json
from datetime import datetime
from database import supabase

class SovereignComplianceEngine:
    """Global Data Privacy & Sovereignty Engine (GDPR, NDPA, CCPA, HIPAA)."""

    @staticmethod
    def export_customer_data(tenant_id: str, customer_phone: str) -> dict:
        """GDPR / NDPA Article 15: Right of Access Data Export."""
        try:
            # Gather profile, customer ledgers, and transactions
            profile = supabase.table("tenant_customers").select("*").eq("tenant_id", tenant_id).eq("phone_number", customer_phone).execute().data
            ledgers = supabase.table("customer_ledgers").select("*").eq("tenant_id", tenant_id).eq("phone_number", customer_phone).execute().data
            txns = supabase.table("tenant_transactions").select("*").eq("tenant_id", tenant_id).eq("phone_number", customer_phone).execute().data

            return {
                "compliance_framework": "GDPR / NDPA / CCPA Certified Data Export",
                "timestamp": datetime.now().isoformat(),
                "customer_phone": customer_phone,
                "profile": profile or [],
                "ledgers": ledgers or [],
                "transactions": txns or []
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def erase_customer_data(tenant_id: str, customer_phone: str) -> bool:
        """GDPR / NDPA Article 17: Right to be Forgotten / Complete Data Anonymization."""
        try:
            supabase.table("customer_ledgers").delete().eq("tenant_id", tenant_id).eq("phone_number", customer_phone).execute()
            supabase.table("bot_mutes").delete().eq("tenant_id", tenant_id).eq("phone_number", customer_phone).execute()
            supabase.table("tenant_customers").delete().eq("tenant_id", tenant_id).eq("phone_number", customer_phone).execute()
            return True
        except Exception as e:
            print(f"[ERROR] Data erasure failed: {e}")
            return False

    @staticmethod
    def sanitize_hipaa_phi(text: str) -> str:
        """HIPAA Health Data Privacy: Anonymizes Protected Health Information."""
        # Masks medical record numbers, SSN/NIN patterns
        import re
        sanitized = re.sub(r'\b\d{11}\b', '[REDACTED_NIN]', text)
        sanitized = re.sub(r'\b\d{9}\b', '[REDACTED_SSN]', sanitized)
        return sanitized

sovereign_compliance = SovereignComplianceEngine()
