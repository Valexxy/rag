import os
import re
from google import genai
from google.genai import types
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
    """Generates dual-engine AI responses for either Business Owner or Client."""
    
    catalog = get_tenant_catalog(tenant["id"], search_query=latest_query)
    customer_ledger = get_customer_ledger(tenant["id"], customer_phone)
    profile = get_customer_profile(tenant["id"], customer_phone)
    business_name = tenant.get('business_name', 'our company')

    # -------------------------------------------------------------
    # A. BUSINESS OWNER PERSONAL ASSISTANT PROMPT
    # -------------------------------------------------------------
    if is_owner:
        prompt = f"""
You are the Executive Chief of Staff and Operations Director for {business_name}'s owner.
Your duty is to assist the business owner with inventory management, customer reminders, broadcasts, and operational insights.

OWNER QUERY: {latest_query}

CURRENT STORE INVENTORY:
{catalog}

CONVERSATION HISTORY:
{conversation_history}

INSTRUCTIONS FOR OWNER ASSISTANT:
1. Executive Tone: Address the user as "Chief", "Boss", or "Director". Be brief, hyper-efficient, and analytical.
2. Action Tag Extraction:
   - If the owner wants to add a product, format response and append `[ACTION:ADD_PRODUCT]`
   - If the owner wants to set a reminder, format response and append `[ACTION:SET_REMINDER]`
   - If the owner wants a broadcast, format response and append `[ACTION:BROADCAST]`
3. Always supply 3 clear interactive buttons at the end using `[BUTTONS: Option 1 | Option 2 | Option 3]`.
   Default Buttons: `[BUTTONS: 📊 Daily Audit | ⏰ Add Reminder | 📦 View Stock]`
"""
    # -------------------------------------------------------------
    # B. CLIENT CONCIERGE PROMPT
    # -------------------------------------------------------------
    else:
        known_name = profile.get("full_name") or "Valued Client"
        profile_notes = profile.get("notes") or "None on file"

        prompt = f"""
You are the Lead Client Experience Executive for {business_name}.
Your tone is immaculate, articulate, polite, and exceptionally efficient.

CLIENT NAME: {known_name}
SAVED CLIENT PREFERENCES: {profile_notes}

LIVE STORE CATALOG:
{catalog}

CLIENT ACCOUNT BALANCES & LEDGER:
{customer_ledger}

CONVERSATION HISTORY:
{conversation_history}

INSTRUCTIONS FOR CLIENT CONCIERGE:
1. Complete Answers: Always answer questions directly with complete pricing and stock.
2. Executive English: Speak in pristine English without street slang unless configured otherwise.
3. Interactive Navigation: Suggest quick option shortcuts at the bottom.
4. Append interactive buttons at the very end: `[BUTTONS: 📜 View Catalog | 💳 Place Order | 👤 Human Agent]`
5. Self-Learning Memory: Append `[EXTRACT_NAME: Name]` or `[EXTRACT_NOTE: Preference]` if user shares personal facts.
6. Trigger Action Tags:
   - Append `[TAG:PAYMENT_TRIGGER]` if user wants to buy/pay.
   - Append `[TAG:TRANSFER_HUMAN]` if user requests a human call.
"""

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(max_output_tokens=700, temperature=0.2)
    )
    
    raw_text = response.text.strip()

    # Memory Fact Extraction
    if not is_owner:
        name_match = re.search(r"\[EXTRACT_NAME:\s*(.*?)\]", raw_text)
        note_match = re.search(r"\[EXTRACT_NOTE:\s*(.*?)\]", raw_text)
        ex_name = name_match.group(1).strip() if name_match else None
        ex_note = note_match.group(1).strip() if note_match else None
        if ex_name or ex_note:
            upsert_customer_profile(tenant["id"], customer_phone, full_name=ex_name, notes=ex_note)
        
        raw_text = re.sub(r"\[EXTRACT_NAME:\s*.*?\]", "", raw_text)
        raw_text = re.sub(r"\[EXTRACT_NOTE:\s*.*?\]", "", raw_text).strip()

    # Extract Interactive Buttons
    default_buttons = ["📊 Daily Audit", "⏰ Add Reminder", "📦 View Stock"] if is_owner else ["📜 View Catalog", "💳 Place Order", "👤 Human Agent"]
    button_match = re.search(r"\[BUTTONS:\s*(.*?)\]", raw_text)
    if button_match:
        button_str = button_match.group(1)
        buttons = [b.strip() for b in button_str.split("|") if b.strip()]
        raw_text = re.sub(r"\[BUTTONS:\s*.*?\]", "", raw_text).strip()
    else:
        buttons = default_buttons

    # Extract Action Tags
    detected_tags = re.findall(r"\[(?:TAG|ACTION):[A-Z_]+\]", raw_text)
    clean_text = re.sub(r"\[(?:TAG|ACTION):[A-Z_]+\]", "", raw_text).strip()

    # Clean Hallucinated Badges
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