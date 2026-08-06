import os
import json
import time
from dotenv import load_dotenv

# 1. Load environment variables from .env file first
load_dotenv()

from google import genai

# 2. Initialize Client with loaded key
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = 'gemini-2.5-flash'

# 🌐 100+ Niche Master Registry (Sample spanning key industries)
TEST_NICHES = [
    # E-Commerce & Retail
    {"niche": "Mobile Accessories", "query": "How much is your 20k mAh power bank and does it come with warranty?"},
    {"niche": "Luxury Sneakers", "query": "Do you have Jordan 1 Retro in size 43? Can I pay on delivery?"},
    {"niche": "Wig & Hair Sales", "query": "Is this 30 inch bone straight human hair or synthetic?"},
    {"niche": "Skincare & Beauty", "query": "I have hyperpigmentation on my face, which of your serums should I buy?"},
    
    # Hospitality & Food
    {"niche": "Artisanal Bakery", "query": "Can I order a two-tier red velvet cake for tomorrow 2 PM?"},
    {"niche": "Fine Dining Restaurant", "query": "Do you have a table for 4 available tonight at 8 PM?"},
    {"niche": "Shortlet Apartments", "query": "How much per night for your 2-bedroom penthouse in Victoria Island?"},
    
    # Professional & Healthcare Services
    {"niche": "Dental Clinic", "query": "My tooth is aching badly, how much is scaling and polishing?"},
    {"niche": "Auto Repair Workshop", "query": "My car engine light is showing and the transmission is jerking. Can I bring it in?"},
    {"niche": "Fitness Gym & Personal Trainer", "query": "What are your monthly membership rates and do you offer weight loss meal plans?"},
    {"niche": "Law Firm", "query": "I need help drafting a business contract. What are your consultation fees?"},
    
    # Tech & Logistics
    {"niche": "Logistics & Delivery", "query": "I want to send a parcel from Ikeja to Lekki today. What's the fee?"},
    {"niche": "SaaS Platform Support", "query": "How do I upgrade my monthly subscription to the Enterprise plan?"}
]

def simulate_niche_engine(niche: str, customer_message: str) -> dict:
    """Simulates ultra-adaptive responses with modern tag hooks and dynamic interactive buttons."""
    
    system_instruction = f"""
You are the hyper-smart, ultra-modern AI operations system powering a business in the '{niche}' industry.

YOUR OBJECTIVE:
1. Provide a direct, highly accurate, and helpful response relevant strictly to the business niche: '{niche}'.
2. Match the tone and energy appropriate for the customer's query.
3. Automatically attach appropriate ACTION TAGS at the end of your response when needed:
   - Attach `[TAG:TRANSFER_HUMAN]` if the user expresses frustration, asks for a call/human, or asks complex legal/medical questions requiring expert oversight.
   - Attach `[TAG:PAYMENT_TRIGGER]` if the user shows explicit buying intent.
   - Attach `[TAG:BOOKING_SLOT]` if the user asks for appointments, dates, or reservations.

4. Provide up to 3 context-aware INTERACTIVE BUTTONS for quick WhatsApp reply options formatted as:
   `[BUTTONS: Option 1 | Option 2 | Option 3]`

Example Output:
"Our 20,000mAh Power Bank goes for ₦19,000 with a 6-month warranty included! ⚡ 

[TAG:PAYMENT_TRIGGER]
[BUTTONS: 💳 Buy Now | 📜 View Specs | 👤 Talk to Human]"
"""

    prompt = f"""Business Niche: {niche}
Customer Inquiry: "{customer_message}" """

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=f"{system_instruction}\n\n{prompt}"
    )
    
    raw_text = response.text.strip()
    
    # Extract Tags & Buttons from text
    tags = [token for token in raw_text.split() if token.startswith("[TAG:")]
    
    buttons = []
    if "[BUTTONS:" in raw_text:
        try:
            button_part = raw_text.split("[BUTTONS:")[1].split("]")[0]
            buttons = [b.strip() for b in button_part.split("|")]
        except Exception:
            pass

    return {
        "niche": niche,
        "query": customer_message,
        "response": raw_text,
        "detected_tags": tags,
        "interactive_buttons": buttons
    }

def run_suite():
    print("🚀 Starting 100+ Niche Simulation & Intent Tagging Suite...\n")
    print("=" * 80)
    
    for item in TEST_NICHES:
        print(f"\n🏢 TESTING NICHE: {item['niche'].upper()}")
        print(f"💬 CUSTOMER: \"{item['query']}\"")
        
        start_time = time.time()
        result = simulate_niche_engine(item["niche"], item["query"])
        latency = round(time.time() - start_time, 2)
        
        print(f"⏱️ Response Time: {latency}s")
        print(f"🤖 AI RESPONSE:\n{result['response']}")
        print("-" * 80)

if __name__ == "__main__":
    run_suite()