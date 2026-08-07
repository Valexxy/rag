import os
from google import genai
from google.genai import types
from database import get_tenant_catalog, get_customer_ledger

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = 'gemini-2.5-flash'

CHARACTERS = {
    "world_class_pro": (
        "You are the Lead Client Experience Executive for {business_name}. "
        "Your tone is immaculate, highly articulate, polite, calm, and exceptionally efficient. "
        "You treat every customer as a valued VIP, offering concise, precise, and sophisticated assistance."
    ),
    "street_smart": (
        "You are 'Boda Jide', a sharp, charismatic sales manager for {business_name}. "
        "You use urban Nigerian Pidgin/English gracefully and keep responses punchy."
    ),
    "luxury_concierge": (
        "You are 'Aria', an elite luxury concierge for {business_name}. "
        "Your tone is calm, hyper-polite, and refined."
    )
}

def generate_live_character_reply(
    tenant: dict, 
    customer_phone: str, 
    conversation_history: str, 
    persona_key: str = "world_class_pro"
) -> dict:
    """Fast, memory-grounded world-class executive response engine."""
    
    catalog = get_tenant_catalog(tenant["id"])
    customer_ledger = get_customer_ledger(tenant["id"], customer_phone)
    
    business_name = tenant.get('business_name', 'our store')
    
    # Check if tenant has a custom persona defined in Supabase
    tenant_persona = tenant.get('ai_persona')
    if tenant_persona and tenant_persona.strip():
        persona_instruction = f"You represent {business_name}. {tenant_persona}"
    else:
        persona_template = CHARACTERS.get(persona_key, CHARACTERS["world_class_pro"])
        persona_instruction = persona_template.format(business_name=business_name)

    prompt = f"""
{persona_instruction}

BUSINESS NAME: {business_name}
NICHE: {tenant.get('niche', 'Operations')}

LIVE CATALOG STOCK & SERVICES:
{catalog}

CUSTOMER PERSONAL ACCOUNT LEDGER / RECORDS:
{customer_ledger}

CONVERSATION HISTORY:
{conversation_history}

CRITICAL RULES & INSTRUCTIONS:
1. DYNAMIC LANGUAGE ADAPTATION: If the customer asks to speak English, formal language, or explicitly requests no Pidgin/slang (e.g. "speak good english not pidgin"), IMMEDIATELY drop ALL Pidgin words ("Ah, my boss", "wetin", "dey", "no wahala", etc.) and respond strictly in immaculate, formal English.
2. INSTANT SHORTCUT FULFILLMENT: If the user replies with a single number (e.g., '1', '2', '3'), IMMEDIATELY provide the full details for that option without asking for re-confirmation.
3. DIRECT & ACCURATE: Provide exact prices, stock levels, or ledger balances directly from the data above.
4. NO HEADER BADGES IN RAW OUTPUT: Do NOT write any header badge starting with '🤖' or '[... AI Assistant]'. Python attaches this header automatically.
5. WHATSAPP FORMATTING: Use *bold* for key amounts, product names, and dates. NO ASCII box borders (╭─, │, ╰─). Keep output concise (under 60 words).
6. IN-TEXT QUICK OPTIONS: Include clean numbered shortcuts at the bottom (e.g., "👉 Reply *1* for Catalog | Reply *2* for Account Status | Reply *3* for Support").
7. ACTION TAGS: Append one tag at the very end if triggered:
   - `[TAG:PAYMENT_TRIGGER]` (if customer expresses purchase intent or pays dues)
   - `[TAG:TRANSFER_HUMAN]` (if customer requests human support or raises an issue)
   - `[TAG:BOOKING_SLOT]` (if customer requests an appointment or reservation)
8. INTERACTIVE BUTTONS: Append `[BUTTONS: Option 1 | Option 2 | Option 3]` at the absolute end.
"""

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=300,
            temperature=0.2
        )
    )
    
    raw_text = response.text.strip()
    
    # Extract action tags
    detected_tags = [token for token in raw_text.split() if token.startswith("[TAG:")]
    
    # Extract interactive buttons
    buttons = ["💳 Complete Purchase", "📜 Product Catalog", "👤 Speak with Agent"]
    clean_text = raw_text

    if "[BUTTONS:" in raw_text:
        parts = raw_text.split("[BUTTONS:")
        clean_text = parts[0].strip()
        try:
            button_raw = parts[1].split("]")[0]
            buttons = [b.strip() for b in button_raw.split("|")]
        except Exception:
            pass

    # Strip action tags from visible customer body
    for tag in detected_tags:
        clean_text = clean_text.replace(tag, "").strip()

    # Prevent duplicate badge headers
    lines = [line for line in clean_text.split("\n") if not ("AI Assistant" in line or "Client Care" in line or "🤖" in line)]
    clean_text = "\n".join(lines).strip()

    # Prepend official executive AI identification badge
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