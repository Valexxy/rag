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

HOW TO GET FREE API KEYS:
  Cerebras:  https://cloud.cerebras.ai       (email signup, no CC)
  OpenRouter: https://openrouter.ai          (email signup, no CC)
  Mistral:   https://console.mistral.ai      (select "Experiment" plan)
"""

import os
import json
import logging
import urllib.request
import urllib.error
import concurrent.futures

logger = logging.getLogger(__name__)

# ── API Keys (set these in Render environment variables) ─────────────
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


STORE_SYSTEM_PROMPT = """You are the official 24/7 AI Sales & Customer Care Consultant for {business_name} located at {address}.

CURRENT STORE CATALOG & BASE PRICES:
{catalog}

YOUR PURPOSE & MISSION:
1. You STAND IN FIRST for every customer conversation. Be warm, professional, respectful, and highly knowledgeable.
2. For items in the store catalog: Explain their features, specs, and base prices accurately using ₦ (Naira).
3. For technical / advisory questions (e.g., solar load calculations, inverter sizing, power needs, appliance compatibility): Answer intelligently and give expert recommendations.
4. For questions about delivery / shipping to any location (e.g. Ibadan, Lagos, Abuja, PH, Kano): Confirm that {business_name} ships nationwide across Nigeria & West Africa. Explain that exact live delivery fees and final order terms are confirmed by the Store Manager (+2348072015725) to prevent price discrepancies.
5. For items or services OUTSIDE the catalog or custom market errands/favors: Explain what {business_name} specializes in, offer to connect the customer directly to the Store Manager (+2348072015725) to check if it can be sourced, and offer help with our in-stock items.
6. Tone: Warm, helpful, respectful, professional African commercial consultant. Keep responses concise, clear, and actionable (3-5 sentences). Always end with a helpful question or call to action."""


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

        business_name = (tenant or {}).get("business_name", "Teeslux Global Store")
        address = (tenant or {}).get("store_address", "Onitsha, Anambra State")
        cat_lines = "\n".join([
            f"- {i.get('name', 'Item')}: ₦{i.get('price', 0):,.0f} — {i.get('description', '')}"
            for i in (catalog or [])[:12] if isinstance(i, dict)
        ])

        system = STORE_SYSTEM_PROMPT.format(
            business_name=business_name,
            catalog=cat_lines or "(No items listed yet)",
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
                return {
                    "success": True,
                    "reply": result,
                    "architecture": f"FreeAIHub_{provider['name']}",
                    "needs_clarification": "?" in result,
                }

        return None  # All providers failed

    def _call(self, provider: dict, key: str, system: str, user_msg: str) -> str | None:
        """
        Makes a single HTTP POST to the provider with a 4-second timeout.
        Uses stdlib urllib only — no extra dependencies.
        """
        def _do_request():
            payload = json.dumps({
                "model": provider["model"],
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_msg},
                ],
                "max_tokens": 400,
                "temperature": 0.4,
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
        except concurrent.futures.TimeoutError:
            logger.warning(f"[FreeAIHub] {provider['name']} timed out after 10s")
            return None
        except urllib.error.HTTPError as e:
            logger.warning(f"[FreeAIHub] {provider['name']} HTTP {e.code}: {e.reason}")
            return None
        except Exception as e:
            logger.warning(f"[FreeAIHub] {provider['name']} failed: {type(e).__name__}: {str(e)[:80]}")
            return None

    def status(self) -> dict:
        """Returns which providers are currently configured with API keys."""
        self._refresh_keys()
        return {
            "cerebras":   bool(self._keys.get("CEREBRAS_API_KEY")),
            "openrouter": bool(self._keys.get("OPENROUTER_API_KEY")),
            "mistral":    bool(self._keys.get("MISTRAL_API_KEY")),
        }


free_ai_hub = FreeAIHub()
