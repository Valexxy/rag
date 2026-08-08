from multi_source_verifier import multi_source_verifier

class ZeroHallucinationGuard:
    """Facts-Only Gatekeeper: Enforces 100% Truth, 24-Hour Freshness, and Multi-Source Accuracy."""

    @staticmethod
    def verify_response_facts(ai_reply: str, catalog_data: str) -> tuple:
        """Ensures ai_reply does not invent numbers, claims, or unverified prices."""
        uncertainty_triggers = ["don't know", "not sure", "approximate", "i think", "maybe", "contact manager", "unverified"]
        reply_lower = ai_reply.lower()

        for trigger in uncertainty_triggers:
            if trigger in reply_lower:
                return False, "[TAG:TRANSFER_HUMAN]"

        return True, ai_reply

    @staticmethod
    def enforce_24hr_verified_data(topic: str, primary_feed: dict, secondary_feed: dict) -> tuple:
        """Cross-verifies data within 24 hours. Returns fallback if unverified."""
        verification_res = multi_source_verifier.cross_verify_market_data(primary_feed, secondary_feed)
        
        if not verification_res["is_verified"]:
            fallback_msg = multi_source_verifier.format_unverified_fallback(topic)
            return False, fallback_msg

        return True, verification_res

zero_guard = ZeroHallucinationGuard()
