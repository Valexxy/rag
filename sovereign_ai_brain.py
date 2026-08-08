import os
import json
import re
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Inject HF_TOKEN for authenticated HuggingFace access (higher rate limits)
_hf_token = os.environ.get("HF_TOKEN")
if _hf_token:
    os.environ["HUGGINGFACE_TOKEN"] = _hf_token
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


# ─────────────────────────────────────────────
# MODEL PRIORITY: Groq Llama 3.3 70B → Gemini 1.5 Flash 8B
# Both are 100% free. Groq is primary (fastest, best reasoning).
# Gemini 1.5 Flash 8B: 1,500 req/day, 1M tokens/day — high quota.
# ─────────────────────────────────────────────
GROQ_MODEL    = "llama-3.3-70b-versatile"   # Free: 14,400 req/day, 128K context
GEMINI_MODEL  = "gemini-1.5-flash-8b"        # Free: 1,500 req/day, higher quota than 2.0
GEMINI_RETRY_AFTER = 60   # seconds to wait after rate limit before retrying

# Intent classification schema — what Groq/Gemini will return
INTENT_SCHEMA = {
    "GREETING":       "Short hi/hello/good morning (no product or question embedded)",
    "MENU_OPTION":    "Customer replied with a digit 1-5 or #1-#5",
    "CATALOG_QUERY":  "Customer asking about a specific product, price, availability",
    "HUMAN_REQUEST":  "Customer wants human support, escalation, further enquiries",
    "COMMAND":        "Message starts with # (trust, buy, price, legal, market etc.)",
    "PURCHASE":       "Customer explicitly wants to buy, pay, order, or place an order",
    "GENERAL":        "Location, hours, policy, returns, complaints, other business questions",
    "UNKNOWN":        "Cannot be classified — route to human"
}


def _get_groq_client():
    """Returns a Groq client if GROQ_API_KEY is available."""
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        return None
    try:
        from groq import Groq
        return Groq(api_key=key)
    except Exception as e:
        logger.warning(f"[SovereignBrain] Groq client init failed: {e}")
        return None


def _get_gemini_client():
    """Returns a Gemini client if GEMINI_API_KEY is available."""
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=key)
    except Exception as e:
        logger.warning(f"[SovereignBrain] Gemini client init failed: {e}")
        return None


def _build_intent_prompt(message: str, catalog_names: list, conversation_history: str = "") -> str:
    """
    Builds the NLU intent classification prompt.
    Hardened for all SAAS edge cases: Pidgin, all-caps, Hausa/Igbo mix,
    multi-tenant catalogs, angry customers, gibberish, abuse, etc.
    """
    catalog_list = "\n".join([f"  - {name}" for name in catalog_names]) if catalog_names else "  (No catalog items — new store)"
    history_block = f"\n[RECENT CONVERSATION CONTEXT]:\n{conversation_history[-500:]}\n" if conversation_history else ""

    return f"""You are an expert NLU intent classifier for a multi-tenant WhatsApp commerce platform serving Nigerian businesses.

[BUSINESS CATALOG (this tenant's products/services)]:
{catalog_list}
{history_block}
[CUSTOMER MESSAGE]: "{message}"

Classify into EXACTLY ONE intent:

GREETING      → ONLY pure greetings with no question or product mention embedded
               Examples: "Hi", "Hello", "Good morning", "Hey"
               NOT: "Good morning, do you have panels?" (that = CATALOG_QUERY)

MENU_OPTION   → Customer sent ONLY a single digit 1-5 or #1-#5 as menu reply
               Examples: "1", "2", "#3"

CATALOG_QUERY → Any question or inquiry about products/services/prices/availability
               Works in: English, Pidgin, Broken English, mixed language
               Examples: "do you have solar panels", "how much na your generator",
               "pls i wan buy rice how much e go cost", "SOLAR PANEL PRICE???",
               "what types you get", "e get gold for your shop?"

HUMAN_REQUEST → Customer wants to speak with a human/manager/owner/agent
               OR complex multi-part enquiries needing human attention
               OR frustration/complaints/urgency
               Examples: "i need human help", "further enquiries", "connect me to manager",
               "oga i wan see your oga", "I have a complaint", "this is urgent"

COMMAND       → Message starts with # symbol
               Examples: "#trust", "#buy", "#price", "#human", "#catalog"

PURCHASE      → Clear intent to buy, pay, order, or make payment now
               Examples: "i want to buy", "how do i pay", "send account details"

GENERAL       → Business questions not about specific products:
               location, hours, delivery, return policy, warranty

UNKNOWN       → Single ambiguous words ("ok", "hmm", "fine"), gibberish,
               spam, offensive content, or truly unclassifiable input

CLASSIFICATION RULES (follow strictly):
1.  Pidgin: "pls i wan buy generator" = CATALOG_QUERY (product + want)
2.  Pidgin human: "oga i wan see your oga for matter" = HUMAN_REQUEST
3.  Greeting + product in SAME message = CATALOG_QUERY (product wins)
4.  "further enquiries" alone or with any text = HUMAN_REQUEST
5.  "help" alone = HUMAN_REQUEST; "help me find a generator" = CATALOG_QUERY
6.  All-caps messages: classify by CONTENT, not formatting
7.  Single words "ok", "hmm", "fine", "noted" = UNKNOWN
8.  Gibberish / random characters = UNKNOWN
9.  Abusive/offensive messages = UNKNOWN
10. Numbers that are not 1-5 (e.g. "100", phone numbers) = UNKNOWN
11. Empty catalog: all product queries → HUMAN_REQUEST
12. Classify based ONLY on the catalog listed above for this specific business
13. product_query: extract the SIMPLEST possible product name (e.g. "solar panel")
14. "i need information" or "enquiry" alone = HUMAN_REQUEST
15. If PURCHASE intent, set product_query to the item being purchased if identifiable

Respond with ONLY valid JSON — no markdown, no code block, no explanation:
{{"intent": "INTENT_NAME", "product_query": "extracted product name or null", "confidence": 0.0_to_1.0, "reasoning": "one sentence"}}"""


def _build_answer_prompt(
    message: str,
    intent: str,
    catalog: list,
    matched_product: Optional[dict],
    conversation_history: str,
    business_name: str,
    business_niche: str,
    owner_phone: str,
    store_address: str,
) -> str:
    """
    Builds the final answer generation prompt.
    Strictly grounded — the AI can ONLY use data provided here.
    """
    catalog_block = "\n".join([
        f"  • {item.get('name','?')}: ₦{item.get('price',0):,.0f} — {item.get('description','')}"
        for item in catalog if isinstance(item, dict)
    ]) if catalog else "  (No products currently listed)"

    matched_block = ""
    if matched_product and isinstance(matched_product, dict):
        matched_block = f"""
[BEST MATCHING PRODUCT FOUND]:
  Name: {matched_product.get('name', 'Unknown')}
  Price: ₦{matched_product.get('price', 0):,.0f}
  Description: {matched_product.get('description', '')}
  Status: {matched_product.get('status', 'In Stock')}
"""

    return f"""You are {business_name}'s AI assistant on WhatsApp. You ONLY know what is provided below.

[YOUR BUSINESS]:
  Name: {business_name}
  Type: {business_niche}
  Location: {store_address}
  Owner Contact: {owner_phone}
  Hours: Monday to Saturday, 8:00 AM – 6:00 PM WAT

[FULL CATALOG]:
{catalog_block}
{matched_block}
[CONVERSATION HISTORY]:
{conversation_history or "(First message)"}

[CUSTOMER MESSAGE]: "{message}"
[DETECTED INTENT]: {intent}

STRICT RULES — NEVER BREAK THESE:
1. Answer ONLY from the data above. Never invent prices, products, or information.
2. If asked about something NOT in the catalog → respond with exactly: HANDOFF_NEEDED
3. If you cannot answer with 100% certainty → respond with exactly: HANDOFF_NEEDED
4. Never say you are ChatGPT, Claude, Gemini or any other AI. You are {business_name}'s AI.
5. Be warm, professional, concise (2-4 sentences max).
6. Always end catalog answers with: "Reply *#buy* to order or *#human* for manager."
7. For GENERAL questions (location, hours, policy) — answer from business info above.
8. Use ₦ symbol for all prices. Never use $ or USD.

Write your response now (or write HANDOFF_NEEDED):"""


class SovereignAIBrain:
    """
    The central reasoning intelligence for the commerce bot.
    
    Architecture:
    - Intent Classification: Groq Llama 3.3 70B → Gemini Flash 2.0 (fallback)
    - Answer Generation: Groq Llama 3.3 70B → Gemini Flash 2.0 (fallback)  
    - Semantic Catalog Search: Local sentence-transformers (offline, always works)
    - Memory: Redis-cached conversation history
    """

    def __init__(self):
        self.groq = _get_groq_client()
        self.gemini = _get_gemini_client()
        self._model_status = self._check_models()

    def _check_models(self) -> dict:
        status = {
            "groq_available": self.groq is not None,
            "gemini_available": self.gemini is not None,
        }
        if not status["groq_available"] and not status["gemini_available"]:
            logger.error("[SovereignBrain] ⚠️ NO AI MODEL AVAILABLE — all queries will route to human")
        elif status["groq_available"]:
            logger.info("[SovereignBrain] ✅ Primary: Groq Llama 3.3 70B active")
        elif status["gemini_available"]:
            logger.info("[SovereignBrain] ✅ Primary: Gemini Flash 2.0 active (Groq unavailable)")
        return status

    def _call_llm(self, prompt: str, max_tokens: int = 300, temperature: float = 0.1) -> Optional[str]:
        """
        Calls the best available LLM. Groq first (faster/more capable), Gemini fallback.
        Protected by Enterprise ProviderCircuitBreaker & telemetry tracking.
        Returns raw text or None if both fail.
        """
        from circuit_breaker_telemetry import circuit_breaker

        # Try Groq first if circuit is healthy
        if self.groq and circuit_breaker.is_available("groq"):
            t_start = time.time()
            try:
                resp = self.groq.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                lat_ms = (time.time() - t_start) * 1000
                circuit_breaker.record_success("groq", lat_ms)
                return resp.choices[0].message.content.strip()
            except Exception as e:
                err_str = str(e).lower()
                circuit_breaker.record_error("groq", str(e))
                if "rate_limit" in err_str or "429" in err_str:
                    logger.warning(f"[SovereignBrain] Groq rate limited — auto failing over to Gemini")
                else:
                    logger.warning(f"[SovereignBrain] Groq failed, failing over to Gemini: {e}")

        # Gemini fallback with retry on 429 if circuit is healthy
        if self.gemini and circuit_breaker.is_available("gemini"):
            for attempt in range(2):  # 2 attempts: immediate + 1 retry
                t_start = time.time()
                try:
                    from google.genai import types as genai_types
                    resp = self.gemini.models.generate_content(
                        model=GEMINI_MODEL,
                        contents=prompt,
                        config=genai_types.GenerateContentConfig(
                            max_output_tokens=max_tokens,
                            temperature=temperature,
                        )
                    )
                    lat_ms = (time.time() - t_start) * 1000
                    circuit_breaker.record_success("gemini", lat_ms)
                    return resp.text.strip()
                except Exception as e:
                    err_str = str(e)
                    circuit_breaker.record_error("gemini", err_str)
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        if attempt == 0:
                            logger.warning(f"[SovereignBrain] Gemini rate limited, waiting 10s then retrying")
                            time.sleep(10)  # Wait 10s then retry once
                            continue
                        logger.error(f"[SovereignBrain] Gemini quota exhausted — routing to human")
                    else:
                        logger.error(f"[SovereignBrain] Gemini failed: {e}")
                    break

        return None

    def classify_intent(
        self,
        message: str,
        catalog: list,
        conversation_history: str = ""
    ) -> dict:
        """
        Classifies the intent of any customer message using Llama 3.3 70B.
        Returns: {"intent": str, "product_query": str|None, "confidence": float}
        
        Falls back to rule-based classification if LLM is unavailable.
        """
        catalog_names = [
            item.get("name", "") for item in catalog
            if isinstance(item, dict) and item.get("name")
        ]
        prompt = _build_intent_prompt(message, catalog_names, conversation_history)

        raw = self._call_llm(prompt, max_tokens=150, temperature=0.0)

        if raw:
            # Extract JSON from LLM response
            try:
                # Handle markdown code blocks
                json_match = re.search(r'\{.*?\}', raw, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    intent = parsed.get("intent", "UNKNOWN").upper()
                    if intent not in INTENT_SCHEMA:
                        intent = "UNKNOWN"
                    return {
                        "intent": intent,
                        "product_query": parsed.get("product_query"),
                        "confidence": float(parsed.get("confidence", 0.9)),
                        "reasoning": parsed.get("reasoning", ""),
                        "source": "llm"
                    }
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"[SovereignBrain] JSON parse failed: {e} | Raw: {raw[:200]}")

        # ── Deterministic fallback if LLM fails ──
        return self._rule_based_classify(message)

    def _rule_based_classify(self, message: str) -> dict:
        """
        Deterministic fallback classifier. Covers the most common patterns.
        Used when both LLM providers are down or rate-limited.
        """
        m = message.lower().strip()

        # Human request patterns
        human_signals = [
            "human", "manager", "agent", "support", "help", "escalate",
            "speak to", "talk to", "connect me", "further enquiries",
            "more enquiries", "real person", "call me", "i need someone",
            "speak with", "contact"
        ]
        if any(sig in m for sig in human_signals):
            return {"intent": "HUMAN_REQUEST", "product_query": None, "confidence": 0.85, "source": "rules"}

        # Pure greetings (≤3 words, no question)
        greet_words = {"hi", "hello", "hey", "menu", "start", "good morning", "good afternoon", "good evening"}
        if m in greet_words or (len(m.split()) <= 3 and any(m.startswith(g) for g in ["good morning", "good afternoon", "good evening", "hi", "hello", "hey"])):
            return {"intent": "GREETING", "product_query": None, "confidence": 0.95, "source": "rules"}

        # Numeric menu options
        if m in {"1", "2", "3", "4", "5", "#1", "#2", "#3", "#4", "#5"}:
            return {"intent": "MENU_OPTION", "product_query": None, "confidence": 1.0, "source": "rules"}

        # # Commands
        if m.startswith("#"):
            return {"intent": "COMMAND", "product_query": None, "confidence": 1.0, "source": "rules"}

        # Purchase signals
        purchase_words = ["buy", "order", "purchase", "pay", "payment", "place order", "i want to buy"]
        if any(w in m for w in purchase_words):
            return {"intent": "PURCHASE", "product_query": None, "confidence": 0.8, "source": "rules"}

        # Catalog / product inquiry
        catalog_signals = ["do you have", "do you sell", "how much", "price of", "price for",
                           "how many types", "available", "in stock", "solar", "panel", "generator",
                           "power bank", "rice", "gold", "what is your", "show me"]
        if any(sig in m for sig in catalog_signals):
            return {"intent": "CATALOG_QUERY", "product_query": None, "confidence": 0.75, "source": "rules"}

        # General business questions
        general_words = ["address", "location", "where", "open", "close", "hours", "return", "refund", "policy", "deliver"]
        if any(w in m for w in general_words):
            return {"intent": "GENERAL", "product_query": None, "confidence": 0.75, "source": "rules"}

        return {"intent": "UNKNOWN", "product_query": None, "confidence": 0.3, "source": "rules"}

    def generate_answer(
        self,
        message: str,
        intent: str,
        catalog: list,
        matched_product: Optional[dict],
        conversation_history: str,
        tenant: dict,
    ) -> dict:
        """
        Generates a grounded, accurate answer using the best available LLM.
        Enhanced with:
        1. Sub-15ms Semantic Cache lookup
        2. Dynamic Few-Shot Knowledge Exemplar Injection
        3. Post-Generation Fact & Price Verification Guardrail
        """
        from semantic_cache import semantic_cache
        from adaptive_knowledge_memory import adaptive_memory
        from post_generation_auditor import post_auditor

        tenant_id = tenant.get("id", "t-demo")
        business_name = tenant.get("business_name", "Store")
        niche = tenant.get("business_niche", "retail")
        owner_phone = tenant.get("owner_phone", "+234 807 201 5725")
        store_address = tenant.get("store_address", "Onitsha, Anambra State")

        # ── 1. SUB-15MS SEMANTIC CACHE LOOKUP ────────────────────────────
        cached_result = semantic_cache.get(tenant_id, message)
        if cached_result:
            return cached_result

        # ── 2. DYNAMIC FEW-SHOT EXEMPLAR INJECTION ───────────────────────
        few_shot_context = adaptive_memory.format_few_shot_context(tenant_id, message)
        extended_history = f"{few_shot_context}\n{conversation_history}" if few_shot_context else conversation_history

        prompt = _build_answer_prompt(
            message=message,
            intent=intent,
            catalog=catalog,
            matched_product=matched_product,
            conversation_history=extended_history,
            business_name=business_name,
            business_niche=niche,
            owner_phone=owner_phone,
            store_address=store_address,
        )

        raw = self._call_llm(prompt, max_tokens=350, temperature=0.2)

        if not raw:
            # Both LLMs failed → safe human handoff
            return {
                "reply": f"🤖 *[{business_name} AI Assistant]*\n\nThank you for your message! Our store manager will assist you directly right away.",
                "is_human_transfer": True,
                "confidence": 0.0,
                "source": "fallback"
            }

        # Check for explicit handoff signal from AI
        if "HANDOFF_NEEDED" in raw.upper():
            return {
                "reply": None,  # Caller will use human handoff template
                "is_human_transfer": True,
                "confidence": 0.0,
                "source": "ai_handoff"
            }

        # Clean any stray AI artifacts
        clean = re.sub(r'\[TAG:[A-Z_]+\]', '', raw).strip()
        clean = re.sub(r'\[BUTTONS:.*?\]', '', clean, flags=re.DOTALL).strip()

        # ── 3. POST-GENERATION FACT & PRICE AUDIT ───────────────────────
        audited_clean, audit_passed, audit_meta = post_auditor.audit_response(
            ai_response_text=clean,
            catalog=catalog,
            matched_product=matched_product
        )

        result_payload = {
            "reply": f"🤖 *[{business_name} AI Assistant]*\n\n{audited_clean}",
            "is_human_transfer": False,
            "confidence": 0.95 if audit_passed else 0.8,
            "source": "llm",
            "audit": audit_meta
        }

        # ── 4. STORE IN SEMANTIC CACHE FOR FUTURE SUB-15MS RESPONSES ────
        semantic_cache.set(tenant_id, message, result_payload)

        return result_payload

    @property
    def is_operational(self) -> bool:
        """Returns True if at least one LLM provider is available."""
        return self._model_status["groq_available"] or self._model_status["gemini_available"]


# Singleton instance — imported by main.py and character_engine.py
sovereign_brain = SovereignAIBrain()
