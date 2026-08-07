import time
import random
import re

class MetaAntiBanGuardrail:
    """Meta WhatsApp Policy Compliance & Anti-Ban Shield."""

    def __init__(self):
        self.message_counter = 0
        self.last_send_timestamp = 0.0

    def calculate_human_jitter_delay(self) -> float:
        """Simulates human typing & network variance (3 to 7 seconds delay between broadcast messages)."""
        return round(random.uniform(3.0, 7.0), 2)

    def is_within_rate_limit(self, max_per_minute: int = 15) -> bool:
        """Enforces Meta policy speed limits (max 15 messages per minute per instance)."""
        now = time.time()
        if now - self.last_send_timestamp < 60.0:
            if self.message_counter >= max_per_minute:
                return False
            self.message_counter += 1
        else:
            self.message_counter = 1
            self.last_send_timestamp = now
        return True

    def randomize_broadcast_template(self, text: str, recipient_phone: str) -> str:
        """Variates message wording slightly so spam detection algorithms do not flag duplicate strings."""
        salutations = ["Hello", "Hi", "Greetings", "Good day"]
        chosen_greeting = random.choice(salutations)
        
        # Insert zero-width spaces or subtle variations to prevent exact hash matching by Meta
        random_suffix = "".join([chr(8203) for _ in range(random.randint(1, 4))])
        
        return f"{chosen_greeting}! {text}{random_suffix}"

antiban_guard = MetaAntiBanGuardrail()
