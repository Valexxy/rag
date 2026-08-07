import time
import random
import functools

class SmartRetryEngine:
    """Smart Retry Engine with Realistic Human & Network Jitter Delay."""

    @staticmethod
    def execute_with_smart_retry(func, max_retries: int = 3, base_delay: float = 2.0, *args, **kwargs):
        """Executes a function with realistic jitter delay retries."""
        last_exception = None
        for attempt in range(1, max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    # Calculate realistic human typing/network jitter delay
                    jitter = random.uniform(0.5, 1.5)
                    delay = (base_delay * (2 ** (attempt - 1))) + jitter
                    print(f"[SMART RETRY] Attempt {attempt} failed ({e}). Simulating network delay: {delay:.2f}s before retry...")
                    time.sleep(delay)
                else:
                    print(f"[SMART RETRY FAILED] All {max_retries} attempts exhausted for {func.__name__}.")
                    raise last_exception

smart_retry = SmartRetryEngine()
