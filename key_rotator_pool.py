"""
====================================================================
DYNAMIC AI KEY ROTATOR & POOL MANAGER (v2026)
====================================================================
Manages pools of free API keys across multiple providers:
  - Groq Cloud
  - Cerebras AI
  - Cloudflare Workers AI
  - Google Gemini 2.0 Flash
  - OpenRouter Free Models
  - Mistral AI

Features:
  1. Multi-key Array Parsing: Supports comma-separated keys in env vars
     (e.g., GROQ_API_KEYS="key1,key2,key3")
  2. Automatic Cooldown Management: When a key gets HTTP 429 (Rate Limit),
     it is placed on a temporary 60-second cooldown without dropping requests.
  3. Live Health & Stats Tracking: Real-time tracking of active keys,
     cooldown counts, total requests served, and error counts.
  4. Round-Robin Distribution: Spreads requests evenly across all healthy keys.
"""

import os
import time
import logging
import random
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

COOLDOWN_SECONDS = 60  # Key cooldown duration when hitting 429 Rate Limit


class KeyPool:
    """Manages a pool of API keys for a specific provider."""

    def __init__(self, provider_name: str, env_var_singular: str, env_var_plural: str):
        self.provider_name = provider_name
        self.env_var_singular = env_var_singular
        self.env_var_plural = env_var_plural
        self._keys: List[str] = []
        self._cooldowns: Dict[str, float] = {}  # key -> timestamp when cooldown ends
        self._success_counts: Dict[str, int] = {}
        self._error_counts: Dict[str, int] = {}
        self._index = 0
        self.refresh_keys()

    def refresh_keys(self):
        """Reads keys from environment variables (comma-separated or single)."""
        import base64
        raw_plural = os.environ.get(self.env_var_plural, "")
        raw_singular = os.environ.get(self.env_var_singular, "")

        # Default Base64 Decoded Fallbacks from User Config
        if not raw_plural and not raw_singular:
            if "GROQ" in self.env_var_singular:
                raw_plural = base64.b64decode("Z3NrX0hzOXA3aFN6NmxITjRwZng1ZDlNV0dkeWIzRlllOExKZFdibGVGWmJ2NEdXRmJEbEx3SGcsZ3NrX29yOEluVkxJSHFKRTNQdW1qRDdEV0dkeWIzRlk0bVFOZE5QME9pbXJRUGJrZXU3QkVrOFgsZ3NrX0ZvbWcxS0dwalNKamdYMjRQaUp1V0dkeWIzRllKSXk5NzJaMGs5TUZzRW84a3R3RDlpT1UsZ3NrX2dXb01uZmlmSjV2ek10TTNxUEVxV0dkeWIzRllJem9jTFp4T0NFR3R4QXN0Mno0ZHFsdWw=").decode("utf-8")
            elif "CEREBRAS" in self.env_var_singular:
                raw_plural = base64.b64decode("Y3NrLWMzOGZmOGg2d3dyamRuaDJtZGg5Yzk2d2VmODV4NGpma2Z0a214OGQ5bjZjampyYyxjc2stOGVjd3h3bXRkcjllMmhjbThtaGhtdjhjM21ta3Rtd2t4cHJwdnBqMjk0dmp5a3hyLGNzay1rNTl3NDh4amhtd20ydjV4NmQ2dGg0bjR2NXdyZTR3dG02eDV0aDU0aDk1NnA1amQsY3NrLWRyd3RwcGp5am5yOThweWtqamRqbXk2ZTg0eHdkaHByNDltNHR0ZHB2eW10Y3dtMyxjc2stdHk2M3k5M2M4OGM5cjhrcnB2aGRlOGNjOHBkeXRreHZ4bXJkeXB3dHhyM25oODQz").decode("utf-8")
            elif "OPENROUTER" in self.env_var_singular:
                raw_plural = base64.b64decode("c2stb3ItdjEtNjA2YmM3Yzc3OWE3ZTE0MzhjYTVkYTZkYmQ4NzBiZTQ5ZTVhNDgxOWVjMzZhYzU5ZDhjMDRkOTg1MWYyMjQ5MCxzay1vci12MS1lZDA4MTJiMzA2YTA5MGU3YjA1ZWUwMjcyZTg5MDIyOGYzNzQxNzc0ODAxOTQ4NmE3MGY4ZjY4MGFhOTcwYTI5LHNrLW9yLXYxLWYyM2Y3N2M0MWJhOTJmZjY1ZDBmMWQzNDY4Y2FhNjUwMzlmNzc3MWYwNzM3MGIyNjAyZjczMDE0ZTA1MjI1MjIsc2stb3ItdjEtZDkyNDAwY2M1NzYzMDg1YzVkMjllMDExOTkxNjg4ZDA4N2E3MmI4YWMwMWZjOWFkMjUzMDc1NWUwZmVlYWI2MQ==").decode("utf-8")
            elif "GEMINI" in self.env_var_singular:
                raw_plural = base64.b64decode("QVEuQWI4Uk42SjB5UnViNWdGeGVLcHgxcG0zNGhrSGExbmpBejVfZW9mdzJCVS0xV3lITXcsQVEuQWI4Uk42SVVQV1JvQjV5TXR2enJJU2tnNm5UNWV1YTNqQXJ2UmgzZDV4cGNaV0lFUFEsQVEuQWI4Uk42SnY3blE5R2NsMnRxN00yOW5XX2F4eERFV1dtQ0RGeFRpUlQ2aG5jUi1CREE=").decode("utf-8")
            elif "CF_API_TOKEN" in self.env_var_singular:
                raw_plural = base64.b64decode("Y2Z1dF9GR2tEN1ZLNHQ3UDVkM2duMWw0eERCMFFWS045aWdWNU52aFBLMHdBMGQ4MTczZDAsY2Z1dF9DbnhBWmNUbVZhdXNwRzhHUFZZbExob2tSOEt6TkgzVWlTTDdlQWUwOWMzNDU4OGE=").decode("utf-8")

        parsed_keys = []
        if raw_plural:
            parsed_keys.extend([k.strip() for k in raw_plural.split(",") if k.strip()])
        if raw_singular and raw_singular not in parsed_keys:
            parsed_keys.append(raw_singular.strip())

        # Preserve existing metrics if key already registered
        for k in parsed_keys:
            if k not in self._success_counts:
                self._success_counts[k] = 0
                self._error_counts[k] = 0

        self._keys = parsed_keys

    def get_healthy_key(self) -> Optional[str]:
        """
        Returns a healthy, non-cooldown API key using round-robin.
        Returns None if no keys are configured or all keys are on cooldown.
        """
        self.refresh_keys()
        if not self._keys:
            return None

        now = time.time()
        healthy_keys = [k for k in self._keys if self._cooldowns.get(k, 0) <= now]

        if not healthy_keys:
            logger.warning(f"[{self.provider_name}] All {len(self._keys)} keys are currently on cooldown!")
            return None

        # Round-robin selection
        selected_key = healthy_keys[self._index % len(healthy_keys)]
        self._index += 1
        return selected_key

    def mark_rate_limited(self, key: str, cooldown_duration: int = COOLDOWN_SECONDS):
        """Puts a key on cooldown due to HTTP 429 Rate Limit."""
        now = time.time()
        self._cooldowns[key] = now + cooldown_duration
        self._error_counts[key] = self._error_counts.get(key, 0) + 1
        masked_key = key[:6] + "..." if len(key) > 8 else "key"
        logger.warning(
            f"[{self.provider_name}] Key '{masked_key}' rate-limited (429)! "
            f"Placed on {cooldown_duration}s cooldown."
        )

    def mark_success(self, key: str):
        """Records a successful API call for metrics."""
        self._success_counts[key] = self._success_counts.get(key, 0) + 1

    def status(self) -> dict:
        """Returns diagnostic status of the key pool."""
        self.refresh_keys()
        now = time.time()
        active_count = sum(1 for k in self._keys if self._cooldowns.get(k, 0) <= now)
        cooldown_count = len(self._keys) - active_count
        return {
            "provider": self.provider_name,
            "total_keys": len(self._keys),
            "active_keys": active_count,
            "cooldown_keys": cooldown_count,
            "total_successes": sum(self._success_counts.values()),
            "total_errors": sum(self._error_counts.values()),
        }


class GlobalAIKeyRotator:
    """
    Unified manager for all free AI provider key pools.
    """

    def __init__(self):
        self.groq_pool = KeyPool("Groq", "GROQ_API_KEY", "GROQ_API_KEYS")
        self.cerebras_pool = KeyPool("Cerebras", "CEREBRAS_API_KEY", "CEREBRAS_API_KEYS")
        self.openrouter_pool = KeyPool("OpenRouter", "OPENROUTER_API_KEY", "OPENROUTER_API_KEYS")
        self.mistral_pool = KeyPool("Mistral", "MISTRAL_API_KEY", "MISTRAL_API_KEYS")
        self.gemini_pool = KeyPool("Gemini", "GEMINI_API_KEY", "GEMINI_API_KEYS")
        self.cloudflare_pool = KeyPool("Cloudflare", "CF_API_TOKEN", "CF_API_TOKENS")

    def get_status_report(self) -> dict:
        """Returns overall health metrics across all provider pools."""
        pools = [
            self.groq_pool,
            self.cerebras_pool,
            self.openrouter_pool,
            self.mistral_pool,
            self.gemini_pool,
            self.cloudflare_pool,
        ]
        total_keys = sum(p.status()["total_keys"] for p in pools)
        active_keys = sum(p.status()["active_keys"] for p in pools)

        return {
            "total_keys_configured": total_keys,
            "active_keys_ready": active_keys,
            "providers": {p.provider_name.lower(): p.status() for p in pools},
        }


# Global Singleton Instance
ai_key_rotator = GlobalAIKeyRotator()
