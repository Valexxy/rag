import os
import uuid
from google import genai
from database import get_tenant_catalog
from monnify import create_tenant_payment_link

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = 'gemini-2.5-flash'

def process_multitenant_message(tenant: dict, customer_phone: str, message_text: str) -> dict:
    """Processes incoming chat, detects intents, formats answers, and builds payment links on demand."""
    
    catalog = get_tenant_catalog(tenant["id"])
    
    system_prompt = f"""
You are the primary AI operations manager for '{tenant['business_name']}', operating in the '{tenant['niche']}' industry.
Persona & Tone: {tenant['ai_persona']}

LIVE CATALOG / INVENTORY / SERVICES:
{catalog}

CUSTOMER MESSAGE: "{message_text}"

INSTRUCTIONS:
1. Identify if the user wants to buy/pay. If yes, extract the requested item and calculated total price.
2. Reply in the exact dialect/language used by the customer (Pidgin, English, Hausa, Igbo).
3. Be direct, authoritative, and concise.

If the message is an explicit purchase request, structure your answer to confirm the total amount and state "GENERATING_PAYMENT_LINK:[AMOUNT]".
Otherwise, reply naturally.
"""

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=system_prompt
    )
    
    reply_text = response.text.strip()
    
    # Check for automated payment trigger
    if "GENERATING_PAYMENT_LINK:" in reply_text:
        try:
            amount_str = reply_text.split("GENERATING_PAYMENT_LINK:")[1].split()[0].replace("₦", "").replace(",", "").strip()
            amount = float(amount_str)
            
            payment_ref = f"TX_{tenant['instance_name'].upper()}_{uuid.uuid4().hex[:8]}"
            checkout_url = create_tenant_payment_link(tenant, amount, customer_phone, payment_ref)
            
            if checkout_url:
                clean_reply = reply_text.split("GENERATING_PAYMENT_LINK:")[0].strip()
                final_response = f"{clean_reply}\n\n💳 *Payment Link:* {checkout_url}\n\n_Click the link to complete payment via Transfer or Card._"
                return {"reply": final_response, "payment_ref": payment_ref, "amount": amount}
        except Exception as e:
            print(f"❌ Error generating link: {e}")
            
    return {"reply": reply_text, "payment_ref": None, "amount": 0}