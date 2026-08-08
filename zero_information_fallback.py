from smart_timezone_engine import smart_timezone

class ZeroInformationFallbackEngine:
    """Zero-Hallucination Fallback & Owner Re-Alert Protocol when 0 catalog data exists."""

    @staticmethod
    def format_zero_info_fallback_card(business_name: str, customer_phone: str, query_topic: str) -> dict:
        """Generates transparent, polite fallback card when AI has zero database facts for query."""
        greeting = smart_timezone.get_time_of_day_greeting()

        card_text = f"""📋 *[{business_name} - INQUIRY RECORDED]*
---------------------------------------------
{greeting}! 

I searched our active database records for *{business_name}*, but I could not find verified pricing or specs for:
👉 `"{query_topic}"`

📝 *Actions Taken:*
1️⃣ Your query has been logged as *High Priority Ticket* for store management.
2️⃣ An urgent alert was dispatched to our management team to verify availability.

🤖 *In the meantime, you can:*
• Type `menu` - Explore items in stock
• Type `#news` - Read trade updates
• Leave details here — management will reply directly as soon as they review our store records!"""

        return {
            "reply": card_text,
            "status": "zero_info_fallback_sent",
            "query_topic": query_topic
        }

zero_info_fallback = ZeroInformationFallbackEngine()
