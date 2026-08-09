"""
====================================================================
CROSS-TENANT DISCOVERY & STORE SWITCHING ENGINE (v2030)
====================================================================
Prevents cross-store confusion when multiple businesses share 1 WhatsApp number:
1. Auto-Reset Session: Inactive sessions (> 4 hours) reset to IDLE store chooser.
2. Cross-Tenant Index Scan: If query fails in active store, scans all tenant catalogs.
   If found in another store, offers seamless 1-click store switching.
3. Explicit Commands: #store, #switch, menu, change store instantly opens Store Chooser.
"""

from typing import Dict, Any, List, Optional
from whatsapp_ui import whatsapp_ui


class StoreSwitchingEngine:
    """Zero-Confusion Multi-Tenant Store Router."""

    def __init__(self):
        # remoteJid -> {"tenant_id": str, "instance_name": str, "last_active": timestamp}
        self._user_store_context: Dict[str, Dict[str, Any]] = {}

    def get_user_store(self, remote_jid: str) -> Optional[Dict[str, Any]]:
        clean_jid = str(remote_jid).lower().strip()
        ctx = self._user_store_context.get(clean_jid)
        if not ctx:
            return None

        # 4-hour session timeout auto-reset
        import time
        if time.time() - ctx.get("last_active", 0) > 14400: # 4 hours
            del self._user_store_context[clean_jid]
            return None

        ctx["last_active"] = time.time()
        return ctx

    def set_user_store(self, remote_jid: str, instance_name: str, tenant_data: Dict[str, Any]):
        import time
        clean_jid = str(remote_jid).lower().strip()
        self._user_store_context[clean_jid] = {
            "instance_name": instance_name,
            "tenant_data": tenant_data,
            "last_active": time.time()
        }

    def format_store_chooser_menu(self, tenants: List[Dict[str, Any]]) -> str:
        lines = []
        icons = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        for i, t in enumerate(tenants[:5]):
            icon = icons[i] if i < len(icons) else f"{i+1}️⃣"
            biz = t.get("business_name", "Store")
            niche = t.get("niche", "retail").capitalize()
            lines.append(f"{icon} *{biz}* `({niche})`")

        stores_text = "\n".join(lines)

        return (
            f"🏢 *[Sovereign Global Multi-Store Hub]*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Welcome! Which store would you like to shop with today?\n\n"
            f"{stores_text}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💬 Reply 1, 2, 3, or 4 to enter store!\n"
            f"💡 Reply `#switch` anytime to change stores."
        )

    def check_cross_tenant_match(self, query: str, all_tenant_catalogs: Dict[str, list]) -> Optional[Dict[str, Any]]:
        """
        Scans all store catalogs if query failed in current store.
        If found in another store, returns recommendation to switch!
        """
        q = query.lower().strip()
        for instance_name, catalog in all_tenant_catalogs.items():
            for item in catalog:
                if not isinstance(item, dict):
                    continue
                name = (item.get("name") or "").lower()
                if any(word in name for word in q.split() if len(word) >= 3):
                    return {
                        "matched_instance": instance_name,
                        "item_name": item.get("name"),
                        "price": item.get("price")
                    }
        return None


store_router = StoreSwitchingEngine()
