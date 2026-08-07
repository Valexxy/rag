import os
import re
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from database import (
    get_tenant_catalog, 
    get_customer_ledger, 
    get_customer_profile, 
    upsert_customer_profile
)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = 'gemini-2.5-flash'

def generate_live_character_reply(
    tenant: dict, 
    customer_phone: str, 
    latest_query: str,
    conversation_history: str, 
    is_owner: bool = False
) -> dict:
    """Smart Free-Tier Engine: Bypasses Gemini for inventory and greetings to save API quota."""
    
    business_name = tenant.get('business_name', 'our company')
    query_lower = latest_query.lower().strip()

    # -------------------------------------------------------------
    # FREE-TIER OPTIMIZATION 1: Direct Catalog Bypass (0 AI Quota Used)
    # -------------------------------------------------------------
    catalog_keywords = ["catalog", "product", "sell", "price", "stock", "item", "list", "what do you sell"]
    if not is_owner and any(kw in query_lower for kw in catalog_keywords):
        catalog_text = get_tenant_catalog(tenant["id"], search_query=latest_query)
        reply_body = f"Here is our current live inventory and price list:\n\n{catalog_text}"
        return {
            "reply": f"🤖 *[{business_name} Client Care]*\n\n{reply_body}",
            "buttons": ["📜 View Catalog", "💳 Place Order", "👤 Human Agent"],
            "detected_tags": [],
            "is_buy_intent": False,
            "is_human_transfer": False
        }

    # -------------------------------------------------------------
    # FREE-TIER OPTIMIZATION 2: Direct Greeting Bypass (0 AI Quota Used)
    # -------------------------------------------------------------
    greeting_keywords = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "sup"]
    if not is_owner and query_lower in greeting_keywords:
        reply_body = f"Good day! Welcome to {business_name}. How can we assist you with our products today?"
        return {
            "reply": f"🤖 *[{business_name} Client Care]*\n\n{reply_body}",
            "buttons": ["📜 View Catalog", "💳 Place Order", "👤 Human Agent"],
            "detected_tags": [],
            "is_buy_intent": False,
            "is_human_transfer": False
        }

    # -------------------------------------------------------------
    # STANDARD GEMINI AI PIPELINE (For complex or specific queries)
    # -------------------------------------------------------------
    catalog = get_tenant_catalog(tenant["id"], search_query=latest_query)
    customer_ledger = get_customer_ledger(tenant["id"], customer_phone)
    profile = get_customer_profile(tenant["id"], customer_phone)

    if is_owner:
        prompt = f"""
You are the Executive Chief of Staff for {business_name}'s owner.
OWNER QUERY: {latest_query}
INVENTORY STOCK: {catalog}
"""
    else:
        known_name = profile.get("full_name") or "Valued Client"
        prompt = f"""
You are the Client Experience Executive for {business_name}.
CLIENT: {known_name}
LIVE CATALOG: {catalog}
LEDGER: {customer_ledger}
QUERY: {latest_query}
"""

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=500, temperature=0.2)
        )
        raw_text = response.text.strip()
    except ClientError as ce:
        if "429" in str(ce) or "RESOURCE_EXHAUSTED" in str(ce):
            print("⚠️ Gemini Free Tier Quota Reached. Serving direct database fallback.")
            catalog_fallback = get_tenant_catalog(tenant["id"])
            return {
                "reply": f"🤖 *[{business_name} Client Care]*\n\nWelcome! Here is our available catalog while our AI assistant rests:\n\n{catalog_fallback}",
                "buttons": ["📜 View Catalog", "👤 Human Agent"],
                "detected_tags": [],
                "is_buy_intent": False,
                "is_human_transfer": False
            }
        raise ce
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        catalog_fallback = get_tenant_catalog(tenant["id"])
        return {
            "reply": f"🤖 *[{business_name} Client Care]*\n\nWelcome! Here are our available products:\n\n{catalog_fallback}",
            "buttons": ["📜 View Catalog", "👤 Human Agent"],
            "detected_tags": [],
            "is_buy_intent": False,
            "is_human_transfer": False
        }

    buttons = ["📊 Daily Audit", "⏰ Add Reminder", "📦 View Stock"] if is_owner else ["📜 View Catalog", "💳 Place Order", "👤 Human Agent"]
    button_match = re.search(r"\[BUTTONS:\s*(.*?)\]", raw_text)
    if button_match:
        button_str = button_match.group(1)
        buttons = [b.strip() for b in button_str.split("|") if b.strip()]
        raw_text = re.sub(r"\[BUTTONS:\s*.*?\]", "", raw_text).strip()

    clean_text = re.sub(r"\[(?:TAG|ACTION):[A-Z_]+\]", "", raw_text).strip()
    header_title = "Executive Assistant" if is_owner else "Client Care"
    
    return {
        "reply": f"🤖 *[{business_name} {header_title}]*\n\n{clean_text}",
        "buttons": buttons,
        "detected_tags": [],
        "is_buy_intent": False,
        "is_human_transfer": False
    }