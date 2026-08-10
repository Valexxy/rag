"""
====================================================================
STRICT TENANT DOMAIN GUARDRAIL & ANTI-ABUSE ENGINE (v2026 - REFACTORED)
====================================================================
Enforces business boundary scoping per merchant tenant:
  1. ONLY blocks explicit spam, programming, general trivia, and politics.
  2. Routes out-of-catalog product requests (e.g. "Do you sell cloths", "Do you sell cars") to Sourcing Lead Engine.
  3. ALWAYS allows all store inquiries, delivery questions, city locations, product questions, specs, and prices IN_DOMAIN for AI reasoning.
"""

import logging
from typing import Dict

logger = logging.getLogger("StrictDomainGuardrail")

EXPLICIT_SPAM_KEYWORDS = [
    "write code", "python code", "javascript code", "html code", "css code",
    "sql query", "write an essay", "write a poem", "write a story", "tell me a joke",
    "who won uefa", "who won champion", "who won premier league", "who is the president",
    "tell me about politics", "crypto price prediction", "bitcoin forecast"
]

class StrictDomainGuardrail:
    """Refactored Domain Guardrail — Zero False Positives for Business Queries."""

    def classify_query(self, query: str, tenant: dict) -> str:
        q = query.lower().strip()

        # 1. ONLY block explicit spam / programming / general trivia / politics
        if any(kw in q for kw in EXPLICIT_SPAM_KEYWORDS):
            return "RUBBISH_OFF_TOPIC"

        # 2. Store Operational, Logistics, Cities & General Buying Questions are ALWAYS IN_DOMAIN
        store_ops_keywords = [
            "deliver", "delivery", "shipping", "ship", "send", "waybill", "transport",
            "ibadan", "lagos", "abuja", "kano", "port harcourt", "enugu", "benin", "delta",
            "calabar", "owerri", "jos", "kaduna", "sokoto", "asaba", "warri", "location",
            "address", "where", "how do you", "payment", "bank", "account", "hours", "contact",
            "phone", "manager", "package", "packaging", "warranty", "price", "cost", "how much"
        ]
        if any(kw in q for kw in store_ops_keywords):
            return "IN_DOMAIN"

        # 3. Check for out-of-catalog product requests (e.g. "Do you sell cloths")
        catalog = tenant.get("catalog", [])
        catalog_names = [item.get("name", "").lower() for item in catalog if isinstance(item, dict)]
        domain_scope = tenant.get("business_domain_scope", "").lower()

        if any(phrase in q for phrase in ["do you sell", "do you have", "can i buy", "do you supply", "can you supply"]):
            matches_domain = any(word in q for word in domain_scope.replace(",", " ").split() if len(word) > 3)
            matches_catalog = any(name in q or any(word in q for word in name.split() if len(word) > 3) for name in catalog_names)
            if not matches_domain and not matches_catalog:
                return "BUSINESS_OUT_OF_CATALOG"

        # 4. DEFAULT: ALL OTHER BUSINESS & STORE INQUIRIES ARE IN_DOMAIN!
        return "IN_DOMAIN"

    def handle_rubbish_off_topic(self, tenant: dict) -> Dict[str, str]:
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
            "manager_alert": None
        }

    def handle_business_out_of_catalog(self, query: str, customer_phone: str, tenant: dict) -> Dict[str, str]:
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
