import os
from google import genai
from database import get_products_catalog

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = 'gemini-2.5-flash'

def generate_reply(message_text: str) -> dict:
    """Generates niche-accurate responses with modern tags, Gen-Z vibe matching, and WhatsApp buttons."""
    
    catalog = get_products_catalog()
    
    prompt = f"""You are an elite, hyper-modern AI sales and customer experience manager for a business in Nigeria.

LIVE CATALOG / INVENTORY / SERVICES:
{catalog}

CUSTOMER MESSAGE: "{message_text}"

INSTRUCTIONS & RULES:
1. MATCH DIALECT/VIBE: Detect if customer speaks Pidgin, English, Igbo, Hausa, or Gen Z slang and respond in the EXACT vibe (e.g., using clean emojis, modern friendly phrasing).
2. STICK TO CATALOG: Quote exact prices and stock levels directly from the live catalog.
3. ACTION TAGS:
   - If user asks for human/call/complains: include tag `[TAG:TRANSFER_HUMAN]`
   - If user wants to buy/order: include tag `[TAG:BUY_NOW]`
4. INTERACTIVE BUTTONS:
   - Always append 2 to 3 contextual quick reply buttons at the very bottom using format: `[BUTTONS: Button 1 | Button 2 | Button 3]`
   - Examples: `[BUTTONS: 💳 Pay Now | 📦 Check Stock | 👤 Human Agent]`

Generate the complete response now:
"""

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt
    )
    
    raw_response = response.text.strip()
    
    # Parse buttons out of the text
    buttons = ["👤 Talk to Human", "📜 View Catalog"]
    clean_text = raw_response
    
    if "[BUTTONS:" in raw_response:
        parts = raw_response.split("[BUTTONS:")
        clean_text = parts[0].strip()
        button_raw = parts[1].split("]")[0]
        buttons = [b.strip() for b in button_raw.split("|")]

    return {
        "text": clean_text,
        "buttons": buttons,
        "is_human_transfer": "[TAG:TRANSFER_HUMAN]" in raw_response,
        "is_buy_intent": "[TAG:BUY_NOW]" in raw_response
    }