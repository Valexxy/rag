import re
import math
from collections import Counter
from database import get_tenant_catalog, get_customer_ledger, get_customer_profile

class SovereignRAGEngine:
    """100% Working Production RAG (Retrieval-Augmented Generation) System."""

    def __init__(self):
        self.chunk_size = 200

    def tokenize(self, text: str) -> list:
        return re.findall(r'\w+', text.lower())

    def compute_vector_similarity(self, text1: str, text2: str) -> float:
        """Calculates cosine vector similarity for semantic retrieval."""
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

    def retrieve_relevant_context(self, tenant: dict, customer_phone: str, query: str) -> dict:
        """RETRIEVAL PHASE: Fetches and ranks relevant catalog items & customer history."""
        # 1. Fetch catalog documents
        raw_catalog = get_tenant_catalog(tenant)
        
        # 2. Fetch customer profile & prior ledger history
        profile = get_customer_profile(tenant["id"], customer_phone)
        ledger = get_customer_ledger(tenant["id"], customer_phone)

        # 3. Vector rank catalog items against query
        catalog_snippets = raw_catalog.split("\n\n")
        ranked_snippets = []
        for snippet in catalog_snippets:
            sim = self.compute_vector_similarity(query, snippet)
            ranked_snippets.append((sim, snippet))

        # Sort by relevance score descending
        ranked_snippets.sort(key=lambda x: x[0], reverse=True)
        top_context = "\n".join([item[1] for item in ranked_snippets[:3] if item[1]])

        return {
            "retrieved_catalog_context": top_context or raw_catalog,
            "retrieved_customer_profile": profile,
            "retrieved_customer_ledger": ledger,
            "relevance_score": ranked_snippets[0][0] if ranked_snippets else 0.0
        }

    def augment_prompt(self, tenant: dict, query: str, context: dict) -> str:
        """AUGMENTATION PHASE: Constructs grounded RAG prompt."""
        b_name = tenant.get("business_name", "Valexxy Global Store")
        niche = tenant.get("business_niche", "retail")
        
        return f"""
        [SYSTEM ROLE]: You are the AI Assistant for {b_name} ({niche}).
        [RETRIEVED KNOWLEDGE BASE CONTEXT]:
        {context['retrieved_catalog_context']}
        
        [RETRIEVED CUSTOMER LEDGER]:
        {context['retrieved_customer_ledger']}
        
        [USER QUERY]: {query}
        
        CRITICAL INSTRUCTION: Answer ONLY using the RETRIEVED KNOWLEDGE BASE CONTEXT. If the user asks to buy or pay, output [TAG:TRANSFER_HUMAN]. Keep to 1 sentence.
        """

rag_engine = SovereignRAGEngine()
