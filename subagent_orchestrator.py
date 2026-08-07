class SubagentOrchestrator:
    """Delegates customer queries to parallel specialized sub-agents."""

    @staticmethod
    def route_to_agent(intent: str, query: str) -> str:
        """Determines which autonomous sub-agent should handle the request."""
        if intent == "PURCHASE":
            return "SALES_AGENT"
        elif intent == "LOGISTICS":
            return "LOGISTICS_AGENT"
        elif intent == "BOOKING":
            return "BOOKING_AGENT"
        elif intent == "SUPPORT":
            return "SUPPORT_AGENT"
        return "GENERAL_AGENT"

subagent_orchestrator = SubagentOrchestrator()
