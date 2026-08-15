"""
====================================================================
SECURITY FORTRESS v2026
====================================================================
- HMAC SHA-512 Paystack Webhook Verification
- HMAC SHA-256 Monnify Webhook Verification
- HMAC SHA-256 Meta WhatsApp Webhook Verification
- VOIP / Disposable Phone Number Risk Scoring
- Anti-Account-Diversion Lock
====================================================================
"""

import hashlib
import hmac
import logging
import re

logger = logging.getLogger("SecurityFortress")


class SecurityFortress:

    # ── PAYSTACK HMAC SHA-512 ─────────────────────────────────────────────
    @staticmethod
    def verify_paystack_signature(payload_bytes: bytes, signature_header: str, secret_key: str) -> bool:
        """Validates Paystack X-Paystack-Signature header using HMAC SHA-512."""
        try:
            expected = hmac.new(
                secret_key.encode("utf-8"),
                payload_bytes,
                hashlib.sha512
            ).hexdigest()
            return hmac.compare_digest(expected, signature_header.strip())
        except Exception as e:
            logger.error(f"[SecurityFortress] Paystack HMAC failed: {e}")
            return False

    # ── MONNIFY HMAC SHA-256 ──────────────────────────────────────────────
    @staticmethod
    def verify_monnify_signature(payload_str: str, signature_header: str, secret_key: str) -> bool:
        """Validates Monnify monnify-signature header using HMAC SHA-256."""
        try:
            expected = hmac.new(
                secret_key.encode("utf-8"),
                payload_str.encode("utf-8"),
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(expected, signature_header.strip())
        except Exception as e:
            logger.error(f"[SecurityFortress] Monnify HMAC failed: {e}")
            return False

    # ── META WHATSAPP HMAC SHA-256 ────────────────────────────────────────
    @staticmethod
    def verify_meta_signature(payload_bytes: bytes, signature_header: str, app_secret: str) -> bool:
        """Validates Meta X-Hub-Signature-256 header using HMAC SHA-256."""
        try:
            sig = signature_header.replace("sha256=", "").strip()
            expected = hmac.new(
                app_secret.encode("utf-8"),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(expected, sig)
        except Exception as e:
            logger.error(f"[SecurityFortress] Meta HMAC failed: {e}")
            return False

    # ── VOIP / DISPOSABLE NUMBER RISK SCORE ──────────────────────────────
    @staticmethod
    def score_phone_risk(phone: str) -> dict:
        """
        Assigns a risk score to a WhatsApp phone number.
        Nigerian numbers (+234) are LOW risk.
        +1 / +44 VOIP / non-African numbers are HIGH risk — flag for manager audit.
        """
        phone = str(phone).strip().replace("+", "")

        # African country codes — LOW RISK
        african_prefixes = [
            "234",  # Nigeria
            "233",  # Ghana
            "254",  # Kenya
            "256",  # Uganda
            "255",  # Tanzania
            "251",  # Ethiopia
            "27",   # South Africa
            "225",  # Ivory Coast
            "221",  # Senegal
            "237",  # Cameroon
        ]

        for prefix in african_prefixes:
            if phone.startswith(prefix):
                return {"risk": "LOW", "flag_manager": False, "reason": "Verified African number"}

        # VOIP / Non-African numbers — HIGH RISK
        high_risk_prefixes = ["1", "44", "91", "86", "7"]  # US, UK, India, China, Russia
        for prefix in high_risk_prefixes:
            if phone.startswith(prefix):
                return {
                    "risk": "HIGH",
                    "flag_manager": True,
                    "reason": f"Non-African VOIP/virtual number detected (+{prefix}...). Manager verification required before dispatch."
                }

        return {"risk": "MEDIUM", "flag_manager": True, "reason": "Unknown country code — manager audit recommended"}

    # ── ANTI-ACCOUNT-DIVERSION LOCK ───────────────────────────────────────
    @staticmethod
    def detect_account_diversion_attempt(query: str) -> bool:
        """
        Detects if a customer is attempting to divert payment to a personal account.
        Returns True if diversion attempt is detected.
        """
        diversion_phrases = [
            "another account", "your account number", "send to my account",
            "different account", "personal account", "give me your account",
            "transfer to", "change the account", "new account number",
            "pay directly", "pay to you", "your bank details",
        ]
        q = query.lower()
        return any(phrase in q for phrase in diversion_phrases)

    @staticmethod
    def anti_diversion_response(manager_phone: str) -> str:
        return (
            "🔒 *Security Notice:* For your protection and to prevent fraud, all payments "
            "are made exclusively to the official store virtual account generated at checkout. "
            "Our store manager cannot and will not provide alternative personal bank accounts.\n\n"
            f"📞 If you have payment concerns, contact our Store Manager directly: +{manager_phone}"
        )


security_fortress = SecurityFortress()
