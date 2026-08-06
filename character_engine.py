import os
from google import genai
from database import get_tenant_catalog

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = 'gemini-2.5-flash'

CHARACTERS = {
    "street_smart": "You are 'Boda Jide', a sharp, street-smart, highly charismatic Lagos sales manager. You use urban Nigerian slang effortlessly, mix Pidgin with English gracefully, use energetic emojis, and make the customer feel valued ('My boss', 'Chief').",
    "luxury_concierge": "You are 'Aria', a high-end, sophisticated luxury concierge. Your tone is calm, elite, hyper-polite, and refined. You speak immaculate English with subtle elegance.",
    "gen_z_hype": "You are 'Zeen', a hyper-energetic, modern Gen-Z AI shopping buddy. You use current internet slang ('No cap', 'Valid', 'It's giving...'), clean formatting, and vibrant emojis 🔥."
}

def generate_live_character_reply(tenant: dict, conversation_history: str, persona_key: str = "street_smart") -> dict:
    """Generates an immersive, character-driven response with glassmorphic layout styling and action hooks."""
    catalog = get_tenant_catalog(tenant["id"])
    persona_instruction = CHARACTERS.get(persona_key, CHARACTERS["street_smart"])

    prompt = f"""
{persona_instruction}

BUSINESS NAME: {tenant['business_name']}
INDUSTRY NICHE: {tenant['niche']}

LIVE CATALOG STOCK & SERVICES:
{catalog}

CONVERSATION HISTORY:
{conversation_history}

RULES & INSTRUCTIONS:
1. Stay strictly in character.
2. Incorporate exact pricing and stock levels from the live catalog accurately.
3. Structure your response with a clean, glassmorphic layout using borders (╭─ ╮, │, ╰─ ╯) and engaging emojis.
4. Append 3 quick action buttons at the very bottom using format: `[BUTTONS: Option 1 | Option 2 | Option 3]`
5. If the customer expresses clear purchase intent, include the action tag `[TAG:BUY_INTENT]`.
6. If the customer asks for a human agent or complains, include the action tag `[TAG:TRANSFER_HUMAN]`.
"""

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt
    )
    
    raw_text = response.text.strip()
    
    # Parse interactive buttons
    buttons = ["🔥 View Catalog", "💳 Quick Checkout", "💬 Talk to Human"]
    clean_text = raw_text
    if "[BUTTONS:" in raw_text:
        parts = raw_text.split("[BUTTONS:")
        clean_text = parts[0].strip()
        button_raw = parts[1].split("]")[0]
        buttons = [b.strip() for b in button_raw.split("|")]

    return {
        "reply": clean_text,
        "buttons": buttons,
        "is_buy_intent": "[TAG:BUY_INTENT]" in raw_text,
        "is_human_transfer": "[TAG:TRANSFER_HUMAN]" in raw_text
    }