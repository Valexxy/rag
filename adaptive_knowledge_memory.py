"""
====================================================================
ADAPTIVE KNOWLEDGE MEMORY & FEW-SHOT LEARNING ENGINE
====================================================================
Maintains a dynamic memory store of verified store knowledge, custom Q&A pairs,
and successful owner corrections. Automatically retrieves the top-2 most relevant
few-shot exemplars and injects them into the NLU/LLM context!
"""

import time
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class AdaptiveKnowledgeMemory:
    """Dynamic Few-Shot Learning & Knowledge RAG Memory Engine."""

    def __init__(self):
        # In-memory store: tenant_id -> list of {"question": str, "answer": str, "vector": list}
        self._memory_store: Dict[str, List[dict]] = {}
        self._embedder = None

    def _get_embedder(self):
        if self._embedder is None:
            try:
                from semantic_catalog_engine import semantic_catalog
                self._embedder = semantic_catalog
            except Exception:
                pass
        return self._embedder

    def add_learned_exemplar(self, tenant_id: str, question: str, answer: str, source: str = "owner_correction"):
        """Stores a new verified Q&A exemplar for continuous learning."""
        tid = str(tenant_id)
        if tid not in self._memory_store:
            self._memory_store[tid] = []

        embedder = self._get_embedder()
        q_vec = embedder._embed(question) if embedder and getattr(embedder, "_embedder_ready", False) else None

        self._memory_store[tid].append({
            "question": question,
            "answer": answer,
            "vector": q_vec,
            "source": source,
            "created_at": time.time()
        })
        logger.info(f"[AdaptiveMemory] 🧠 Learned new Q&A exemplar for tenant '{tid}': '{question[:35]}'")

    def get_relevant_exemplars(self, tenant_id: str, query: str, top_k: int = 2) -> List[dict]:
        """Retrieves top_k most semantically relevant exemplars for few-shot prompt injection."""
        tid = str(tenant_id)
        if tid not in self._memory_store or not self._memory_store[tid]:
            return []

        embedder = self._get_embedder()
        if not embedder or not getattr(embedder, "_embedder_ready", False):
            return self._memory_store[tid][:top_k]

        try:
            q_vec = embedder._embed(query)
            scored = []
            for item in self._memory_store[tid]:
                if item.get("vector") is not None:
                    sim = embedder._cosine(q_vec, item["vector"])
                    if sim >= 0.4:  # Minimum relevant threshold
                        scored.append((sim, item))

            scored.sort(key=lambda x: x[0], reverse=True)
            return [x[1] for x in scored[:top_k]]
        except Exception as e:
            logger.warning(f"[AdaptiveMemory] Exemplar retrieval error: {e}")
            return []

    def format_few_shot_context(self, tenant_id: str, query: str) -> str:
        """Formats relevant exemplars into clean few-shot prompt context."""
        exemplars = self.get_relevant_exemplars(tenant_id, query, top_k=2)
        if not exemplars:
            return ""

        lines = ["[PAST VERIFIED EXAMPLES FOR THIS STORE]:"]
        for ex in exemplars:
            lines.append(f"  Customer: \"{ex['question']}\"")
            lines.append(f"  Store Answer: \"{ex['answer']}\"\n")

        return "\n".join(lines) + "\n"

# Singleton instance
adaptive_memory = AdaptiveKnowledgeMemory()
