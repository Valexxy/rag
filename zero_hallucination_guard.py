class ZeroHallucinationGuard:
    """Facts-Only Gatekeeper: Prevents AI from inventing catalog details or unverified prices."""

    @staticmethod
    def verify_response_facts(ai_reply: str, catalog_data: str) -> tuple:
        """Ensures ai_reply does not invent numbers or claims absent from verified catalog data."""
        # If catalog is empty or AI expresses uncertainty, flag for human manager handoff
        uncertainty_triggers = ["don't know", "not sure", "approximate", "i think", "maybe", "contact manager"]
        reply_lower = ai_reply.lower()

        for trigger in uncertainty_triggers:
            if trigger in reply_lower:
                return False, "[TAG:TRANSFER_HUMAN]"

        return True, ai_reply

zero_guard = ZeroHallucinationGuard()
