"""
====================================================================
CLOUDFLARE WORKERS AI ENGINE
====================================================================
Llama 3.3 70B running on Cloudflare's global GPU network.
- 100% free, 10,000 neurons/day (~2,000+ WhatsApp replies/day)
- Resets every 24 hours — no monthly cap
- You own the configuration — Cloudflare runs the GPU
- No token restrictions within the daily allowance
- Sub-second response time on Cloudflare edge

HOW TO SET UP (5 minutes, free, no credit card):
  1. Sign up at https://dash.cloudflare.com (free account)
  2. Your Account ID is shown in the right sidebar under "Workers & Pages"
  3. Go to My Profile → API Tokens → Create Token
     → Use "Workers AI" template OR custom token with "Workers AI: Edit"
  4. Add to Render environment variables:
       CF_ACCOUNT_ID=your_account_id_here
       CF_API_TOKEN=your_api_token_here

ENDPOINT USED:
  POST https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/{MODEL}
  Response format: { "result": { "response": "..." }, "success": true }
"""

import os
import json
import logging
import urllib.request
import urllib.error
import concurrent.futures

logger = logging.getLogger(__name__)

# ── Model selection ───────────────────────────────────────────────────
# Best available on Cloudflare Workers AI (fast, smart, free):
CF_PRIMARY_MODEL   = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"   # Best reasoning
CF_FALLBACK_MODEL  = "@cf/meta/llama-3.1-8b-instruct-fast"         # Fast backup
CF_FALLBACK2_MODEL = "@cf/qwen/qwen3-30b-a3b-fp8"                  # Alternative

STORE_SYSTEM_PROMPT = """You are a warm, highly knowledgeable sales consultant for {business_name}, a Nigerian store in Onitsha, Anambra State specializing in {niche}.

Store address: {address}
Business hours: Monday–Saturday, 8:00 AM–6:00 PM WAT

Current catalog:
{catalog}

YOUR RULES:
1. Answer warmly and naturally — like a real Nigerian store representative.
2. For items IN catalog → give exact name, price (₦), and details directly from the list above.
3. For items NOT in catalog → politely clarify what you specialize in, recommend where to find it in Onitsha Market, and offer to help with something else.
4. If the query is vague or broad → ask a friendly, specific clarifying question.
5. NEVER be silent. NEVER drop the customer. Be concise (3–5 sentences max).
6. Nigerian English tone: warm, professional, natural. Use ₦ for all prices."""


class CloudflareWorkersAI:
    """
    Calls Cloudflare Workers AI REST API — Llama 3.3 70B on Cloudflare GPU.
    No token restrictions within 10K neurons/day free allowance.
    All calls have 4-second hard timeouts.
    """

    def __init__(self):
        self._account_id = os.environ.get("CF_ACCOUNT_ID", "")
        self._api_token  = os.environ.get("CF_API_TOKEN", "")

    @property
    def is_configured(self) -> bool:
        """Returns True if both CF_ACCOUNT_ID and CF_API_TOKEN are set."""
        self._account_id = os.environ.get("CF_ACCOUNT_ID", "")
        self._api_token  = os.environ.get("CF_API_TOKEN", "")
        return bool(self._account_id and self._api_token)

    def generate_reply(
        self,
        query: str,
        tenant: dict,
        catalog: list,
        chat_history: str = ""
    ) -> dict | None:
        """
        Sends query to Cloudflare Workers AI (Llama 3.3 70B on CF GPU).
        Falls back through model list if primary model fails.
        Returns None if not configured or all models fail.
        """
        if not self.is_configured:
            logger.debug("[CloudflareAI] Skipping — CF_ACCOUNT_ID / CF_API_TOKEN not set")
            return None

        business_name = (tenant or {}).get("business_name", "Teeslux Global Store")
        address       = (tenant or {}).get("store_address", "Onitsha, Anambra State")
        niche         = (tenant or {}).get("business_niche", "electronics & solar energy")

        cat_lines = "\n".join([
            f"- {i.get('name', 'Item')}: ₦{i.get('price', 0):,.0f} — {i.get('description', '')}"
            for i in (catalog or [])[:14] if isinstance(i, dict)
        ])

        system = STORE_SYSTEM_PROMPT.format(
            business_name=business_name,
            niche=niche,
            address=address,
            catalog=cat_lines or "(No catalog items yet)"
        )

        history = f"\nRecent conversation:\n{chat_history[-500:]}\n" if chat_history else ""
        user_msg = f"{history}Customer asked: {query}"

        for model in [CF_PRIMARY_MODEL, CF_FALLBACK_MODEL, CF_FALLBACK2_MODEL]:
            result = self._call(model, system, user_msg)
            if result:
                logger.info(f"[CloudflareAI] ✅ Responded using model: {model}")
                return {
                    "success": True,
                    "reply": result,
                    "architecture": f"Cloudflare_WorkersAI_{model.split('/')[-1]}",
                    "needs_clarification": "?" in result,
                }

        return None

    def _call(self, model: str, system: str, user_msg: str) -> str | None:
        """
        Makes a single POST to Cloudflare Workers AI REST API with 4-second timeout.
        Uses stdlib urllib — no extra dependencies.
        """
        url = (
            f"https://api.cloudflare.com/client/v4/accounts"
            f"/{self._account_id}/ai/run/{model}"
        )

        def _do_request():
            payload = json.dumps({
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user_msg},
                ],
                "max_tokens": 400,
                "temperature": 0.4,
            }).encode("utf-8")

            req = urllib.request.Request(
                url,
                data=payload,
                headers={
                    "Authorization": f"Bearer {self._api_token}",
                    "Content-Type":  "application/json",
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8"))

                # Cloudflare response format: {"result": {"response": "..."}, "success": true}
                if data.get("success") and data.get("result"):
                    result = data["result"]
                    # Native format
                    if isinstance(result, dict) and result.get("response"):
                        return result["response"].strip()
                    # OpenAI-compat format (if CF switches)
                    if isinstance(result, dict) and result.get("choices"):
                        return result["choices"][0]["message"]["content"].strip()

                return None

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                return ex.submit(_do_request).result(timeout=4.5)

        except concurrent.futures.TimeoutError:
            logger.warning(f"[CloudflareAI] Model '{model}' timed out after 4s")
            return None
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8")[:120]
            except Exception:
                pass
            if e.code == 429:
                logger.warning(f"[CloudflareAI] Daily neuron limit hit (429) — neurons exhausted")
            else:
                logger.warning(f"[CloudflareAI] HTTP {e.code}: {e.reason} — {body}")
            return None
        except Exception as e:
            logger.warning(f"[CloudflareAI] Failed: {type(e).__name__}: {str(e)[:80]}")
            return None

    def status(self) -> dict:
        """Returns current configuration status."""
        return {
            "configured":  self.is_configured,
            "account_id":  bool(self._account_id),
            "api_token":   bool(self._api_token),
            "primary_model": CF_PRIMARY_MODEL,
        }


cloudflare_ai = CloudflareWorkersAI()
