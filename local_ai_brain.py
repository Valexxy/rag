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

    def classify_intent(self, text: str) -> tuple:
        """Classifies intent locally without any external LLM call."""
        text_clean = text.lower().strip()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(r'\b' + pattern + r'\b', text_clean):
                    return intent, 0.95  # High confidence match

        return "GENERAL_INQUIRY", 0.50

local_brain = LocalAIBrain()
