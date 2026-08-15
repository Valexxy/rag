"""
====================================================================
HIGH PERFORMANCE CACHE v2026
====================================================================
Redis-based Idempotency Locks, Human Takeover Circuit Breaker,
24-Hour Customer Interaction Window, and NIBSS Downtime Handler.
Includes in-memory fallback for local dev environments.
====================================================================
"""

import os
import time
import logging
from typing import Optional

logger = logging.getLogger("HighPerformanceCache")

# ── Try to connect to Redis ───────────────────────────────────────────────
REDIS_URL = os.environ.get("REDIS_URL", "")
_redis_client = None

try:
    if REDIS_URL:
        import redis
        _redis_client = redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=2)
        _redis_client.ping()
        logger.info("[Cache] ✅ Redis connected successfully")
except Exception as e:
    logger.warning(f"[Cache] ⚠️ Redis unavailable — using in-memory fallback: {e}")
    _redis_client = None

# ── In-memory fallback store ──────────────────────────────────────────────
_memory_store: dict = {}


def _set(key: str, value: str, ex: int = 86400) -> bool:
    """Set a key with expiry. Returns False if key already exists (nx behavior)."""
    if _redis_client:
        return bool(_redis_client.set(key, value, nx=True, ex=ex))
    now = time.time()
    if key in _memory_store:
        if _memory_store[key]["expires"] > now:
            return False  # Key exists and not expired
    _memory_store[key] = {"value": value, "expires": now + ex}
    return True


def _get(key: str) -> Optional[str]:
    if _redis_client:
        return _redis_client.get(key)
    now = time.time()
    entry = _memory_store.get(key)
    if entry and entry["expires"] > now:
        return entry["value"]
    return None


def _delete(key: str):
    if _redis_client:
        _redis_client.delete(key)
    else:
        _memory_store.pop(key, None)


# ── IDEMPOTENCY LOCK ─────────────────────────────────────────────────────
class RedisIdempotencyManager:
    """Prevents duplicate webhook execution using unique event IDs."""

    def check_and_lock(self, event_id: str) -> bool:
        """
        Returns True if event is NEW (should be processed).
        Returns False if event has already been processed (duplicate — drop).
        Sets a 24-hour idempotency lock.
        """
        acquired = _set(f"idempotency:{event_id}", "1", ex=86400)
        if not acquired:
            logger.warning(f"[Idempotency] Duplicate event dropped: {event_id}")
        return acquired


# ── HUMAN TAKEOVER CIRCUIT BREAKER ───────────────────────────────────────
class HumanTakeoverCircuitBreaker:
    """Activates/deactivates AI mute for a specific customer phone number."""

    TAKEOVER_TTL = 86400  # 24 hours default

    TAKEOVER_TRIGGERS = [
        "human", "agent", "manager", "owner", "call me", "scam",
        "fraud", "speak to someone", "real person", "wahala",
        "i want to talk", "connect me", "get me your boss"
    ]

    def is_muted(self, tenant_id: str, phone: str) -> bool:
        return _get(f"takeover:{tenant_id}:{phone}") == "1"

    def activate(self, tenant_id: str, phone: str):
        _set(f"takeover:{tenant_id}:{phone}", "1", ex=self.TAKEOVER_TTL)
        logger.info(f"[Takeover] AI muted for {phone}")

    def deactivate(self, tenant_id: str, phone: str):
        _delete(f"takeover:{tenant_id}:{phone}")
        logger.info(f"[Takeover] AI unmuted for {phone}")

    def should_trigger(self, text: str) -> bool:
        q = text.lower()
        return any(t in q for t in self.TAKEOVER_TRIGGERS)


# ── 24-HOUR CUSTOMER INTERACTION WINDOW ──────────────────────────────────
class CustomerWindowManager:
    """
    Tracks last interaction timestamp per customer per tenant.
    Messages older than 24 hours should use Meta utility templates.
    """

    WINDOW_TTL = 86400  # 24 hours

    def record_interaction(self, tenant_id: str, phone: str):
        _set(f"window:{tenant_id}:{phone}", str(int(time.time())), ex=self.WINDOW_TTL)

    def is_within_window(self, tenant_id: str, phone: str) -> bool:
        val = _get(f"window:{tenant_id}:{phone}")
        if not val:
            return False
        last_seen = int(val)
        return (time.time() - last_seen) < self.WINDOW_TTL

    def force_refresh(self, tenant_id: str, phone: str):
        _delete(f"window:{tenant_id}:{phone}")
        self.record_interaction(tenant_id, phone)


# ── NIBSS PAYMENT PENDING QUEUE ───────────────────────────────────────────
class NIBSSPendingQueue:
    """
    Holds orders in PENDING_SETTLEMENT status when NIBSS interbank
    network is slow or experiencing downtime. Prevents false failures.
    """

    def enqueue(self, reference: str, metadata: dict, ttl: int = 7200):
        import json
        _set(f"nibss_pending:{reference}", json.dumps(metadata), ex=ttl)
        logger.info(f"[NIBSS Queue] Order {reference} queued for settlement polling")

    def get(self, reference: str) -> Optional[dict]:
        import json
        val = _get(f"nibss_pending:{reference}")
        return json.loads(val) if val else None

    def clear(self, reference: str):
        _delete(f"nibss_pending:{reference}")
        logger.info(f"[NIBSS Queue] Order {reference} cleared from pending queue")


# ── Singletons ─────────────────────────────────────────────────────────────
idempotency_manager = RedisIdempotencyManager()
human_takeover = HumanTakeoverCircuitBreaker()
customer_window = CustomerWindowManager()
nibss_queue = NIBSSPendingQueue()
