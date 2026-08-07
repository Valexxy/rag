import os
import json
from datetime import datetime
from database import supabase

class DatabaseBackupEngine:
    """Automated Multi-Tenant Database Backup & Snapshot Engine."""

    @staticmethod
    def create_database_snapshot(backup_dir: str = "backups") -> str:
        """Exports database records to local JSON snapshot file."""
        os.makedirs(backup_dir, exist_ok=True)
        filename = f"{backup_dir}/snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            tenants = supabase.table("tenants").select("*").execute().data or []
            entities = supabase.table("tenant_entities").select("*").execute().data or []
            customers = supabase.table("tenant_customers").select("*").execute().data or []
            txns = supabase.table("tenant_transactions").select("*").execute().data or []

            backup_payload = {
                "timestamp": datetime.now().isoformat(),
                "counts": {
                    "tenants": len(tenants),
                    "entities": len(entities),
                    "customers": len(customers),
                    "transactions": len(txns)
                },
                "tenants": tenants,
                "entities": entities,
                "customers": customers,
                "transactions": txns
            }

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(backup_payload, f, indent=2)

            print(f"[BACKUP SUCCESS] Created database snapshot at {filename}")
            return filename
        except Exception as e:
            print(f"[BACKUP ERROR] Snapshot creation failed: {e}")
            return ""

backup_engine = DatabaseBackupEngine()
