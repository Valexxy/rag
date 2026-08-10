"""
====================================================================
STRICT TENANT DOMAIN GUARDRAIL & ANTI-ABUSE ENGINE (v2026)
====================================================================
Enforces 100% strict business boundary scoping per merchant tenant:
  1. Prevents AI abuse (rejects coding, general trivia, politics, creative writing)
  2. Ensures AI token usage is 100% focused on tenant's store catalog & services
  3. Instantly routes all out-of-domain queries to human store manager
"""

import re
import logging
from typing import Dict, Optional

logger = logging.getLogger("StrictDomainGuardrail")

# Forbidden General Off-Topic Keywords (Anti-Abuse)
OFF_TOPIC_KEYWORDS = [
    "write code", "python", "javascript", "html", "css", "sql", "script",
    "essay", "poem", "story", "joke", "song", "lyrics", "homework",
    "president", "election", "politics", "football", "premier league",
    "champion", "who is", "tell me a story", "crypto", "bitcoin", "solana"
]

class StrictDomainGuardrail:
    """Enforces strict tenant business boundaries and routes out-of-domain queries to human manager."""

    def is_query_in_tenant_domain(self, query: str, tenant: dict) -> bool:
        """Determines whether a query is relevant to the tenant's business domain."""
        q = query.lower().strip()

        # 1. Anti-Abuse Check: Reject obvious general off-topic keywords
        if any(kw in q for kw in OFF_TOPIC_KEYWORDS):
            logger.warning(f"[DomainGuardrail] Off-topic query rejected: '{query}'")
            return False

        # 2. Extract tenant domain keywords from business name & catalog
        biz_name = tenant.get("business_name", "").lower()
        catalog = tenant.get("catalog", [])

        domain_keywords = set(["price", "buy", "order", "cost", "warranty", "ship", "delivery", "payment", "stock", "store", "shop", "address", "location", "hours", "spec", "help"])
        
        for word in biz_name.split():
            if len(word) > 2:
                domain_keywords.add(word)

        for item in catalog:
            if isinstance(item, dict):
                name = item.get("name", "").lower()
                for w in name.split():
                    if len(w) > 2:
                        domain_keywords.add(w)
                keywords = item.get("keywords", [])
                if isinstance(keywords, list):
                    for kw in keywords:
                        domain_keywords.add(str(kw).lower())

        # Check if query matches tenant domain keywords
        if any(kw in q for kw in domain_keywords):
            return True

        # Short general greetings / store questions are allowed
        if len(q.split()) <= 4:
            return True

        return False

    def handle_out_of_domain(self, query: str, customer_phone: str, tenant: dict) -> Dict[str, str]:
        """Generates polite out-of-domain response and triggers human manager handoff."""
        biz_name = tenant.get("business_name", "Teeslux Global Store")
        manager_phone = tenant.get("manager_phone", "2348072015725")

        return {
            "type": "out_of_domain_handoff",
            "customer_reply": (
                f"🤖 *[{biz_name} — Assistant]*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"I am specialized specifically to assist with *{biz_name}* products, pricing, and orders.\n\n"
                f"📞 *Connecting Store Manager:* Your inquiry has been routed directly to our store manager (`+{manager_phone}`) for personal assistance.\n\n"
                f"💬 Our manager will reply to you shortly!"
            ),
            "manager_alert": (
                f"🚨 *[OUT-OF-DOMAIN INQUIRY — MANAGER ROUTED]* 🚨\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🏪 *Store:* {biz_name}\n"
                f"👤 *Customer:* `+{customer_phone}`\n"
                f"💬 *Query:* '{query}'\n\n"
                f"⚡ *ACTION REQUIRED:* Out-of-scope inquiry! Please reply to customer `+{customer_phone}` directly."
            )
        }


strict_domain_guardrail = StrictDomainGuardrail()
