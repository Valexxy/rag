"""
====================================================================
FREE AI HUB — Cerebras + OpenRouter + Mistral Unified Reasoning Engine
====================================================================
Three completely separate free AI providers chained as one hub:

  1. Cerebras AI  — llama-3.3-70b @ ~1M tokens/day, ~2000 tok/s (fastest free AI)
  2. OpenRouter   — llama-3.3-70b:free / deepseek-chat:free (50+ models, rotating)
  3. Mistral AI   — mistral-small-latest (free experiment tier, ~1 req/sec)

All use the same OpenAI-compatible API format.
All have 4-second hard timeouts — no blocking sleep anywhere.
All are completely separate from Groq and Gemini quotas.
"""

import os
import json
import logging
import urllib.request
import urllib.error
import concurrent.futures

logger = logging.getLogger(__name__)

# ── API Keys ──────────────────────────────────────────────────────────
CEREBRAS_API_KEY  = os.environ.get("CEREBRAS_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MISTRAL_API_KEY   = os.environ.get("MISTRAL_API_KEY", "")

# ── Provider configurations ───────────────────────────────────────────
PROVIDERS = [
    {
        "name": "OpenRouter_Auto",
        "key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "openrouter/auto",
        "headers": lambda key: {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://rag-403h.onrender.com",
            "X-Title": "Sovereign AI Commerce",
        },
    },
    {
        "name": "OpenRouter_DeepSeek",
        "key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "deepseek/deepseek-r1:free",
        "headers": lambda key: {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://rag-403h.onrender.com",
            "X-Title": "Sovereign AI Commerce",
        },
    },
    {
        "name": "Cerebras",
        "key_env": "CEREBRAS_API_KEY",
        "base_url": "https://api.cerebras.ai/v1/chat/completions",
        "model": "llama-3.3-70b",
        "headers": lambda key: {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    },
]


STORE_SYSTEM_PROMPT = """You are the official Executive AI Sales & Customer Care Consultant for {business_name} located at {address}.

CURRENT LIVE SUPABASE PRODUCT CATALOG & OFFICIAL PRICES:
{catalog}

STRICT COMMERCIAL CONSTITUTION & OPERATIONAL BOUNDARIES:

1. PRODUCT PRICE BOUNDARY (STRICT RULE):
   - The ONLY costs/prices you are authorized to state are the exact product prices listed in the Live Supabase Catalog above.
   - Quoting any product price not in the database is strictly forbidden.

2. ZERO EXTRA COST QUOTING RULE (MANDATORY HUMAN HANDOVER):
   - You are STRICTLY PROHIBITED from stating or guessing any shipping fee, waybill cost, delivery fee, installation charge, or bulk discount.
   - If a customer asks about ANY non-product cost (e.g., "how much for shipping to Sapele/Lagos/Abuja?", "what is the waybill fee?", "how much for installation?"):
     a) Stating the product price is allowed if relevant.
     b) Inform the customer warmly and respectfully that all delivery, waybill, and installation costs are custom-calculated and finalized exclusively by our Human Store Manager (+2348072015725) to guarantee the exact lowest rate for their location.
     c) Append `[TRANSFER_HUMAN]` at the end of your response so our human manager is alerted instantly.

3. SENSITIVE CONVERSATIONAL TONE & SENTIMENT MATCHING:
   - Always maintain a warm, executive, highly respectful, and empathetic African commercial tone.
   - Use clean, elegant formatting with bolding (*like this*) and appropriate professional emojis.
   - Respond in concise, clear, and actionable paragraphs (2 to 4 sentences).

4. TECHNICAL & ADVISORY INTELLIGENCE:
   - Provide expert advice on solar sizing, inverter capacity, power bank battery needs, and product compatibility based on catalog specs.

5. PAYMENT INTEGRITY & ANTI-DIVERSION:
   - Never provide personal bank accounts. Payments are processed exclusively through official virtual accounts or verified store checkout.

6. HUMAN ESCALATION TRIGGER:
   - If user asks for human manager, expresses complaint, asks for waybill/shipping fees, or requests personal bank details, append `[TRANSFER_HUMAN]`.
"""


class FreeAIHub:
    """
    Unified hub for Cerebras + OpenRouter + Mistral free AI APIs.
    Tries providers in order, uses first successful response.
    All calls have 4-second hard timeouts.
    """

    def __init__(self):
        self._keys = {
            "CEREBRAS_API_KEY":   CEREBRAS_API_KEY,
            "OPENROUTER_API_KEY": OPENROUTER_API_KEY,
            "MISTRAL_API_KEY":    MISTRAL_API_KEY,
        }

    def _refresh_keys(self):
        """Re-read env vars or active key pools."""
        try:
            from key_rotator_pool import ai_key_rotator
            c_key = os.environ.get("CEREBRAS_API_KEY") or ai_key_rotator.cerebras_pool.get_healthy_key() or ""
            o_key = os.environ.get("OPENROUTER_API_KEY") or ai_key_rotator.openrouter_pool.get_healthy_key() or ""
            m_key = os.environ.get("MISTRAL_API_KEY") or ai_key_rotator.mistral_pool.get_healthy_key() or ""
        except Exception:
            c_key = os.environ.get("CEREBRAS_API_KEY", "")
            o_key = os.environ.get("OPENROUTER_API_KEY", "")
            m_key = os.environ.get("MISTRAL_API_KEY", "")

        self._keys = {
            "CEREBRAS_API_KEY": c_key,
            "OPENROUTER_API_KEY": o_key,
            "MISTRAL_API_KEY": m_key,
        }

    def generate_reply(
        self,
        query: str,
        tenant: dict = None,
        catalog: list = None,
        chat_history: str = ""
    ) -> dict | None:
        """
        Tries Cerebras → OpenRouter (Llama) → OpenRouter (DeepSeek) → Mistral.
        Returns the first successful response or None if all fail.
        """
        self._refresh_keys()

        business_name = (tenant or {}).get("business_name", "Teeslux Global Electronics & Solar")
        address = (tenant or {}).get("store_address", "Onitsha Main Market, Anambra State")

        # Format Supabase catalog items
        cat_lines = []
        if isinstance(catalog, list):
            for i in catalog[:12]:
                if isinstance(i, dict):
                    cat_lines.append(f"- {i.get('name', 'Item')}: ₦{i.get('price', 0):,.2f} — {i.get('description', '')}")

        system = STORE_SYSTEM_PROMPT.format(
            business_name=business_name,
            catalog="\n".join(cat_lines) if cat_lines else "(Catalog loading from Supabase DB...)",
            address=address
        )

        history = f"\nRecent chat:\n{chat_history[-400:]}\n" if chat_history else ""
        user_msg = f"{history}Customer: {query}"

        for provider in PROVIDERS:
            key = self._keys.get(provider["key_env"], "")
            if not key:
                logger.debug(f"[FreeAIHub] Skipping {provider['name']} — no API key set")
                continue

            result = self._call(provider, key, system, user_msg)
            if result:
                logger.info(f"[FreeAIHub] ✅ {provider['name']} responded successfully")

                is_transfer = "[TRANSFER_HUMAN]" in result or "TRANSFER_HUMAN" in result
                clean_reply = result.replace("[TRANSFER_HUMAN]", "").replace("TRANSFER_HUMAN", "").strip()

                return {
                    "success": True,
                    "reply": clean_reply,
                    "architecture": f"FreeAIHub_{provider['name']}",
                    "is_human_transfer": is_transfer,
                    "needs_clarification": "?" in clean_reply,
                }

        return None

    def _call(self, provider: dict, key: str, system: str, user_msg: str) -> str | None:
        """
        Makes a single HTTP POST to the provider with a 10-second timeout.
        """
        def _do_request():
            payload = json.dumps({
                "model": provider["model"],
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_msg},
                ],
                "max_tokens": 400,
                "temperature": 0.3,
            }).encode("utf-8")

            headers = provider["headers"](key)
            req = urllib.request.Request(
                provider["base_url"],
                data=payload,
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["choices"][0]["message"]["content"].strip()
                return text if text else None

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                return ex.submit(_do_request).result(timeout=10.5)
        except Exception as e:
            logger.warning(f"[FreeAIHub] {provider['name']} error: {e}")
            return None


free_ai_hub = FreeAIHub()
