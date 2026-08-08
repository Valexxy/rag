"""
╔══════════════════════════════════════════════════════════════════╗
║         SEMANTIC CATALOG ENGINE — VECTOR SEARCH CORE           ║
║  sentence-transformers all-MiniLM-L6-v2 (Local, Free, Fast)    ║
║  + TF-IDF fallback when model not yet downloaded                ║
╚══════════════════════════════════════════════════════════════════╝

Finds the correct catalog item by MEANING, not keywords.
"panels for my inverter system" → 550W Monocrystalline Solar Panel ✅
"something to store power" → 20,000 mAh Solar Power Bank ✅
"i need human help" → NO MATCH (score too low) → human handoff ✅
"""

import os
import math
import json
import logging
import hashlib
from collections import Counter
from typing import Optional

logger = logging.getLogger(__name__)

# Minimum cosine similarity score to consider a catalog match valid.
# Below this threshold → item is NOT returned → falls to human handoff.
SEMANTIC_MATCH_THRESHOLD = 0.32   # sentence-transformers cosine score (0.0-1.0)
TFIDF_MATCH_THRESHOLD    = 0.50   # TF-IDF fallback — high threshold to avoid mismatches

# Redis key prefix for embedding cache
CACHE_PREFIX = "catalog_embed:"


def _get_redis():
    """Returns Redis client if available."""
    try:
        import redis
        url = os.environ.get("REDIS_URL") or os.environ.get("REDIS_HOST")
        if url and url.startswith("redis://"):
            return redis.from_url(url, decode_responses=False, socket_connect_timeout=3)
        host = os.environ.get("REDIS_HOST", "localhost")
        port = int(os.environ.get("REDIS_PORT", 6379))
        pw = os.environ.get("REDIS_PASSWORD", "")
        user = os.environ.get("REDIS_USERNAME", "default")
        return redis.Redis(host=host, port=port, username=user, password=pw,
                           decode_responses=False, socket_connect_timeout=3)
    except Exception:
        return None


class SemanticCatalogEngine:
    """
    Two-tier catalog search engine:
    Tier 1: HuggingFace sentence-transformers (semantic meaning, ~90MB local model)
    Tier 2: TF-IDF cosine similarity (always works, no download needed)
    
    Both are 100% free and run locally without any API calls.
    """

    def __init__(self):
        self._embedder = None
        self._embedder_ready = False
        self._redis = _get_redis()
        self._try_load_embedder()

    def _try_load_embedder(self):
        """Attempts to load sentence-transformers in a non-blocking background thread."""
        import threading
        
        def _bg_load():
            try:
                logger.info("[SemanticCatalog] Initializing sentence-transformers in background thread...")
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer("all-MiniLM-L6-v2")
                self._embedder = model
                self._embedder_ready = True
                logger.info("[SemanticCatalog] ✅ sentence-transformers loaded — semantic search active")
            except ImportError:
                logger.warning("[SemanticCatalog] sentence-transformers not installed — using TF-IDF fallback")
            except Exception as e:
                logger.warning(f"[SemanticCatalog] Model load failed — using TF-IDF fallback: {e}")

        t = threading.Thread(target=_bg_load, daemon=True)
        t.start()

    # ── Embedding helpers ────────────────────────────────────────────

    def _item_to_text(self, item: dict) -> str:
        """Converts a catalog item dict to a searchable text string."""
        name = item.get("name", "")
        desc = item.get("description", "")
        # Include synonyms from metadata if available
        meta = item.get("metadata", {}) or {}
        tags = " ".join(meta.get("tags", [])) if isinstance(meta, dict) else ""
        return f"{name}. {desc}. {tags}".strip()

    def _cache_key(self, text: str) -> str:
        return CACHE_PREFIX + hashlib.md5(text.encode()).hexdigest()

    def _get_cached_embedding(self, text: str):
        if not self._redis:
            return None
        try:
            import numpy as np
            raw = self._redis.get(self._cache_key(text))
            if raw:
                return np.frombuffer(raw, dtype=np.float32)
        except Exception:
            pass
        return None

    def _cache_embedding(self, text: str, embedding):
        if not self._redis:
            return
        try:
            import numpy as np
            self._redis.setex(
                self._cache_key(text),
                86400 * 7,  # 7-day cache
                embedding.astype(np.float32).tobytes()
            )
        except Exception:
            pass

    def _embed(self, text: str):
        """Returns embedding vector, using Redis cache when possible."""
        cached = self._get_cached_embedding(text)
        if cached is not None:
            return cached
        vec = self._embedder.encode(text, convert_to_numpy=True, show_progress_bar=False)
        self._cache_embedding(text, vec)
        return vec

    def _cosine(self, a, b) -> float:
        """Fast cosine similarity between two numpy vectors."""
        import numpy as np
        denom = (np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)

    # ── TF-IDF fallback (no external dependencies) ──────────────────

    def _tfidf_score(self, query: str, item_text: str) -> float:
        """Basic bag-of-words cosine similarity — always works."""
        STOPWORDS = {
            "the", "a", "an", "is", "it", "in", "on", "at", "to", "for",
            "of", "and", "or", "but", "not", "with", "this", "that", "are",
            "was", "be", "by", "do", "have", "has", "had", "i", "you", "we",
            "they", "he", "she", "good", "morning", "afternoon", "evening",
            "need", "want", "please", "help", "human", "further", "enquiries",
            "more", "some", "any", "just", "very", "how", "what", "where",
            "who", "why", "when", "can", "get", "my", "your", "our", "their"
        }
        def tokenize(t):
            import re
            return [w for w in re.findall(r'\w+', t.lower()) if w not in STOPWORDS and len(w) > 2]

        q_tokens = Counter(tokenize(query))
        d_tokens = Counter(tokenize(item_text))
        if not q_tokens or not d_tokens:
            return 0.0
        common = set(q_tokens) & set(d_tokens)
        numerator = sum(q_tokens[w] * d_tokens[w] for w in common)
        denom = math.sqrt(sum(v**2 for v in q_tokens.values())) * math.sqrt(sum(v**2 for v in d_tokens.values()))
        return float(numerator / denom) if denom else 0.0

    # ── Main search API ─────────────────────────────────────────────

    def search(self, query: str, catalog: list) -> dict:
        """
        Finds the best matching catalog item for a customer's query.
        
        Args:
            query: Customer's message or extracted product intent
            catalog: List of catalog item dicts from database
            
        Returns:
            {
                "matched": bool,
                "item": dict | None,
                "score": float,
                "method": "semantic" | "tfidf",
                "reply": str  (formatted WhatsApp product card)
            }
        """
        if not catalog or not isinstance(catalog, list):
            return {"matched": False, "item": None, "score": 0.0, "method": "none"}

        # Filter to valid dict items only
        valid_items = [item for item in catalog if isinstance(item, dict) and item.get("name")]
        if not valid_items:
            return {"matched": False, "item": None, "score": 0.0, "method": "none"}

        best_item = None
        best_score = 0.0
        method = "none"

        # ── KEYWORD DISAMBIGUATION TABLE ────────────────────────────────
        # Maps query keywords → product name fragments they should boost.
        # Used to tiebreak between semantically close items (e.g. solar panel
        # vs solar power bank both containing "solar").
        # Boost value of +0.15 is decisive without overpowering the base score.
        KEYWORD_BOOSTS = {
            "panel":     ("panel", +0.15),
            "panels":    ("panel", +0.15),
            "bank":      ("power bank", +0.15),
            "powerbank": ("power bank", +0.15),
            "generator": ("generator", +0.15),
            "inverter":  ("inverter", +0.15),
            "genset":    ("generator", +0.15),
            "kva":       ("kva", +0.30),
            "1.5kva":    ("1.5kva", +0.35),
            "3.5kva":    ("3.5kva", +0.35),
            "rice":      ("rice", +0.15),
            "gold":      ("gold", +0.15),
            "bullion":   ("gold", +0.15),
        }

        def _apply_keyword_boost(base_score: float, item: dict, query_lower: str) -> float:
            """Applies keyword boost to disambiguate semantically similar items."""
            item_name_lower = item.get("name", "").lower()
            item_desc_lower = item.get("description", "").lower()
            item_text_lower = f"{item_name_lower} {item_desc_lower}".replace(" ", "").replace(".", "").replace("-", "")
            q_clean = query_lower.replace(" ", "").replace(".", "").replace("-", "")
            
            boosted = base_score
            query_tokens = set(query_lower.split())
            
            # Exact substring match for technical product specs (e.g. 1.5kva in 1.5kvadualsolargenerator)
            if q_clean in item_text_lower and len(q_clean) >= 3:
                boosted += 0.35

            for token, (target_fragment, boost) in KEYWORD_BOOSTS.items():
                if (token in query_tokens or token in q_clean) and target_fragment in item_text_lower:
                    boosted += boost
                    break
            return boosted

        q_lower = query.lower()

        if self._embedder_ready:
            # ── TIER 1: Semantic Embeddings + Keyword Boost ───────────────
            try:
                query_vec = self._embed(query)
                scored_items = []
                for item in valid_items:
                    item_text = self._item_to_text(item)
                    item_vec = self._embed(item_text)
                    raw_score = self._cosine(query_vec, item_vec)
                    boosted_score = _apply_keyword_boost(raw_score, item, q_lower)
                    scored_items.append((boosted_score, raw_score, item))

                scored_items.sort(key=lambda x: x[0], reverse=True)
                if scored_items:
                    best_score = scored_items[0][0]
                    best_item = scored_items[0][2]
                method = "semantic+boost"
                threshold = SEMANTIC_MATCH_THRESHOLD
            except Exception as e:
                logger.warning(f"[SemanticCatalog] Semantic search failed, using TF-IDF: {e}")
                best_item = None
                best_score = 0.0

        if not self._embedder_ready or method == "none":
            # ── TIER 2: TF-IDF + Keyword Boost Fallback ──────────────────
            scored_items = []
            for item in valid_items:
                item_text = self._item_to_text(item)
                raw_score = self._tfidf_score(query, item_text)
                boosted_score = _apply_keyword_boost(raw_score, item, q_lower)
                scored_items.append((boosted_score, item))
            scored_items.sort(key=lambda x: x[0], reverse=True)
            if scored_items:
                best_score = scored_items[0][0]
                best_item = scored_items[0][1]
            method = "tfidf+boost"
            threshold = TFIDF_MATCH_THRESHOLD

        if best_item and best_score >= threshold:
            return {
                "matched": True,
                "item": best_item,
                "score": best_score,
                "method": method,
                "reply": self._format_product_card(best_item)
            }

        return {"matched": False, "item": None, "score": best_score, "method": method}

    def search_with_intent(self, product_query: Optional[str], full_message: str, catalog: list) -> dict:
        """
        Two-pass search: first tries the extracted product intent,
        then tries the full message if intent search fails.
        This gives the best accuracy when the AI has extracted a product name.
        """
        # Pass 1: Use AI-extracted product query (most accurate)
        if product_query:
            result = self.search(product_query, catalog)
            if result["matched"]:
                return result

        # Pass 2: Use full customer message
        result = self.search(full_message, catalog)
        return result

    def _format_product_card(self, item: dict) -> str:
        """Formats a catalog item as a beautiful WhatsApp product card."""
        name = item.get("name", "Product")
        price = item.get("price", 0)
        desc = item.get("description", "In Stock & Ready for Dispatch")
        status = item.get("status", "In Stock")
        price_fmt = f"₦{price:,.2f}" if isinstance(price, (int, float)) else str(price)

        return (
            f"🛍️ *[Teeslux Store — Product Found]*\n\n"
            f"✅ *{name}*\n"
            f"💰 *Fixed Price:* {price_fmt}\n"
            f"📦 *Status:* {status}\n"
            f"📝 *Details:* {desc}\n\n"
            f"💬 Reply *#buy* to place your order, or *#human* to speak with our manager."
        )


# Singleton — import this everywhere
semantic_catalog = SemanticCatalogEngine()
