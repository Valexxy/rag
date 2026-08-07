import os
import re
from groq import Groq
from database import get_tenant_catalog, get_customer_ledger, get_customer_profile

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL_ID = 'llama-3.1-8b-instant'

def generate_live_character_reply(
    tenant: dict, 
    customer_phone: str, 
    latest_query: str,
    conversation_history: str, 
    is_owner: bool = False
) -> dict:
    """Enterprise Engine using Groq Free Tier with Enhanced Database Bypasses (0% AI Cost)."""
    
    business_name = tenant.get('business_name', 'our company')
    query_lower = latest_query.lower().strip()

    # -------------------------------------------------------------
    # 1. ENHANCED DATABASE BYPASSES (0 AI Cost / Instant Supabase Fetch)
    # -------------------------------------------------------------
    
    # Catalog & Pricing Bypass
    catalog_keywords = ["catalog", "product", "sell", "price", "stock", "item", "list", "what do you sell", "how much"]
    if not is_owner and any(kw in query_lower for kw in catalog_keywords):
        catalog_text = get_tenant_catalog(tenant["id"], search_query=latest_query)
        return {
            "reply": f"🤖 *[{business_name} Client Care]*\n\nHere is our active inventory and price list:\n\n{catalog_text}",
            "buttons": ["📜 View Catalog", "💳 Place Order", "👤 Human Agent"],
            "detected_tags": [],
            "is_high_value": False,
            "is_human_transfer": False
        }

    # Greeting Bypass
    greeting_keywords = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "sup"]
    if not is_owner and query_lower in greeting_keywords:
        return {
            "reply": f"🤖 *[{business_name} Client Care]*\n\nGood day! Welcome to {business_name}. How can we assist you with our products or services today?",
            "buttons": ["📜 View Catalog", "💳 Place Order", "👤 Human Agent"],
            "detected_tags": [],
            "is_high_value": False,
            "is_human_transfer": False
        }

    # Location, Hours, & Contact Bypass
    location_keywords = ["address", "location", "where are you", "office", "store", "open", "closing time", "hours"]
    if not is_owner and any(kw in query_lower for kw in location_keywords):
        return {
            "reply": f"🤖 *[{business_name} Client Care]*\n\nWe operate from our primary distribution warehouse in Onitsha, Anambra State, Nigeria. Open Monday to Saturday, 8:00 AM to 6:00 PM.",
            "buttons": ["📜 View Catalog", "💳 Place Order", "👤 Human Agent"],
            "detected_tags": [],
            "is_high_value": False,
            "is_human_transfer": False
        }

    # -------------------------------------------------------------
    # 2. GROQ LLM API PIPELINE (For complex or unique queries)
    # -------------------------------------------------------------
    catalog = get_tenant_catalog(tenant["id"], search_query=latest_query)
    customer_ledger = get_customer_ledger(tenant["id"], customer_phone)
    profile = get_customer_profile(tenant["id"], customer_phone) if 'get_customer_profile' in globals() else {}

    if is_owner:
        prompt = f"""
You are the Executive Chief of Staff for {business_name}'s owner.
OWNER QUERY: {latest_query}
INVENTORY STOCK: {catalog}
"""
    else:
        known_name = profile.get("full_name") or "Valued Client"
        prompt = f"""
You are the Senior Enterprise Client Experience Executive for {business_name}. 
Evaluate the incoming message using these strict scenario protocols:
1. PERSONAL / FAMILY CHAT: Respond warmly and respectfully without pushing products if it's personal.
2. OUT OF STOCK / SOURCING: Offer pre-order and warehouse import pipelines if an item is out of stock.
3. PRICE HAGGLING: State standard institutional rates, and tag bulk reviews with [TAG:PRICE_NEGOTIATION].
4. COMPLAINT / DISPUTE: Apologize with corporate empathy and trigger [TAG:TRANSFER_HUMAN].
5. HIGH-VALUE WHOLESALE (>= ₦1,000,000): Provide wholesale terms and trigger [TAG:HIGH_VALUE_TRANSACTION].

SENDER PROFILE: {known_name}
LIVE CATALOG: {catalog}
FINANCIAL LEDGER: {customer_ledger}
CONVERSATION HISTORY: {conversation_history}
CLIENT QUERY: {latest_query}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": "You are a professional business executive assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.2
        )
        raw_text = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Groq API error: {e}")
        catalog_fallback = get_tenant_catalog(tenant["id"])
        return {
            "reply": f"🤖 *[{business_name} Client Care]*\n\nWelcome! Here are our available products:\n\n{catalog_fallback}",
            "buttons": ["📜 View Catalog", "👤 Human Agent"],
            "detected_tags": [],
            "is_high_value": False,
            "is_human_transfer": False
        }

    buttons = ["📊 Executive Audit", "⏰ Set Schedule", "📦 Inventory"] if is_owner else ["📜 View Catalog", "💳 Place Order", "👤 Human Agent"]
    button_match = re.search(r"\[BUTTONS:\s*(.*?)\]", raw_text)
    if button_match:
        button_str = button_match.group(1)
        buttons = [b.strip() for b in button_str.split("|") if b.strip()]
        raw_text = re.sub(r"\[BUTTONS:\s*.*?\]", "", raw_text).strip()

    detected_tags = re.findall(r"\[TAG:[A-Z_]+\]", raw_text)
    clean_text = re.sub(r"\[TAG:[A-Z_]+\]", "", raw_text).strip()
    header_title = "Executive Office" if is_owner else "Client Care"
    
    is_high_value = "[TAG:HIGH_VALUE_TRANSACTION]" in detected_tags or any(w in query_lower for w in ["million", "1,000,000", "1m", "carton", "container", "bulk", "wholesale"])
    is_human_transfer = "[TAG:TRANSFER_HUMAN]" in detected_tags or any(w in query_lower for w in ["human", "agent", "manager", "complaint", "refund"])

    return {
        "reply": f"🤖 *[{business_name} {header_title}]*\n\n{clean_text}",
        "buttons": buttons,
        "detected_tags": detected_tags,
        "is_high_value": is_high_value,
        "is_human_transfer": is_human_transfer
    }