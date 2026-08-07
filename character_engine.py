import os
import re
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from database import get_tenant_catalog, get_customer_ledger, get_customer_profile

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = 'gemini-2.5-flash'

def generate_live_character_reply(
    tenant: dict, 
    customer_phone: str, 
    latest_query: str,
    conversation_history: str, 
    is_owner: bool = False
) -> dict:
    """Enterprise 1M-Scenario Intent Routing & Cognitive Character Engine."""
    
    business_name = tenant.get('business_name', 'our company')
    query_lower = latest_query.lower().strip()

    # Free-Tier Optimization: Direct Catalog Bypass (0 AI Quota Used)
    catalog_keywords = ["catalog", "product", "sell", "price", "stock", "item", "list", "what do you sell"]
    if not is_owner and any(kw in query_lower for kw in catalog_keywords):
        catalog_text = get_tenant_catalog(tenant["id"], search_query=latest_query)
        return {
            "reply": f"🤖 *[{business_name} Client Care]*\n\nHere is our active inventory and price list:\n\n{catalog_text}",
            "buttons": ["📜 View Catalog", "💳 Place Order", "👤 Human Agent"],
            "detected_tags": [],
            "is_high_value": False,
            "is_human_transfer": False
        }

    # Free-Tier Optimization: Direct Greeting Bypass (0 AI Quota Used)
    greeting_keywords = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "sup"]
    if not is_owner and query_lower in greeting_keywords:
        return {
            "reply": f"🤖 *[{business_name} Client Care]*\n\nGood day! Welcome to {business_name}. How can we assist you with our products or services today?",
            "buttons": ["📜 View Catalog", "💳 Place Order", "👤 Human Agent"],
            "detected_tags": [],
            "is_high_value": False,
            "is_human_transfer": False
        }

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
This WhatsApp line handles shared personal and business operations. Evaluate the incoming message using these strict scenario protocols:

1. PERSONAL / FAMILY CHAT SCENARIO: If the sender is asking after the owner personally, catching up, or chatting casually, respond warmly and respectfully on behalf of management without pushing products.
2. OUT OF STOCK / SOURCING SCENARIO: If an item requested is out of stock, inform the client that it can be sourced/pre-ordered through your warehouse import pipeline and offer to lock down a unit.
3. PRICE HAGGLING SCENARIO: If the user asks for a price discount, state that standard institutional rates apply, but offer to escalate bulk orders for management review using [TAG:PRICE_NEGOTIATION].
4. COMPLAINT / DISPUTE SCENARIO: If the user is complaining about delivery delays, damaged goods, or service errors, apologize with profound corporate empathy and immediately trigger [TAG:TRANSFER_HUMAN].
5. HIGH-VALUE WHOLESALE SCENARIO (>= ₦1,000,000): If the inquiry involves bulk cartons, container loads, or major institutional funds, provide professional wholesale terms and trigger [TAG:HIGH_VALUE_TRANSACTION].

SENDER PROFILE: {known_name}
LIVE CATALOG: {catalog}
FINANCIAL LEDGER: {customer_ledger}
CONVERSATION HISTORY: {conversation_history}
CLIENT QUERY: {latest_query}
"""

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=600, temperature=0.2)
        )
        raw_text = response.text.strip()
    except ClientError as ce:
        if "429" in str(ce) or "RESOURCE_EXHAUSTED" in str(ce):
            catalog_fallback = get_tenant_catalog(tenant["id"])
            return {
                "reply": f"🤖 *[{business_name} Client Care]*\n\nOur systems are handling high institutional volume. Here is our active catalog:\n\n{catalog_fallback}",
                "buttons": ["📜 View Catalog", "👤 Human Agent"],
                "detected_tags": [],
                "is_high_value": False,
                "is_human_transfer": False
            }
        raise ce
    except Exception as e:
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