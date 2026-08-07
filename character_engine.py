import os
from google import genai
from google.genai import types
from database import get_tenant_catalog, get_customer_ledger

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = 'gemini-2.5-flash'

CHARACTERS = {
    "street_smart": "You are 'Boda Jide', a sharp, street-smart Lagos operations manager for {business_name}. You speak urban Nigerian Pidgin/English gracefully, keep responses punchy, and make customers feel valued ('My boss', 'Chief').",
    "luxury_concierge": "You are 'Aria', an elite luxury concierge for {business_name}. Your tone is calm, hyper-polite, and refined.",
    "gen_z_hype": "You are 'Zeen', a hyper-energetic Gen-Z AI assistant for {business_name}. You use modern slang and vibrant emojis 🔥."
}

def generate_live_character_reply(tenant: dict, customer_phone: str, conversation_history: str, persona_key: str = "street_smart") -> dict:
    """Fast, memory-grounded character response engine with low latency, AI badge, and action hooks."""
    
    # Fetch ground truth catalog AND specific customer account records
    catalog = get_tenant_catalog(tenant["id"])
    customer_ledger = get_customer_ledger(tenant["id"], customer_phone)
    
    business_name = tenant.get('business_name', 'our store')
    persona_template = CHARACTERS.get(persona_key, CHARACTERS["street_smart"])
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

RULES & INSTRUCTIONS:
1. DIRECT REPLIES ONLY: Answer the user's specific question using exact facts from the catalog or their account ledger. Do not dump the entire catalog unless explicitly asked.
2. WHATSAPP FORMATTING: Use *bold* for key numbers, prices, and names. NO ASCII box borders (╭─, │, ╰─). Keep output concise (under 60 words).
3. IN-TEXT QUICK REPLIES: Add clear numbered options at the bottom (e.g. "👉 Reply *1* to Order | Reply *2* for Agent").
4. ACTION TAGS: Append one tag at the very end if triggered:
   - `[TAG:PAYMENT_TRIGGER]` (if buying, paying dues, or placing an order)
   - `[TAG:TRANSFER_HUMAN]` (if asking for human support/call or complaining)
   - `[TAG:BOOKING_SLOT]` (if requesting an appointment or reservation)
5. INTERACTIVE BUTTONS: Append `[BUTTONS: Option 1 | Option 2 | Option 3]` at the absolute end.
"""

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=300,
            temperature=0.3
        )
    )
    
    raw_text = response.text.strip()
    
    # Extract action tags
    detected_tags = [token for token in raw_text.split() if token.startswith("[TAG:")]
    
    # Extract buttons
    buttons = ["💳 Pay Now", "📜 View Catalog", "👤 Human Agent"]
    clean_text = raw_text

    if "[BUTTONS:" in raw_text:
        parts = raw_text.split("[BUTTONS:")
        clean_text = parts[0].strip()
        try:
            button_raw = parts[1].split("]")[0]
            buttons = [b.strip() for b in button_raw.split("|")]
        except Exception:
            pass

    # Clean action tags from customer message body
    for tag in detected_tags:
        clean_text = clean_text.replace(tag, "").strip()

    # Apply AI Badge Header
    ai_badge = f"🤖 *[{business_name} AI Assistant]*\n\n"
    final_reply = f"{ai_badge}{clean_text}"

    return {
        "reply": final_reply,
        "buttons": buttons,
        "detected_tags": detected_tags,
        "is_buy_intent": "[TAG:PAYMENT_TRIGGER]" in detected_tags,
        "is_human_transfer": "[TAG:TRANSFER_HUMAN]" in detected_tags,
        "is_booking": "[TAG:BOOKING_SLOT]" in detected_tags
    }