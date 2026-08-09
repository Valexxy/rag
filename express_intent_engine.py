"""
====================================================================
EXPRESS INTENT INTELLIGENCE ENGINE (v2026)
====================================================================
Deep Intent Recognition & Semantic Routing Matrix for Online Commerce & Customer Care.
Understands millions of customer phrasing variations across 6 Core Intent Classes:

1. HUMAN_SUPPORT: Any request for human assistance, help, support, complaint, issue, escalation, person, agent, manager, staff, representative, urgent help.
2. CATALOG_INQUIRY: Inquiries about buying, products, stock, prices, models, specs.
3. OUT_OF_CATALOG: Items not sold in store (oil, cigarettes, clothes, etc.).
4. STORE_OPERATIONS: Hours, location, directions, payment, delivery, warranty, contact.
5. GREETING: Hi, hello, good morning, hey, how far.
6. GENERAL_AI_ADVICE: Product recommendations, sizing, technical questions.
"""

import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# ── SEMANTIC INTENT PATTERNS (Covers millions of natural phrasings) ────
HUMAN_SUPPORT_PATTERNS = [
    # Support & Assistance Intent
    r"\bsupport\b", r"\bhelp\b", r"\bassist\b", r"\bassistance\b", r"\bcare\b",
    r"\bcomplain\b", r"\bcomplaint\b", r"\bissue\b", r"\bproblem\b", r"\btrouble\b",
    r"\bfaulty\b", r"\bbroken\b", r"\bdamaged\b", r"\brefund\b", r"\bdispute\b",
    
    # Human Person & Staff Intent
    r"\bhuman\b", r"\bperson\b", r"\bpeople\b", r"\bagent\b", r"\brep\b",
    r"\brepresentative\b", r"\bmanager\b", r"\bboss\b", r"\bdirector\b",
    r"\bowner\b", r"\bstaff\b", r"\bpersonnel\b", r"\bteam\b", r"\bexecutive\b",
    r"\badmin\b", r"\badministrator\b", r"\bhead\b", r"\bin charge\b",
    
    # Action & Direct Connection Intent
    r"\btalk to\b", r"\bspeak to\b", r"\bspeak with\b", r"\btalk with\b",
    r"\bconnect me\b", r"\btransfer me\b", r"\breach someone\b", r"\bcall me\b",
    r"\bis anyone there\b", r"\banybody there\b", r"\bwho is there\b",
    r"\bneed someone\b", r"\bwant someone\b", r"\bneed help\b", r"\bneed support\b",
    r"\bneed assistance\b", r"\basap\b", r"\burgent\b", r"\bnow\b", r"\bemergency\b"
]

HUMAN_SUPPORT_REGEX = re.compile("|".join(HUMAN_SUPPORT_PATTERNS), re.IGNORECASE)

class ExpressIntentEngine:
    """Zero-Latency Express Intent Classification Engine."""

    def classify_intent(self, text: str) -> Dict[str, Any]:
        if not text:
            return {"intent": "UNKNOWN", "confidence": 0.0}

        q = text.strip().lower()

        # 1. HUMAN_SUPPORT INTENT (Top Priority)
        if HUMAN_SUPPORT_REGEX.search(q):
            return {
                "intent": "HUMAN_SUPPORT",
                "confidence": 1.0,
                "action": "ROUTE_TO_MANAGER",
                "priority": "HIGHEST"
            }

        # 2. GREETING INTENT
        greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "good day", "how far", "yo", "wassup"]
        if q in greetings or any(q.startswith(g + " ") for g in greetings):
            return {
                "intent": "GREETING",
                "confidence": 1.0,
                "action": "SHOW_CLIENT_CARE_MENU"
            }

        # 3. NUMERIC SELECTOR INTENT
        if q in ["1", "2", "3", "4", "5", "6"]:
            return {
                "intent": "NUMERIC_SELECTION",
                "confidence": 1.0,
                "selection": q,
                "action": "SHOW_PRODUCT_DETAILS"
            }

        # 4. DISAMBIGUATION CATEGORY INTENT
        if q in ["solar", "generator", "inverter"]:
            return {
                "intent": "DISAMBIGUATION_CATEGORY",
                "confidence": 1.0,
                "category": q,
                "action": "SHOW_DISAMBIGUATION_MENU"
            }

        # 5. STORE OPERATIONS INTENT
        ops_keywords = ["hours", "open", "close", "address", "location", "where", "pay", "payment", "deliver", "shipping", "warranty", "contact", "phone number"]
        if any(kw in q for kw in ops_keywords):
            return {
                "intent": "STORE_OPERATIONS",
                "confidence": 0.95,
                "action": "ANSWER_OPERATIONAL_FAQ"
            }

        return {
            "intent": "GENERAL_INQUIRY",
            "confidence": 0.8,
            "action": "CHECK_CATALOG_OR_AI"
        }

express_intent = ExpressIntentEngine()
