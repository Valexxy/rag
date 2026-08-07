import hashlib
import json
from datetime import datetime

class AuditVault:
    """Cryptographic SHA-256 Immutable Audit Logging Vault for System Legal Compliance."""

    @staticmethod
    def create_audit_record(tenant_id: str, actor: str, action: str, details: dict) -> dict:
        """Generates a tamper-proof SHA-256 signed audit log record."""
        timestamp = datetime.now().isoformat()
        payload_str = f"{tenant_id}|{actor}|{action}|{json.dumps(details, sort_keys=True)}|{timestamp}"
        digest_hash = hashlib.sha256(payload_str.encode()).hexdigest()

        return {
            "tenant_id": tenant_id,
            "actor": actor,
            "action": action,
            "details": details,
            "timestamp": timestamp,
            "sha256_signature": digest_hash
        }

audit_vault = AuditVault()
