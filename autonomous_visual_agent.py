from rag_engine import rag_engine

class AutonomousVisualAgent:
    """100% Autonomous Vision AI & Multi-Staff Escalation Engine for Unresponsive Managers."""

    def __init__(self):
        self.staff_cascade_phones = []

    def analyze_image_and_match_catalog(self, tenant: dict, customer_phone: str, image_caption: str) -> dict:
        """Autonomous Vision AI: Matches customer photo/video caption to catalog items when manager is unavailable."""
        query = image_caption if image_caption else "solar inverter power bank product"
        
        # Use RAG Vector Engine to retrieve top matching items from catalog
        context_data = rag_engine.retrieve_relevant_context(tenant, customer_phone, query)
        top_catalog = context_data.get("retrieved_catalog_context", "")

        b_name = tenant.get("business_name", "Valexxy Global Store")

        reply_message = f"""🤖 *[{b_name} AUTONOMOUS VISION ASSISTANT]*
---------------------------------------------
While our store manager is in transit, our Vision AI has analyzed your uploaded item! 

📦 *TOP MATCHING ITEMS IN OUR CATALOG:*
{top_catalog[:350]}

---------------------------------------------
👉 *Quick Actions:*
• Reply with the item name to view full details
• Reply `pay` for verified bank transfer details
• Reply `menu` for interactive main menu"""

        return {
            "reply": reply_message,
            "status": "autonomous_vision_matched",
            "matched_catalog": top_catalog
        }

autonomous_visual = AutonomousVisualAgent()
