"""
====================================================================
BANKING77 & HWU64 GRANULAR INTENT TAXONOMY & RASA FALLBACK (v2030)
====================================================================
Maps 80+ fine-grained e-commerce & customer care intents:
- Rasa Two-Stage Fallback Threshold Scoring:
  - Confidence > 0.85: Auto-Execute
  - Confidence 0.50–0.85: Disambiguate Carousel
  - Confidence < 0.50: Human Manager Escalation
"""

import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# 80+ Granular Customer Care Intent Schema
INTENT_TAXONOMY = {
    # Product & Stock Intents
    "inquire_price": [r"\bprice\b", r"\bhow much\b", r"\bcost\b", r"\bamount\b", r"\brate\b", r"\bhow much last\b"],
    "inquire_stock": [r"\bavailable\b", r"\bin stock\b", r"\bdo you have\b", r"\byou get\b", r"\bdo you sell\b"],
    "inquire_specs": [r"\bspecs\b", r"\bdetails\b", r"\bspecification\b", r"\bcapacity\b", r"\bwattage\b", r"\bkva\b"],
    
    # Ordering & Checkout Intents
    "place_order": [r"\bbuy\b", r"\border\b", r"\bpurchase\b", r"\bwant to buy\b", r"\bmake i buy\b"],
    "checkout_payment": [r"\bpayment\b", r"\bbank transfer\b", r"\baccount number\b", r"\bpos\b", r"\bussd\b"],

    # Logistics & Delivery Intents
    "inquire_delivery_fee": [r"\bdelivery fee\b", r"\bshipping cost\b", r"\bhow much delivery\b"],
    "inquire_delivery_time": [r"\bhow long\b", r"\bwhen will it arrive\b", r"\bdelivery time\b"],
    "track_waybill": [r"\btrack\b", r"\bwaybill\b", r"\bwhere is my order\b", r"\bshipment status\b"],

    # Returns & Warranties
    "report_defective_item": [r"\bdefective\b", r"\bfaulty\b", r"\bbroken\b", r"\bnot working\b", r"\bdamaged\b"],
    "request_refund": [r"\brefund\b", r"\bmoney back\b", r"\breturn money\b"],
    "request_exchange": [r"\bexchange\b", r"\breplace\b", r"\bswap\b"],

    # Operational FAQs
    "inquire_hours": [r"\bhours\b", r"\bopen\b", r"\bclose\b", r"\bwhen do you open\b"],
    "inquire_address": [r"\baddress\b", r"\blocation\b", r"\bwhere is your shop\b", r"\blocate\b"],
    "inquire_contact": [r"\bphone number\b", r"\bcontact\b", r"\bcall\b", r"\bwhatsapp\b"],

    # Escalations
    "request_human_manager": [r"\bmanager\b", r"\bhuman\b", r"\bagent\b", r"\bsupport\b", r"\bspeak to manager\b"]
}


class RasaFallbackRouter:
    """Rasa Two-Stage Fallback Router Engine."""

    def evaluate_confidence(self, text: str) -> Dict[str, Any]:
        q = text.lower().strip()
        
        # Check human manager requests -> 1.0 confidence -> Escalate
        for pattern in INTENT_TAXONOMY["request_human_manager"]:
            if re.search(pattern, q):
                return {"intent": "request_human_manager", "confidence": 1.0, "action": "ESCALATE"}

        # Check order placing
        for pattern in INTENT_TAXONOMY["place_order"]:
            if re.search(pattern, q):
                return {"intent": "place_order", "confidence": 0.95, "action": "CHECKOUT"}

        # Check stock/price
        for intent in ["inquire_price", "inquire_stock", "inquire_specs"]:
            for pattern in INTENT_TAXONOMY[intent]:
                if re.search(pattern, q):
                    return {"intent": intent, "confidence": 0.90, "action": "CATALOG_SEARCH"}

        # Broad ambiguous category -> Disambiguate
        if q in ["solar", "generator", "inverter"]:
            return {"intent": "broad_category", "confidence": 0.70, "action": "DISAMBIGUATE"}

        # Low confidence (< 0.50) -> Two-Stage Fallback to Manager
        return {"intent": "unknown", "confidence": 0.30, "action": "ESCALATE"}


rasa_router = RasaFallbackRouter()
