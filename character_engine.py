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
    """Enterprise Engine enforcing elite sales closing, factory sourcing pivots, and seamless owner handovers."""
    
    business_name = tenant.get('business_name', 'our company')
    query_lower = latest_query.lower().strip()

    # -------------------------------------------------------------
    # 1. PAYMENT & TRANSACTION ESCALATION BYPASS (Direct to Owner)
    # -------------------------------------------------------------
    payment_keywords = ["pay", "payment", "account number", "bank", "transfer", "how do i pay", "send account", "price to pay", "pay stack", "paystack", "pos", "cash"]
    if not is_owner and any(kw in query_lower for kw in payment_keywords):
        return {
            "reply": f"🤖 *[{business_name} Client Care]*\n\nFantastic! Let me connect you directly with our management/business owner right now to lock down your order details and provide the payment account. Please hold briefly!",
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
            "reply": f"🤖 *[{business_name} Client Care]*\n\nHere is our active product lineup:\n\n{catalog_text}\n\nWhich of these premium options would you like to grab today?",
            "buttons": ["💳 Place Order", "👤 Human Agent"],
            "detected_tags": [],
            "is_high_value": False,
            "is_human_transfer": False
        }

    # Greeting Bypass
    greeting_keywords = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "sup"]
    if not is_owner and query_lower in greeting_keywords:
        return {
            "reply": f"🤖 *[{business_name} Client Care]*\n\nWelcome to {business_name}! We specialize in top-tier gadgets and direct factory-sourced inventory. What are you looking to get today?",
            "buttons": ["📜 View Catalog", "👤 Human Agent"],
            "detected_tags": [],
            "is_high_value": False,
            "is_human_transfer": False
        }

    # Location, Hours, & Contact Bypass
    location_keywords = ["address", "location", "where are you", "office", "store", "open", "closing time", "hours"]
    if not is_owner and any(kw in query_lower for kw in location_keywords):
        return {
            "reply": f"🤖 *[{business_name} Client Care]*\n\nWe operate from our primary distribution facility in Onitsha, Anambra State, Nigeria, and handle direct commercial shipments. Open Monday to Saturday, 8:00 AM to 6:00 PM.",
            "buttons": ["📜 View Catalog", "👤 Human Agent"],
            "detected_tags": [],
            "is_high_value": False,
            "is_human_transfer": False
        }

    # -------------------------------------------------------------
    # 2. GROQ LLM API PIPELINE (Smart Marketer Persona)
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
You are an elite, high-converting commercial sales executive and mini-importation sourcing expert for {business_name}. 

STRICT SALES RULES:
1. NEVER turn a customer away, NEVER say "we don't have it", and NEVER tell them to check an external website.
2. If they request an item, size, or capacity not currently in the catalog (e.g., 50,000mAh, custom items), pitch our direct factory import and pre-order sourcing pipeline enthusiastically ("We can custom-source and ship that exact specification for you through our direct factory pipeline!").
3. Always drive the conversation toward closing the deal and transition them to the business owner by including [TAG:TRANSFER_HUMAN] so the owner can finalize the arrangement and payment.
4. Output ONLY the clean customer-facing response text without any internal reasoning or meta-commentary.

SENDER PROFILE: {known_name}
LIVE CATALOG: {catalog}
CONVERSATION HISTORY: {conversation_history}
CLIENT QUERY: {latest_query}
"""

    system_instruction = (
        f"You are the Elite Sales Closer for {business_name}. "
        "CRITICAL INSTRUCTION: Output ONLY final customer-facing text. Never leak reasoning. "
        "Always upsell or pivot custom/missing requests into factory pre-orders and include [TAG:TRANSFER_HUMAN] to connect them with management."
    )

    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.3
        )
        raw_text = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Groq API error: {e}")
        catalog_fallback = get_tenant_catalog(tenant["id"])
        return {
            "reply": f"🤖 *[{business_name} Client Care]*\n\nWe can source any custom specification you need! Here are our active items:\n\n{catalog_fallback}\n\nLet me connect you with our management to lock down your custom order.",
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
    is_human_transfer = "[TAG:TRANSFER_HUMAN]" in detected_tags or any(w in query_lower for w in ["human", "agent", "manager", "complaint", "pay", "payment", "bank", "transfer", "account", "source", "import", "pre-order"])

    return {
        "reply": f"🤖 *[{business_name} {header_title}]*\n\n{clean_text}",
        "buttons": buttons,
        "detected_tags": detected_tags,
        "is_high_value": is_high_value,
        "is_human_transfer": is_human_transfer
    }