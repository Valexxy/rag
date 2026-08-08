"""
====================================================================
ENTERPRISE CIRCUIT BREAKER & TELEMETRY ENGINE
====================================================================
Tracks rolling latency, request counts, HTTP 429 rate-limit counts, and health
for Groq and Gemini LLM providers. Trips circuit breaker if error rates spike.
"""

import time
import logging
from typing import Dict

logger = logging.getLogger(__name__)

CIRCUIT_TRIP_THRESHOLD_ERRORS = 3
CIRCUIT_COOLDOWN_SECONDS = 60

class ProviderCircuitBreaker:
    """Sliding-window circuit breaker for LLM providers."""

    def __init__(self):
        self._stats = {
            "groq": {"requests": 0, "errors": 0, "consecutive_429s": 0, "tripped_until": 0.0, "total_latency_ms": 0.0},
            "gemini": {"requests": 0, "errors": 0, "consecutive_429s": 0, "tripped_until": 0.0, "total_latency_ms": 0.0},
        }

    def is_available(self, provider: str) -> bool:
        """Returns True if provider circuit breaker is closed (healthy)."""
        p = provider.lower()
        if p not in self._stats:
            return True
        
        now = time.time()
        if self._stats[p]["tripped_until"] > now:
            remaining = int(self._stats[p]["tripped_until"] - now)
            logger.warning(f"[CircuitBreaker] ⚡ Provider '{provider}' circuit is OPEN (cooldown: {remaining}s remaining)")
            return False
        return True

    def record_success(self, provider: str, latency_ms: float):
        """Records successful call and resets error counter."""
        p = provider.lower()
        if p in self._stats:
            self._stats[p]["requests"] += 1
            self._stats[p]["consecutive_429s"] = 0
            self._stats[p]["total_latency_ms"] += latency_ms

    def record_error(self, provider: str, error_msg: str):
        """Records error and trips circuit if threshold exceeded."""
        p = provider.lower()
        if p in self._stats:
            self._stats[p]["requests"] += 1
            self._stats[p]["errors"] += 1
            if "429" in error_msg or "rate_limit" in error_msg.lower() or "resource_exhausted" in error_msg.lower():
                self._stats[p]["consecutive_429s"] += 1

            if self._stats[p]["consecutive_429s"] >= CIRCUIT_TRIP_THRESHOLD_ERRORS:
                self._stats[p]["tripped_until"] = time.time() + CIRCUIT_COOLDOWN_SECONDS
                logger.error(
                    f"[CircuitBreaker] 🚨 TRIPPED CIRCUIT BREAKER for '{provider}' "
                    f"after {self._stats[p]['consecutive_429s']} consecutive 429 errors. Cooling down for 60s."
                )

    def get_telemetry(self) -> Dict[str, dict]:
        """Returns telemetry stats payload for admin monitoring."""
        now = time.time()
        res = {}
        for p, data in self._stats.items():
            reqs = data["requests"]
            avg_lat = (data["total_latency_ms"] / reqs) if reqs > 0 else 0.0
            is_open = data["tripped_until"] > now
            res[p] = {
                "requests": reqs,
                "errors": data["errors"],
                "avg_latency_ms": round(avg_lat, 1),
                "circuit_state": "OPEN (Tripped)" if is_open else "CLOSED (Healthy)",
                "cooldown_remaining_sec": max(0, int(data["tripped_until"] - now)) if is_open else 0
            }
        return res

# Singleton instance
circuit_breaker = ProviderCircuitBreaker()
