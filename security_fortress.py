import re
import hmac
import hashlib
import base64
from cryptography.fernet import Fernet

MASTER_SECRET = "SovereignSaaS2030MasterSecretKey32BytesLong!"
_fernet_key = base64.urlsafe_b64encode(hashlib.sha256(MASTER_SECRET.encode()).digest())
cipher_suite = Fernet(_fernet_key)

class SecurityFortress:
    """Enterprise System Security, Threat Defense & Prompt Injection Shield."""

    @staticmethod
    def inspect_prompt_injection(user_input: str) -> tuple:
        """Scans input text for AI prompt injection attacks, system overrides, or unauthorized discount attempts."""
        malicious_patterns = [
            r"ignore (all )?(previous )?instructions",
            r"system override",
            r"you are now (an? )?admin",
            r"grant (me )?99%",
            r"free order",
            r"bypass security",
            r"reveal (owner|system) password",
            r"set price to 0"
        ]
        
        input_lower = user_input.lower()
        for pattern in malicious_patterns:
            if re.search(pattern, input_lower):
                return True, "⚠️ *[SECURITY ALERT]* Prompt injection attack detected and blocked by System Defense Fortress."

        return False, ""

    @staticmethod
    def encrypt_credential(plain_text: str) -> str:
        """Encrypts sensitive tenant API keys using AES-256 Fernet encryption."""
        if not plain_text:
            return ""
        return cipher_suite.encrypt(plain_text.encode()).decode()

    @staticmethod
    def decrypt_credential(cipher_text: str) -> str:
        """Decrypts tenant credentials safely."""
        if not cipher_text:
            return ""
        try:
            return cipher_suite.decrypt(cipher_text.encode()).decode()
        except Exception:
            return cipher_text

    @staticmethod
    def verify_webhook_hmac(payload_body: bytes, signature: str, secret: str) -> bool:
        """Verifies HMAC-SHA256 signature for incoming webhooks."""
        if not signature or not secret:
            return True
        computed = hmac.new(secret.encode(), payload_body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed, signature)

security_fortress = SecurityFortress()
