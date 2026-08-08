import re
import math
from collections import Counter

class LocalAIBrain:
    """Zero-Cost Self-Learning Local AI Pattern Matching & Intent Classifier Engine."""

    def __init__(self):
        # Pre-trained local semantic patterns
        self.intent_patterns = {
            "DISCOVERY": [r"catalog", r"price", r"cost", r"how much", r"items", r"products", r"services", r"menu", r"list", r"offerings"],
            "PURCHASE": [r"buy", r"order", r"pay", r"payment", r"bank", r"transfer", r"account", r"checkout", r"purchase"],
            "LOGISTICS": [r"track", r"waybill", r"delivery", r"shipping", r"where is my", r"dispatch", r"courier", r"otp"],
            "BOOKING": [r"book", r"appointment", r"schedule", r"tour", r"inspection", r"reserve", r"slot"],
            "SUPPORT": [r"human", r"agent", r"manager", r"owner", r"speak", r"call", r"help", r"complain"],
            "HOURS_LOCATION": [r"location", r"address", r"where are you", r"office", r"store", r"opening", r"hours", r"open"]
        }

    def tokenize(self, text: str) -> list:
        return re.findall(r'\w+', text.lower())

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculates cosine similarity between two strings locally."""
        vec1 = Counter(self.tokenize(text1))
        vec2 = Counter(self.tokenize(text2))
        
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])

        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        return float(numerator) / denominator

    def match_catalog_product(self, tenant: dict, query: str):
        """Ultra-fast sub-150ms deterministic catalog lookup engine with exact keyword scoring."""
        q_lower = query.lower()
        catalog = tenant.get("catalog", [])
        if not catalog:
            from database import get_tenant_catalog
            catalog = get_tenant_catalog(tenant)
            
        if not isinstance(catalog, list) or not catalog:
            return {"matched": False}

        best_item = None
        best_score = 0

        for item in catalog:
            name = item.get("name", "") if isinstance(item, dict) else str(item)
            desc = item.get("description", "") if isinstance(item, dict) else ""
            item_text = f"{name} {desc}".lower()

            score = 0
            
            # Specific word match scoring
            if "panel" in q_lower or "panels" in q_lower:
                if "panel" in item_text:
                    score += 20
                elif "power bank" in item_text:
                    score -= 10

            if "bank" in q_lower or "power bank" in q_lower:
                if "power bank" in item_text or "bank" in item_text:
                    score += 20

            if "generator" in q_lower or "inverter" in q_lower:
                if "generator" in item_text or "inverter" in item_text:
                    score += 20

            if "rice" in q_lower:
                if "rice" in item_text:
                    score += 20

            if "gold" in q_lower:
                if "gold" in item_text:
                    score += 20

            if "solar" in q_lower and "solar" in item_text:
                score += 5

            # General word overlap (stopwords filter prevents phantom matches)
            STOPWORDS = {
                "good", "morning", "afternoon", "evening", "have", "you", "do",
                "want", "need", "please", "some", "the", "and", "for", "are",
                "this", "that", "with", "from", "can", "get", "how", "many",
                "types", "sell", "buy", "help", "human", "further", "enquiries",
                "enquiry", "question", "questions", "info", "information",
                "more", "about", "please", "kindly", "what", "when", "where",
                "who", "why", "any", "all", "much", "there", "not", "just",
                "your", "our", "its", "like", "also", "other", "send", "let"
            }
            query_words = set(
                w for w in q_lower.split()
                if len(w) > 3 and w not in STOPWORDS
            )
            for qw in query_words:
                if qw in item_text:
                    score += 2

            if score > best_score:
                best_score = score
                best_item = item

        # ✅ MINIMUM SCORE THRESHOLD: Must score >= 10 to be a real catalog match.
        # This prevents generic messages ("I need human help") from accidentally
        # matching a product just because of word overlap with score 0 or 2.
        if best_item and best_score >= 10:
            price = best_item.get("price", "") if isinstance(best_item, dict) else ""
            name = best_item.get("name", "") if isinstance(best_item, dict) else str(best_item)
            desc = best_item.get("description", "") if isinstance(best_item, dict) else ""
            price_fmt = f"₦{price:,.2f}" if isinstance(price, (int, float)) else str(price)
            b_name = tenant.get("business_name", "Store")
            return {
                "matched": True,
                "reply": f"🤖 *[{b_name} Instant Catalog Match]*\n\n✅ *Item:* {name}\n💰 *Fixed Price:* {price_fmt}\n📝 *Details:* {desc or 'In Stock & Ready for Dispatch'}\n\n💬 Reply *#buy* to get payment link, or *#human* to speak with store manager."
            }
            
        return {"matched": False}

    def classify_intent(self, text: str) -> tuple:
        """Classifies intent locally without any external LLM call."""
        text_clean = text.lower().strip()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(r'\b' + pattern + r'\b', text_clean):
                    return intent, 0.95  # High confidence match

        return "GENERAL_INQUIRY", 0.50

local_brain = LocalAIBrain()
