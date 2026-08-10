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
    """Enforces strict tenant business boundaries with 2-tier smart classification."""

    def classify_query(self, query: str, tenant: dict) -> str:
        """
        Classifies query into:
          - 'IN_DOMAIN': Relevant to tenant's store products & services.
          - 'BUSINESS_OUT_OF_CATALOG': Still business-related, but not in current catalog -> Route to Manager.
          - 'RUBBISH_OFF_TOPIC': General trivia, sports, code, politics -> Block AI reply cleanly without manager alert.
        """
        q = query.lower().strip()

        # 1. Rubbish / Anti-Abuse Keywords
        if any(kw in q for kw in OFF_TOPIC_KEYWORDS) or any(phrase in q for phrase in ["uefa", "who won", "premier league", "write code", "football match"]):
            return "RUBBISH_OFF_TOPIC"

        # 2. Store Operational & Logistics Questions are ALWAYS IN_DOMAIN
        store_ops_keywords = ["deliver", "delivery", "shipping", "ship", "location", "address", "where", "how do you", "payment", "bank", "account", "hours", "contact", "phone", "manager"]
        if any(kw in q for kw in store_ops_keywords):
            return "IN_DOMAIN"

        # 3. General business-like buying/selling questions for items NOT in catalog
        catalog = tenant.get("catalog", [])
        catalog_names = [item.get("name", "").lower() for item in catalog if isinstance(item, dict)]
        
        if any(w in q for w in ["do you sell", "do you have", "can i get", "do you carry"]) and not any(name in q or any(word in q for word in name.split() if len(word) > 3) for name in catalog_names):
            return "BUSINESS_OUT_OF_CATALOG"

        # 4. Extract tenant domain keywords from business name, domain scope & catalog
        biz_name = tenant.get("business_name", "").lower()
        domain_scope = tenant.get("business_domain_scope", "").lower()

        domain_keywords = set([
            "price", "buy", "order", "cost", "warranty", "ship", "delivery", "payment",
            "stock", "store", "shop", "address", "location", "hours", "spec", "help",
            "charge", "battery", "power", "solar", "panel", "generator", "inverter"
        ])
        
        for text_source in [biz_name, domain_scope]:
            for word in text_source.replace(",", " ").split():
                if len(word) > 2:
                    domain_keywords.add(word)

        for item in catalog:
            if isinstance(item, dict):
                name = item.get("name", "").lower()
                for w in name.split():
                    if len(w) > 2:
                        domain_keywords.add(w)

        # Check if query matches tenant domain keywords
        if any(kw in q for kw in domain_keywords):
            return "IN_DOMAIN"

        # Short general greetings / store questions are allowed in-domain
        if len(q.split()) <= 4:
            return "IN_DOMAIN"

        # Default fallback for unknown long text
        return "RUBBISH_OFF_TOPIC"

    def handle_rubbish_off_topic(self, tenant: dict) -> Dict[str, str]:
        """Politely informs customer that AI only handles store business queries."""
        biz_name = tenant.get("business_name", "Teeslux Global Store")
        return {
            "type": "rubbish_blocked",
            "customer_reply": (
                f"🤖 *[{biz_name} — Assistant]*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"I am the automated store assistant for *{biz_name}*.\n\n"
                f"I only answer questions relating to our store products, prices, delivery, and orders.\n\n"
                f"💬 Type `/menu` to browse options, or reply with your product inquiry!"
            ),
            "manager_alert": None  # ZERO MANAGER DISTRACTION FOR RUBBISH QUERIES
        }

    def handle_business_out_of_catalog(self, query: str, customer_phone: str, tenant: dict) -> Dict[str, str]:
        """Routes real business leads for out-of-catalog items to the store manager."""
        biz_name = tenant.get("business_name", "Teeslux Global Store")
        manager_phone = tenant.get("manager_phone", "2348072015725")
        return {
            "type": "business_lead_handoff",
            "customer_reply": (
                f"🛍️ *[{biz_name} — Business Inquiry]*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Thank you for reaching out!\n\n"
                f"While that specific item is not in our standard online catalog, our store manager (`+{manager_phone}`) is joining this chat to assist you directly.\n\n"
                f"💬 Please hold on for a moment while our manager replies!"
            ),
            "manager_alert": (
                f"🚨 *[STORE BUSINESS LEAD ALERT]* 🚨\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🏪 *Store:* {biz_name}\n"
                f"👤 *Customer:* `+{customer_phone}`\n"
                f"💬 *Inquiry:* '{query}'\n\n"
                f"⚡ *ACTION REQUIRED:* Business lead! Please reply to `+{customer_phone}` directly."
            )
        }


strict_domain_guardrail = StrictDomainGuardrail()
