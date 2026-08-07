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
    """Generates dual-engine AI responses with 429 rate-limit fallback safety."""
    
    catalog = get_tenant_catalog(tenant["id"], search_query=latest_query)
    customer_ledger = get_customer_ledger(tenant["id"], customer_phone)
    profile = get_customer_profile(tenant["id"], customer_phone)
    business_name = tenant.get('business_name', 'our company')

    if is_owner:
        prompt = f"""
You are the Executive Chief of Staff for {business_name}'s owner.
Your duty is to assist the business owner with inventory, customer queries, and business metrics.
OWNER QUERY: {latest_query}
INVENTORY STOCK: {catalog}
CONVERSATION HISTORY: {conversation_history}

Provide a crisp, executive response. If you want to trigger actions, append tags like [ACTION:ADD_PRODUCT] or [ACTION:SET_REMINDER].
Provide quick options at the end using: [BUTTONS: 📊 Daily Audit | ⏰ Add Reminder | 📦 View Stock]
"""
    else:
        known_name = profile.get("full_name") or "Valued Client"
        profile_notes = profile.get("notes") or "None on file"
        prompt = f"""
You are the Client Experience Executive for {business_name}.
Your tone is immaculate, articulate, polite, and efficient.

CLIENT NAME: {known_name}
SAVED PREFERENCES: {profile_notes}
LIVE CATALOG: {catalog}
ACCOUNT LEDGER: {customer_ledger}
CONVERSATION HISTORY: {conversation_history}
CLIENT QUERY: {latest_query}

INSTRUCTIONS:
1. Provide direct, complete answers with exact prices and stock.
2. Speak in formal, professional English.
3. If the user states their name or preferences, append [EXTRACT_NAME: Full Name] or [EXTRACT_NOTE: Preference details] at the end.
4. Append interactive quick options at the end using: [BUTTONS: 📜 View Catalog | 💳 Place Order | 👤 Human Agent]
5. Append action tags if triggered: [TAG:PAYMENT_TRIGGER] or [TAG:TRANSFER_HUMAN].
"""

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=700, temperature=0.2)
        )
        raw_text = response.text.strip()
    except ClientError as ce:
        if "429" in str(ce) or "RESOURCE_EXHAUSTED" in str(ce):
            print("⚠️ Gemini API Free Tier Quota Exhausted!")
            fallback_msg = "We are currently experiencing high request volumes on our AI assistant tier. Please wait 30 seconds and try again, or contact management directly."
            return {
                "reply": f"🤖 *[{business_name} Notice]*\n\n{fallback_msg}",
                "buttons": ["📜 View Catalog", "👤 Human Agent"],
                "detected_tags": [],
                "is_buy_intent": False,
                "is_human_transfer": False
            }
        raise ce
    except Exception as e:
        print(f"❌ Gemini generation error: {e}")
        return {
            "reply": f"🤖 *[{business_name} System]*\n\nAn unexpected error occurred processing your request. Please try again shortly.",
            "buttons": ["📜 View Catalog", "👤 Human Agent"],
            "detected_tags": [],
            "is_buy_intent": False,
            "is_human_transfer": False
        }

    # Extract & Store Self-Learned Customer Memory Facts
    if not is_owner:
        name_match = re.search(r"\[EXTRACT_NAME:\s*(.*?)\]", raw_text)
        note_match = re.search(r"\[EXTRACT_NOTE:\s*(.*?)\]", raw_text)
        ex_name = name_match.group(1).strip() if name_match else None
        ex_note = note_match.group(1).strip() if note_match else None
        if ex_name or ex_note:
            upsert_customer_profile(tenant["id"], customer_phone, full_name=ex_name, notes=ex_note)
        
        raw_text = re.sub(r"\[EXTRACT_NAME:\s*.*?\]", "", raw_text)
        raw_text = re.sub(r"\[EXTRACT_NOTE:\s*.*?\]", "", raw_text).strip()

    # Parse Interactive Buttons
    default_buttons = ["📊 Daily Audit", "⏰ Add Reminder", "📦 View Stock"] if is_owner else ["📜 View Catalog", "💳 Place Order", "👤 Human Agent"]
    button_match = re.search(r"\[BUTTONS:\s*(.*?)\]", raw_text)
    if button_match:
        button_str = button_match.group(1)
        buttons = [b.strip() for b in button_str.split("|") if b.strip()]
        raw_text = re.sub(r"\[BUTTONS:\s*.*?\]", "", raw_text).strip()
    else:
        buttons = default_buttons

    # Parse Action & Intent Tags
    detected_tags = re.findall(r"\[(?:TAG|ACTION):[A-Z_]+\]", raw_text)
    clean_text = re.sub(r"\[(?:TAG|ACTION):[A-Z_]+\]", "", raw_text).strip()

    # Clean Header Artifacts
    lines = clean_text.split("\n")
    filtered = [l for l in lines if not (re.search(r"🤖|AI Assistant|Client Care|Executive OS", l, re.IGNORECASE) and len(l.strip()) < 50)]
    clean_text = "\n".join(filtered).strip()

    header_title = "Executive Assistant" if is_owner else "Client Care"
    final_reply = f"🤖 *[{business_name} {header_title}]*\n\n{clean_text}"

    return {
        "reply": final_reply,
        "buttons": buttons,
        "detected_tags": detected_tags,
        "is_buy_intent": "[TAG:PAYMENT_TRIGGER]" in detected_tags,
        "is_human_transfer": "[TAG:TRANSFER_HUMAN]" in detected_tags
    }