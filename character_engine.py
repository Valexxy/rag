"""
╔══════════════════════════════════════════════════════════════════╗
║       CHARACTER ENGINE — AI RESPONSE GENERATION PIPELINE       ║
║  Powered by: Sovereign AI Brain (Groq Llama 3.3 70B / Gemini)  ║
║  + Semantic Catalog Search + RAG Context Retrieval              ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import re
import logging
from database import get_tenant_catalog, get_customer_ledger, get_customer_profile
from rag_engine import rag_engine

logger = logging.getLogger(__name__)


def get_niche_config(niche: str) -> dict:
    """Maps business niches to specific vocabulary and action verbs."""
    niche = (niche or "retail").lower()
    if niche == "real_estate":
        return {
            "offerings_name": "property portfolio",
            "action_verb": "schedule a viewing or discuss terms",
        }
    elif niche in ("service", "salon"):
        return {
            "offerings_name": "list of services",
            "action_verb": "book an appointment",
        }
    else:
        return {
            "offerings_name": "product lineup",
            "action_verb": "finalize your request",
        }


def generate_live_character_reply(
    tenant: dict,
    customer_phone: str,
    latest_query: str,
    conversation_history: str,
    is_owner: bool = False,
) -> dict:
    """
    Full AI pipeline for generating a customer reply.
    
    Pipeline:
    1. RAG retrieval — fetch catalog + customer history
    2. Sovereign AI Brain — intent classification + grounded answer generation
    3. Fallback chain — if AI fails, clean human handoff
    
    Returns a dict with:
      - reply: str (formatted WhatsApp message)
      - is_human_transfer: bool
      - is_high_value: bool
      - detected_tags: list
      - buttons: list
    """
    business_name = tenant.get("business_name", "Store")
    niche = tenant.get("business_niche", "retail")
    config = get_niche_config(niche)

    # ── 1. RAG RETRIEVAL ─────────────────────────────────────────────
    rag_context = rag_engine.retrieve_relevant_context(tenant, customer_phone, latest_query)
    full_catalog = rag_context.get("full_catalog", [])
    best_matched_item = rag_context.get("best_matched_item")

    # ── 2. SOVEREIGN AI BRAIN — INTENT + ANSWER ──────────────────────
    try:
        from sovereign_ai_brain import sovereign_brain

        # Classify intent first — understands any phrasing
        classification = sovereign_brain.classify_intent(
            message=latest_query,
            catalog=full_catalog,
            conversation_history=conversation_history,
        )
        intent = classification["intent"]
        product_query = classification.get("product_query")

        # If AI says human request — escalate immediately
        if intent in ("HUMAN_REQUEST", "UNKNOWN") and not is_owner:
            return _human_handoff_reply(business_name)

        # For catalog queries — try semantic search with AI-extracted product name
        if intent == "CATALOG_QUERY" and not is_owner:
            try:
                from semantic_catalog_engine import semantic_catalog
                search_result = semantic_catalog.search_with_intent(
                    product_query=product_query,
                    full_message=latest_query,
                    catalog=full_catalog,
                )
                if search_result["matched"]:
                    return {
                        "reply": search_result["reply"],
                        "is_human_transfer": False,
                        "is_high_value": False,
                        "detected_tags": [],
                        "buttons": ["#buy", "#human"],
                        "source": f"semantic_{search_result['method']}",
                    }
                # No catalog match → let AI generate general answer or handoff
            except Exception as e:
                logger.warning(f"[CharEngine] Semantic search error: {e}")

        # ── 3. MULTI-DIMENSIONAL OPEN-SOURCE AI ENSEMBLE ─────────────────
        from multi_dimensional_ai_ensemble import ai_ensemble
        cat_summary = "\n".join([f"• {item.get('name')}: ₦{item.get('price'):,}" for item in full_catalog if isinstance(item, dict)])
        
        ensemble_res = ai_ensemble.generate_ensemble_reply(
            customer_query=latest_query,
            catalog_context=cat_summary,
            chat_history=conversation_history
        )

        return {
            "reply": ensemble_res["reply"],
            "is_human_transfer": False,
            "is_high_value": False,
            "detected_tags": [],
            "buttons": ["#1 Catalog", "#human Manager"],
            "source": ensemble_res.get("architecture", "multi_dimensional_ensemble"),
        }

    except Exception as e:
        logger.error(f"[CharEngine] Sovereign Brain error: {e}")
        from multi_dimensional_ai_ensemble import ai_ensemble
        fallback = ai_ensemble.generate_ensemble_reply(latest_query, "Teeslux Global Store")
        return {
            "reply": fallback["reply"],
            "is_human_transfer": False,
            "is_high_value": False,
            "detected_tags": [],
            "buttons": ["#1 Catalog", "#human Manager"],
            "source": "fallback_ensemble",
        }


def _human_handoff_reply(business_name: str) -> dict:
    """Returns a clean, professional interactive human handoff reply."""
    return {
        "reply": (
            f"🤖 *[{business_name} AI Assistant]*\n\n"
            f"Thank you for your enquiry! I have notified our store manager to assist you personally.\n\n"
            f"❓ While our manager reviews your request, is there a specific model, size, or detail you'd like me to look up for you in the meantime?"
        ),
        "is_human_transfer": True,
        "is_high_value": False,
        "detected_tags": ["[TAG:TRANSFER_HUMAN]"],
        "buttons": ["👤 Human Agent"],
        "source": "handoff",
    }