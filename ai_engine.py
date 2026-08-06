import os
from google import genai

# Initialize the modern Google Gen AI client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = 'gemini-2.5-flash'

def classify_intent(message_text: str) -> str:
    """Routes the incoming text to the appropriate handler."""
    prompt = f"""Analyze this text: "{message_text}".
Categorize strictly as ONE word:
- BUSINESS (Asking about prices, stock like power banks, location in Onitsha, bank details)
- PERSONAL (Casual greetings like 'how far', family chat, social banter)
- HANDOVER (Requests like 'call me', 'I want human', complaints)
Output ONLY the single word."""
    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt
    )
    return response.text.strip().upper()

def generate_reply(message_text: str) -> str:
    """Generates the sales response matching the buyer's exact dialect."""
    prompt = f"""You are a helpful sales assistant for a Nigerian business.
Understand and reply accurately in the EXACT language/dialect used by the customer (Pidgin, Igbo, Hausa, or English).
Customer Message: "{message_text}" """
    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt
    )
    return f"🤖 *[Sales Assistant]*\n\n{response.text.strip()}"