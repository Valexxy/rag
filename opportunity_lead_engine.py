"""
====================================================================
AUTONOMOUS SOURCING & OPPORTUNITY DOOR-OPENER ENGINE (v2026 - ENHANCED)
====================================================================
Transforms every customer query for non-catalog products, market errands,
or custom assistance requests into a HIGH-VALUE BUSINESS OPPORTUNITY!
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger("OpportunityLeadEngine")

class OpportunityLeadEngine:
    """Detects sourcing & custom market assistance requests to connect customer directly to manager."""

    def evaluate_opportunity(self, query: str, customer_phone: str, tenant: dict) -> Optional[Dict[str, str]]:
        q = query.lower().strip()
        biz_name = tenant.get("business_name", "Teeslux Global Store")
        manager_phone = tenant.get("manager_phone", "2348072015725")

        # 1. Custom Market Errand & Assistance Triggers
        assistance_triggers = [
            "still help me", "can still help", "since you are in", "since you are in main market",
            "can you help me check", "can you help me buy", "help me find", "check wrapper", "help me check"
        ]

        if any(trig in q for trig in assistance_triggers):
            return {
                "type": "market_assistance_opportunity",
                "customer_reply": (
                    f"🤝 *[{biz_name} — Smart Market Assistance]*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Since you need special assistance in the market, let me connect you directly to our Store Manager (`+{manager_phone}`) to see if we can help you get this done!\n\n"
                    f"📞 Our Store Manager is joining this chat right now to assist you personally!"
                ),
                "manager_alert": (
                    f"💰 *[SPECIAL MARKET ASSISTANCE REQUEST]* 💰\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"🏪 *Store:* {biz_name}\n"
                    f"👤 *Customer:* `+{customer_phone}`\n"
                    f"💬 *Customer Request:* '{query}'\n\n"
                    f"📈 *ACTION REQUIRED:* Customer requested market assistance/sourcing! Please reply to `+{customer_phone}` directly on WhatsApp."
                )
            }

        # 2. General Sourcing & Supply Triggers
        sourcing_triggers = [
            "do you have", "can you get", "can you supply", "do you sell", "can you source",
            "looking for", "do you carry", "where can i find", "do you supply", "need 10", "need 20",
            "need 50", "need 100", "bulk supply", "wholesale supply"
        ]

        if any(trigger in q for trigger in sourcing_triggers):
            item_requested = query
            for trigger in sourcing_triggers:
                if trigger in q:
                    item_requested = query.lower().split(trigger)[-1].strip(" ?!.")
                    break

            return {
                "type": "sourcing_opportunity",
                "customer_reply": (
                    f"🤝 *[{biz_name} — Special Sourcing & Supply Portal]*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Thank you for your request for *'{item_requested.title()}'*!\n\n"
                    f"While this item is not in our standard daily online catalog, our business sourcing unit (`+{manager_phone}`) can source, supply, and deliver this directly to you at wholesale rates!\n\n"
                    f"📞 Our Store Director is joining this chat now to provide a price quote and delivery timeline."
                ),
                "manager_alert": (
                    f"💰 *[NEW HIGH-VALUE BUSINESS OPPORTUNITY ALERT]* 💰\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"🏪 *Store:* {biz_name}\n"
                    f"👤 *Customer:* `+{customer_phone}`\n"
                    f"💡 *Opportunity Item:* '{item_requested.title()}'\n"
                    f"📝 *Full Request:* '{query}'\n\n"
                    f"📈 *REVENUE EXPANSION ACTION:* Can you source & supply this item for the customer?\n"
                    f"👉 Reply to customer `+{customer_phone}` directly to quote your price & close the deal!"
                )
            }

        return None

opportunity_lead_engine = OpportunityLeadEngine()
