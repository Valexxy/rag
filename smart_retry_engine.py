import random
import functools

class SmartRetryEngine:
    """Smart Retry Engine - zero blocking sleep, fail-fast design for webhook safety."""

    @staticmethod
    def execute_with_smart_retry(func, max_retries: int = 3, base_delay: float = 0.0, *args, **kwargs):
        """
        Executes a function with retries but ZERO blocking sleep.
        Never delays inside a webhook thread — fail fast and let local engine respond.
        """
        last_exception = None
        for attempt in range(1, max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    # Log only, do NOT sleep — webhook must respond in < 5 seconds
                    print(f"[SMART RETRY] Attempt {attempt} failed ({e}). Retrying immediately (no sleep)...")
                else:
                    print(f"[SMART RETRY FAILED] All {max_retries} attempts exhausted for {func.__name__}.")
                    raise last_exception

smart_retry = SmartRetryEngine()
