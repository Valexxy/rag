"""
╔══════════════════════════════════════════════════════════════════╗
║         SOVEREIGN RAG ENGINE — RETRIEVAL-AUGMENTED GENERATION  ║
║  Upgraded: semantic embeddings + Redis memory + full context    ║
╚══════════════════════════════════════════════════════════════════╝
"""

import re
import math
import json
import logging
from collections import Counter
from database import get_tenant_catalog, get_customer_ledger, get_customer_profile

logger = logging.getLogger(__name__)


class SovereignRAGEngine:
    """
    Production RAG Engine with semantic retrieval.
    
    Retrieval strategy (in priority order):
    1. Semantic similarity via SemanticCatalogEngine (sentence-transformers)
    2. TF-IDF bag-of-words similarity (fallback)
    3. Full catalog dump (last resort)
    """

    def __init__(self):
        self.chunk_size = 200
        # Lazy import to avoid circular deps
        self._semantic_catalog = None

    def _get_semantic_catalog(self):
        if self._semantic_catalog is None:
            try:
                from semantic_catalog_engine import semantic_catalog
                self._semantic_catalog = semantic_catalog
            except Exception as e:
                logger.warning(f"[RAG] Could not load SemanticCatalog: {e}")
        return self._semantic_catalog

    def tokenize(self, text: str) -> list:
        return re.findall(r'\w+', text.lower())

    def compute_tfidf_similarity(self, text1: str, text2: str) -> float:
        """TF-IDF cosine similarity — always available, no dependencies."""
        STOPWORDS = {
            "the", "a", "an", "is", "it", "in", "on", "at", "to", "for",
            "of", "and", "or", "not", "with", "this", "that", "have", "you",
            "do", "good", "morning", "afternoon", "evening", "need", "help",
            "human", "further", "enquiries", "please", "want", "some"
        }
        def clean_tokens(t):
            return [w for w in self.tokenize(t) if w not in STOPWORDS and len(w) > 2]

        vec1 = Counter(clean_tokens(text1))
        vec2 = Counter(clean_tokens(text2))
        common = set(vec1) & set(vec2)
        numerator = sum(vec1[x] * vec2[x] for x in common)
        denom = math.sqrt(sum(v**2 for v in vec1.values())) * math.sqrt(sum(v**2 for v in vec2.values()))
        return float(numerator / denom) if denom else 0.0

    # Keep old method name for backward compatibility
    def compute_vector_similarity(self, text1: str, text2: str) -> float:
        return self.compute_tfidf_similarity(text1, text2)

    def retrieve_relevant_context(self, tenant: dict, customer_phone: str, query: str) -> dict:
        """
        RETRIEVAL PHASE: Fetches and semantically ranks catalog items & customer history.
        
        Returns the most relevant context for answer generation.
        """
        # 1. Fetch catalog
        raw_catalog = get_tenant_catalog(tenant)

        # 2. Fetch customer profile & history
        try:
            profile = get_customer_profile(tenant["id"], customer_phone)
        except Exception:
            profile = {}
        try:
            ledger = get_customer_ledger(tenant["id"], customer_phone)
        except Exception:
            ledger = {}

        # 3. Normalize catalog to list
        if isinstance(raw_catalog, list):
            catalog_items = raw_catalog
            catalog_snippets = [
                f"{item.get('name','?')}: ₦{item.get('price',0):,.0f} — {item.get('description','')}"
                if isinstance(item, dict) else str(item)
                for item in raw_catalog
            ]
        elif isinstance(raw_catalog, str):
            catalog_items = []
            catalog_snippets = raw_catalog.split("\n\n")
        else:
            catalog_items = []
            catalog_snippets = [str(raw_catalog)]

        # 4. Semantic ranking (try sentence-transformers first)
        sc = self._get_semantic_catalog()
        top_context = ""
        best_item = None
        relevance_score = 0.0

        if sc and catalog_items:
            try:
                result = sc.search(query, catalog_items)
                if result["matched"]:
                    best_item = result["item"]
                    relevance_score = result["score"]
                    # Put best match first in context
                    top_context = result["reply"] + "\n\n"
            except Exception as e:
                logger.warning(f"[RAG] Semantic search error: {e}")

        # 5. TF-IDF ranking for remaining items
        ranked = []
        for i, snippet in enumerate(catalog_snippets):
            sim = self.compute_tfidf_similarity(query, snippet)
            ranked.append((sim, snippet))
        ranked.sort(key=lambda x: x[0], reverse=True)
        top_context += "\n".join([item[1] for item in ranked[:3] if item[1]])

        raw_catalog_str = "\n".join(catalog_snippets)

        return {
            "retrieved_catalog_context": top_context or raw_catalog_str,
            "retrieved_customer_profile": profile,
            "retrieved_customer_ledger": ledger,
            "relevance_score": relevance_score,
            "best_matched_item": best_item,
            "full_catalog": catalog_items,
        }

    def augment_prompt(self, tenant: dict, query: str, context: dict) -> str:
        """AUGMENTATION PHASE: Constructs a grounded, structured RAG prompt."""
        b_name = tenant.get("business_name", "Store")
        niche = tenant.get("business_niche", "retail")
        owner_phone = tenant.get("owner_phone", "+234 807 201 5725")
        store_address = tenant.get("store_address", "Onitsha, Anambra State")

        return f"""[SYSTEM ROLE]: You are the AI Assistant for {b_name} ({niche}).
[STORE LOCATION]: {store_address}
[OWNER CONTACT]: {owner_phone}
[BUSINESS HOURS]: Monday - Saturday, 8:00 AM - 6:00 PM WAT

[RETRIEVED KNOWLEDGE BASE — CATALOG]:
{context['retrieved_catalog_context']}

[CUSTOMER PURCHASE HISTORY]:
{context['retrieved_customer_ledger'] or 'First-time customer'}

[CUSTOMER QUERY]: {query}

CRITICAL INSTRUCTIONS:
1. Answer ONLY from the retrieved catalog above. Never invent products or prices.
2. If the item is NOT in the catalog above, output exactly: HANDOFF_NEEDED
3. If the customer wants to buy/pay, output: HANDOFF_NEEDED
4. Keep response to 2-3 sentences max. Use ₦ for all prices.
5. You are {b_name}'s AI, NOT ChatGPT or any other AI."""


rag_engine = SovereignRAGEngine()
