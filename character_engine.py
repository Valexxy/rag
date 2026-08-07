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

CHARACTERS = {
    "world_class_pro": (
        "You are the Lead Client Experience Executive for {business_name}. "
        "Your tone is immaculate, highly articulate, polite, calm, and exceptionally efficient. "
        "You treat every customer as a valued VIP, offering concise, precise, and sophisticated assistance."
    )
}

def generate_live_character_reply(
    tenant: dict, 
    customer_phone: str, 
    latest_query: str,
    conversation_history: str, 
    persona_key: str = "world_class_pro"
) -> dict:
    """Smart Memory-Grounded Intelligence Engine with Self-Learning and Direct Answers."""
    
    # 1. Fetch Targeted Catalog & Ledger
    catalog = get_tenant_catalog(tenant["id"], search_query=latest_query)
    customer_ledger = get_customer_ledger(tenant["id"], customer_phone)
    profile = get_customer_profile(tenant["id"], customer_phone)
    
    business_name = tenant.get('business_name', 'our company')
    
    # 2. Build Profile Context
    known_name = profile.get("full_name") or "Valued Customer"
    profile_notes = profile.get("notes") or "None on file"

    tenant_persona = tenant.get('ai_persona')
    if tenant_persona and tenant_persona.strip():
        persona_instruction = f"You represent {business_name}. {tenant_persona}"
    else:
        persona_template = CHARACTERS.get(persona_key, CHARACTERS["world_class_pro"])
        persona_instruction = persona_template.format(business_name=business_name)

    prompt = f"""
{persona_instruction}

BUSINESS NAME: {business_name}
INDUSTRY NICHE: {tenant.get('niche', 'Operations')}

KNOWN CUSTOMER MEMORY & PROFILE:
- Customer Name: {known_name}
- Saved Customer Notes/Preferences: {profile_notes}

LIVE CATALOG STOCK & SERVICES:
{catalog}

CUSTOMER ACCOUNT LEDGER & BALANCE RECORDS:
{customer_ledger}

CONVERSATION HISTORY (PAST TURNS):
{conversation_history}

CRITICAL EXECUTION INSTRUCTIONS:
1. COMPLETE, DIRECT ANSWERS: When asked "what do you sell" or "what are your prices", IMMEDIATELY provide the full list of products, prices, and stock levels directly in your response. Never send incomplete intros.
2. CONTINUITY & CONTEXT: Use the past conversation history and customer profile memory above. If the customer mentions their name or preference, acknowledge it naturally.
3. EXECUTIVE TONE: Communicate in immaculate, formal English. Do NOT use Pidgin or slang.
4. NO HEADER BADGES IN TEXT: Do NOT output any header badges starting with '🤖' or '[... Client Care]'. Python attaches this automatically.
5. SELF-LEARNING FACT EXTRACTION: If the customer reveals their name or a crucial preference in this turn, append memory extraction tags at the very end:
   - `[EXTRACT_NAME: Customer Full Name]` (if customer states their name)
   - `[EXTRACT_NOTE: Preferred item, budget, or key detail]` (if customer shares preferences)
6. ACTION TAGS & BUTTONS:
   - Append `[TAG:PAYMENT_TRIGGER]` if user expresses buying intent.
   - Append `[TAG:TRANSFER_HUMAN]` if user requests human support or call.
   - Append `[BUTTONS: Option 1 | Option 2 | Option 3]` at the absolute end.
"""

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=700,
            temperature=0.2
        )
    )
    
    raw_text = response.text.strip()
    
    # Extract & Store Self-Learned Customer Memory Facts
    name_match = re.search(r"\[EXTRACT_NAME:\s*(.*?)\]", raw_text)
    note_match = re.search(r"\[EXTRACT_NOTE:\s*(.*?)\]", raw_text)
    
    extracted_name = name_match.group(1).strip() if name_match else None
    extracted_note = note_match.group(1).strip() if note_match else None

    if extracted_name or extracted_note:
        upsert_customer_profile(tenant["id"], customer_phone, full_name=extracted_name, notes=extracted_note)

    # Clean Memory Extraction Tags from Visible Text
    raw_text = re.sub(r"\[EXTRACT_NAME:\s*.*?\]", "", raw_text)
    raw_text = re.sub(r"\[EXTRACT_NOTE:\s*.*?\]", "", raw_text).strip()

    # Extract Interactive Buttons
    buttons = ["💳 Complete Purchase", "📜 Product Catalog", "👤 Speak with Agent"]
    button_match = re.search(r"\[BUTTONS:\s*(.*?)\]", raw_text)
    if button_match:
        button_str = button_match.group(1)
        buttons = [b.strip() for b in button_str.split("|") if b.strip()]
        raw_text = re.sub(r"\[BUTTONS:\s*.*?\]", "", raw_text).strip()

    # Extract Action Tags
    detected_tags = re.findall(r"\[TAG:[A-Z_]+\]", raw_text)
    clean_text = re.sub(r"\[TAG:[A-Z_]+\]", "", raw_text).strip()

    # Remove Hallucinated Badges
    lines = clean_text.split("\n")
    filtered_lines = [line for line in lines if not (re.search(r"🤖|AI Assistant|Client Care", line, re.IGNORECASE) and len(line.strip()) < 50)]
    clean_text = "\n".join(filtered_lines).strip()

    # Prepend Official Executive Badge
    ai_badge = f"🤖 *[{business_name} Client Care]*\n\n"
    final_reply = f"{ai_badge}{clean_text}"

    return {
        "reply": final_reply,
        "buttons": buttons,
        "detected_tags": detected_tags,
        "is_buy_intent": "[TAG:PAYMENT_TRIGGER]" in detected_tags,
        "is_human_transfer": "[TAG:TRANSFER_HUMAN]" in detected_tags,
        "is_booking": "[TAG:BOOKING_SLOT]" in detected_tags
    }