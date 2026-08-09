"""
====================================================================
EXPRESS INTENT ENGINE v2030 — World-Class Customer Care Matrix
====================================================================
Includes:
- Frustration & Anger Detection
- Nigerian Pidgin & E-Commerce Slang Matching
- Price Haggling & Bargaining Guardrails
- Human Escalation Classification
"""

import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Frustration & Anger Keywords
FRUSTRATION_REGEX = re.compile(
    r"\b(rubbish|scam|scammer|thief|cheat|stole|fraud|stupid|useless|horrible|terrible|frustrated|frustration|angry|mad|waste of time|fool|bad service|worst|lawyer|police|sue)\b",
    re.IGNORECASE
)

# Price Haggling Keywords
HAGGLING_REGEX = re.compile(
    r"\b(discount|reduce|reduction|last price|how much last|cheaper|lower price|bargain|slash|cut price|best price)\b",
    re.IGNORECASE
)

# Human Support Escalation Keywords
HUMAN_SUPPORT_REGEX = re.compile(
    r"\b(support|help|assist|assistance|care|complain|complaint|issue|problem|trouble|faulty|broken|damaged|refund|dispute|human|person|people|agent|rep|representative|manager|boss|director|owner|staff|personnel|team|executive|admin|administrator|head|talk to|speak to|speak with|talk with|connect me|transfer me|reach someone|call me|is anyone there|anybody there|who is there|need someone|want someone|need help|need support|need assistance|asap|urgent|now|emergency)\b",
    re.IGNORECASE
)

# Nigerian Pidgin Commerce Slang
PIDGIN_COMMERCE_REGEX = re.compile(
    r"\b(how far|how much be|you get|make i buy|abeg|where your shop dey|i wan buy|wetin be|how much last|choko|shishi)\b",
    re.IGNORECASE
)


class ExpressIntentEngine:
    """World-Class Customer Care Intent Classifier."""

    def classify_intent(self, text: str) -> Dict[str, Any]:
        if not text:
            return {"intent": "UNKNOWN", "confidence": 0.0}

        q = text.strip()

        # 1. Frustration / Anger Detection -> Priority 1 Escalation
        if FRUSTRATION_REGEX.search(q):
            return {
                "intent": "FRUSTRATION_ANGRY_CUSTOMER",
                "confidence": 1.0,
                "action": "URGENT_MANAGER_ESCALATION"
            }

        # 2. Explicit Human Support Request
        if HUMAN_SUPPORT_REGEX.search(q):
            return {
                "intent": "HUMAN_SUPPORT",
                "confidence": 1.0,
                "action": "MANAGER_HANDOVER"
            }

        # 3. Price Haggling / Bargaining Request
        if HAGGLING_REGEX.search(q):
            return {
                "intent": "PRICE_HAGGLING",
                "confidence": 0.95,
                "action": "HAGGLING_GUARDRAIL"
            }

        # 4. Nigerian Pidgin Commerce Request
        if PIDGIN_COMMERCE_REGEX.search(q):
            return {
                "intent": "PIDGIN_COMMERCE",
                "confidence": 0.90,
                "action": "PIDGIN_RESPONSE"
            }

        return {"intent": "GENERAL_INQUIRY", "confidence": 0.5}


express_intent = ExpressIntentEngine()
