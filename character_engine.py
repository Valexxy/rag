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
    """Enterprise Engine enforcing strict catalog knowledge base and payment transfers to human."""
    
    business_name = tenant.get('business_name', 'our company')
    query_lower = latest_query.lower().strip()

    # -------------------------------------------------------------
    # 1. PAYMENT & TRANSACTION ESCALATION BYPASS (Direct to Human)
    # -------------------------------------------------------------
    payment_keywords = ["pay", "payment", "account number", "bank", "transfer", "how do i pay", "send account", "price to pay", "pay stack", "paystack", "pos", "cash"]
    if not is_owner and any(kw in query_lower for kw in payment_keywords):
        return {
            "reply": f"🤖 *[{business_name} Client Care]*\n\nFor payment details and transaction processing, let me connect you directly with our business owner/management. Please hold a moment!",
            "buttons": ["👤 Human Agent"],
            "detected_tags": ["[TAG:TRANSFER_HUMAN]"],
            "is_high_value": False,
            "is_human_transfer": True
        }

    # Catalog & Pricing Bypass
    catalog_keywords = ["catalog", "product", "sell", "price", "stock", "item", "list", "what do you sell", "how much", "power bank"]
    if not is_owner and any(kw in query_lower for kw in catalog_keywords):
        catalog_text = get_tenant_catalog(tenant["id"], search_query=latest_query)
        return {
            "reply": f"🤖 *[{business_name} Client Care]*\n\nHere is our active product catalog and pricing:\n\n{catalog_text}\n\nWould you like to place an order or inquire about any of these items?",
            "buttons": ["💳 Place Order", "👤 Human Agent"],
            "detected_tags": [],
            "is_high_value": False,
            "is_human_transfer": False
        }

    # Greeting Bypass
    greeting_keywords = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "sup"]
    if not is_owner and query_lower in greeting_keywords:
        return {
            "reply": f"🤖 *[{business_name} Client Care]*\n\nGood day! Welcome to {business_name}. How can we assist you with our products today?",
            "buttons": ["📜 View Catalog", "👤 Human Agent"],
            "detected_tags": [],
            "is_high_value": False,
            "is_human_transfer": False
        }

    # Location, Hours, & Contact Bypass
    location_keywords = ["address", "location", "where are you", "office", "store", "open", "closing time", "hours"]
    if not is_owner and any(kw in query_lower for kw in location_keywords):
        return {
            "reply": f"🤖 *[{business_name} Client Care]*\n\nWe operate from our primary distribution facility in Onitsha, Anambra State, Nigeria. Open Monday to Saturday, 8:00 AM to 6:00 PM.",
            "buttons": ["📜 View Catalog", "👤 Human Agent"],
            "detected_tags": [],
            "is_high_value": False,
            "is_human_transfer": False
        }

    # -------------------------------------------------------------
    # 2. GROQ LLM API PIPELINE (Strict Knowledge Base & Escalation)
    # -------------------------------------------------------------
    catalog = get_tenant_catalog(tenant["id"], search_query=latest_query)
    customer_ledger = get_customer_ledger(tenant["id"], customer_phone)
    profile = get_customer_profile(tenant["id"], customer_phone)

    if is_owner:
        prompt = f"""
OWNER QUERY: {latest_query}
INVENTORY: {catalog}
"""
    else:
        known_name = profile.get("full_name") or "Valued Client"
        prompt = f"""
You are the Client Experience Executive for {business_name}.
Strict Rules:
1. Answer customer inquiries strictly using the provided Live Catalog. 
2. Never mention items being 'out of stock'—our warehouse handles demand through sourcing/import pipelines.
3. If the customer asks about payment, bank transfers, account numbers, or closing a transaction, you MUST output [TAG:TRANSFER_HUMAN] so a human agent takes over.
4. If the query goes beyond your catalog knowledge base or requires human negotiation, output [TAG:TRANSFER_HUMAN].
5. Output ONLY the clean customer-facing response text without any internal thoughts.

SENDER PROFILE: {known_name}
LIVE CATALOG: {catalog}
CONVERSATION HISTORY: {conversation_history}
CLIENT QUERY: {latest_query}
"""

    system_instruction = (
        f"You are the Enterprise Client Experience Executive for {business_name}. "
        "CRITICAL INSTRUCTION: Output ONLY final customer-facing text. Never leak reasoning. "
        "If payment or purchase finalization is requested, include [TAG:TRANSFER_HUMAN]."
    )

    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_instruction},
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
            "buttons": ["👤 Human Agent"],
            "detected_tags": ["[TAG:TRANSFER_HUMAN]"],
            "is_high_value": False,
            "is_human_transfer": True
        }

    buttons = ["📊 Executive Audit", "⏰ Set Schedule"] if is_owner else ["📜 View Catalog", "👤 Human Agent"]
    button_match = re.search(r"\[BUTTONS:\s*(.*?)\]", raw_text)
    if button_match:
        button_str = button_match.group(1)
        buttons = [b.strip() for b in button_str.split("|") if b.strip()]
        raw_text = re.sub(r"\[BUTTONS:\s*.*?\]", "", raw_text).strip()

    detected_tags = re.findall(r"\[TAG:[A-Z_]+\]", raw_text)
    clean_text = re.sub(r"\[TAG:[A-Z_]+\]", "", raw_text).strip()
    header_title = "Executive Office" if is_owner else "Client Care"
    
    is_high_value = "[TAG:HIGH_VALUE_TRANSACTION]" in detected_tags or any(w in query_lower for w in ["million", "1,000,000", "1m", "carton", "container", "bulk", "wholesale"])
    is_human_transfer = "[TAG:TRANSFER_HUMAN]" in detected_tags or any(w in query_lower for w in ["human", "agent", "manager", "complaint", "pay", "payment", "bank", "transfer", "account"])

    return {
        "reply": f"🤖 *[{business_name} {header_title}]*\n\n{clean_text}",
        "buttons": buttons,
        "detected_tags": detected_tags,
        "is_high_value": is_high_value,
        "is_human_transfer": is_human_transfer
    }