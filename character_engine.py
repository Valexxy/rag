import os
import re
from database import get_tenant_catalog, get_customer_ledger, get_customer_profile

MODEL_ID = 'llama-3.1-8b-instant'

def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        from groq import Groq
        return Groq(api_key=api_key)
    except Exception:
        return None

def get_niche_config(niche: str) -> dict:
    """Maps dynamic business niches to specific triggers and vocabulary."""
    niche = niche.lower() if niche else "retail"
    if niche == "real_estate":
        return {
            "offerings_name": "property portfolio",
            "action_verb": "schedule a viewing or discuss terms",
            "handoff_keywords": ["view", "inspect", "tour", "agent", "buy property", "rent", "lease", "pay", "yes"]
        }
    elif niche == "service" or niche == "salon":
        return {
            "offerings_name": "list of services",
            "action_verb": "book an appointment",
            "handoff_keywords": ["book", "appointment", "schedule", "time", "date", "pay", "yes"]
        }
    else: # Default Retail/Importation
        return {
            "offerings_name": "product lineup",
            "action_verb": "finalize your request",
            "handoff_keywords": ["pay", "payment", "account", "bank", "transfer", "pos", "cash", "custom", "source", "import", "order", "buy", "yes"]
        }

def generate_live_character_reply(
    tenant: dict, 
    customer_phone: str, 
    latest_query: str,
    conversation_history: str, 
    is_owner: bool = False
) -> dict:
    """Deterministic routing engine that leans less on AI for core logic."""
    
    business_name = tenant.get('business_name', 'our company')
    niche = tenant.get('business_niche', 'retail')
    config = get_niche_config(niche)
    query_lower = latest_query.lower().strip()

    # -------------------------------------------------------------
    # 1. DETERMINISTIC HANDOFF (Zero AI Cost, Instant, Perfect Accuracy)
    # -------------------------------------------------------------
    if not is_owner and any(kw in query_lower for kw in config["handoff_keywords"]):
        return {
            "reply": f"🤖 *[{business_name} Automated System]*\n\nConnecting you directly with management to {config['action_verb']}. Please hold!",
            "buttons": ["👤 Human Agent"],
            "detected_tags": ["[TAG:TRANSFER_HUMAN]"],
            "is_high_value": False,
            "is_human_transfer": True
        }

    # -------------------------------------------------------------
    # 2. DETERMINISTIC CATALOG DISCOVERY (Zero AI Cost, Instant)
    # -------------------------------------------------------------
    discovery_keywords = ["catalog", "price", "list", "what do you", "how much", "offer", "options", "services", "properties", "items", "types", "power bank"]
    if not is_owner and any(kw in query_lower for kw in discovery_keywords):
        catalog_text = get_tenant_catalog(tenant)
        return {
            "reply": f"🤖 *[{business_name} Automated System]*\n\nHere is our active {config['offerings_name']}:\n\n{catalog_text}\n\nWould you like to {config['action_verb']}?",
            "buttons": ["👤 Human Agent"],
            "detected_tags": [],
            "is_high_value": False,
            "is_human_transfer": False
        }

    # Location & Hours Bypass
    location_keywords = ["address", "location", "where are you", "office", "store", "open", "closing time", "hours"]
    if not is_owner and any(kw in query_lower for kw in location_keywords):
        return {
            "reply": f"🤖 *[{business_name} Automated System]*\n\nWe operate from Onitsha, Anambra State. Open Monday to Saturday, 8:00 AM to 6:00 PM.",
            "buttons": ["👤 Human Agent"],
            "detected_tags": [],
            "is_high_value": False,
            "is_human_transfer": False
        }

    # -------------------------------------------------------------
    # 3. LLM CONVERSATIONAL FALLBACK (For everything else)
    # -------------------------------------------------------------
    catalog = get_tenant_catalog(tenant)
    profile = get_customer_profile(tenant["id"], customer_phone)

    if is_owner:
        prompt = f"OWNER QUERY: {latest_query}\nINVENTORY: {catalog}"
    else:
        known_name = profile.get("full_name") or "Valued Client"
        prompt = f"""
        You are the front-desk router for {business_name}, a {niche} business.
        If the user's intent is to {config['action_verb']} or request something outside the catalog, output [TAG:TRANSFER_HUMAN].
        Otherwise, answer their basic question politely using this data: {catalog}.
        Keep it strictly to 1 short sentence.
        
        USER: {latest_query}
        """

    system_instruction = (
        f"You are the Assistant for {business_name}. "
        "CRITICAL: Be extremely concise (1 sentence max). Instantly route any purchase, payment, or custom request to the owner using [TAG:TRANSFER_HUMAN]."
    )

    client = get_groq_client()
    if not client:
        return {
            "reply": f"🤖 *[{business_name} Automated System]*\n\nConnecting you directly with management now. Please hold!",
            "buttons": ["👤 Human Agent"],
            "detected_tags": ["[TAG:TRANSFER_HUMAN]"],
            "is_high_value": False,
            "is_human_transfer": True
        }

    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.1
        )
        raw_text = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[ERROR] Groq API error: {e}")
        return {
            "reply": f"🤖 *[{business_name} Automated System]*\n\nConnecting you directly with management now. Please hold!",
            "buttons": ["👤 Human Agent"],
            "detected_tags": ["[TAG:TRANSFER_HUMAN]"],
            "is_high_value": False,
            "is_human_transfer": True
        }

    buttons = ["📊 Executive Audit", "⏰ Set Schedule"] if is_owner else ["👤 Human Agent"]
    button_match = re.search(r"\[BUTTONS:\s*(.*?)\]", raw_text)
    if button_match:
        button_str = button_match.group(1)
        buttons = [b.strip() for b in button_str.split("|") if b.strip()]
        raw_text = re.sub(r"\[BUTTONS:\s*.*?\]", "", raw_text).strip()

    detected_tags = re.findall(r"\[TAG:[A-Z_]+\]", raw_text)
    clean_text = re.sub(r"\[TAG:[A-Z_]+\]", "", raw_text).strip()
    header_title = "Executive Office" if is_owner else "Automated System"
    
    is_high_value = "[TAG:HIGH_VALUE_TRANSACTION]" in detected_tags
    is_human_transfer = "[TAG:TRANSFER_HUMAN]" in detected_tags

    return {
        "reply": f"🤖 *[{business_name} {header_title}]*\n\n{clean_text}",
        "buttons": buttons,
        "detected_tags": detected_tags,
        "is_high_value": is_high_value,
        "is_human_transfer": is_human_transfer
    }