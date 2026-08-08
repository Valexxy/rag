"""
====================================================================
OPENROUTER ENGINE — Free Multi-Model LLM Fallback
====================================================================
OpenRouter provides access to 100+ LLMs via a single API key.
Free models available: Llama 3.1 8B, Qwen 2.5 7B, Mistral 7B, DeepSeek, etc.
Completely separate quota from Groq and Gemini.
Sign up free at: https://openrouter.ai
"""

import os
import logging
import json
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# Free models available on OpenRouter (no cost, just rate limits)
FREE_MODELS = [
    "meta-llama/llama-3.1-8b-instruct:free",   # Meta Llama 3.1 8B — excellent reasoning
    "qwen/qwen-2.5-7b-instruct:free",           # Alibaba Qwen 2.5 7B — strong multilingual
    "mistralai/mistral-7b-instruct:free",        # Mistral 7B — fast, accurate
    "deepseek/deepseek-r1:free",                 # DeepSeek R1 — strong reasoning
]

SALES_SYSTEM_PROMPT = """You are a warm, knowledgeable sales consultant for {business_name}, a Nigerian retail store specializing in {niche}.

Store location: {address}
Business hours: Monday–Saturday, 8:00 AM–6:00 PM WAT

Current catalog:
{catalog}

Your job:
1. Answer the customer's question accurately and warmly, like a real Nigerian store rep.
2. If asking about a product we sell → give the exact price and details.
3. If asking about something we DON'T sell → politely explain what we specialize in, suggest where they can find it in Onitsha, and ask if you can help with something else.
4. If confused or query is broad → ask a friendly clarifying question.
5. Never be silent. Always respond. Keep it concise (3-5 sentences max).
6. Use ₦ for prices. Be warm, professional, Nigerian-style."""


class OpenRouterEngine:
    """
    Calls OpenRouter API to access free LLMs when Groq and Gemini are unavailable.
    Falls back through multiple free models until one succeeds.
    Hard 4-second timeout per model.
    """

    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY", OPENROUTER_API_KEY)
        self.available = bool(self.api_key)

    def generate_reply(self, query: str, tenant: dict, catalog: list, chat_history: str = "") -> dict:
        """
        Tries free OpenRouter models in sequence until one responds.
        Returns a reply dict or None if all fail.
        """
        if not self.available:
            return None

        business_name = tenant.get("business_name", "Store")
        address = tenant.get("store_address", "Onitsha, Anambra State")
        niche = tenant.get("business_niche", "electronics & solar")

        cat_lines = "\n".join([
            f"- {i.get('name', 'Item')}: ₦{i.get('price', 0):,.0f} ({i.get('description', '')})"
            for i in catalog[:12] if isinstance(i, dict)
        ])

        system = SALES_SYSTEM_PROMPT.format(
            business_name=business_name,
            niche=niche,
            address=address,
            catalog=cat_lines or "(No catalog items currently)"
        )

        history_block = f"\nRecent conversation:\n{chat_history[-400:]}\n" if chat_history else ""
        user_msg = f"{history_block}Customer: {query}"

        for model in FREE_MODELS:
            result = self._call_model(model, system, user_msg)
            if result:
                logger.info(f"[OpenRouter] Model '{model}' responded successfully")
                return {
                    "success": True,
                    "reply": result,
                    "architecture": f"OpenRouter_{model.split('/')[1].split(':')[0]}",
                    "needs_clarification": "?" in result
                }

        return None

    def _call_model(self, model: str, system: str, user_msg: str) -> str:
        """
        Makes a single HTTP request to OpenRouter API with 4-second timeout.
        Uses only stdlib urllib — no extra dependencies needed.
        """
        try:
            payload = json.dumps({
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_msg}
                ],
                "max_tokens": 350,
                "temperature": 0.4
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://rag-403h.onrender.com",
                    "X-Title": "Sovereign AI Commerce"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["choices"][0]["message"]["content"].strip()
                return text if text else None

        except urllib.error.HTTPError as e:
            logger.warning(f"[OpenRouter] Model '{model}' HTTP {e.code}: {e.reason}")
            return None
        except Exception as e:
            logger.warning(f"[OpenRouter] Model '{model}' failed: {type(e).__name__}: {e}")
            return None


openrouter_engine = OpenRouterEngine()
