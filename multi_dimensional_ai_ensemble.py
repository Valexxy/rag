"""
====================================================================
MULTI-DIMENSIONAL OPEN-SOURCE AI ENSEMBLE & CLARIFICATION ENGINE
====================================================================
Combines open-source LLM architectures (Llama 3.3 70B, Qwen 2.5 72B, Mistral)
across 5 conversational dimensions:
1. Product Catalog & Exact Technical Specifications
2. General Commercial Advice & World Knowledge
3. Warm, Natural Human-Like Retail Persona
4. Interactive Clarification & Follow-Up Questionnaire Engine
5. Zero-Silence Fallback Net
"""

import os
import json
import logging
import requests

logger = logging.getLogger(__name__)

# System prompt forcing natural persona + interactive clarification when confused
ENSEMBLE_SYSTEM_PROMPT = """You are a warm, extremely smart, human-like sales consultant and customer care expert for Teeslux Global Electronics & Solar (located in Onitsha, Anambra State, Nigeria).

YOUR CORE DIRECTIVES:
1. NEVER be silent or give robotic corporate disclaimers. Always sound like a real, friendly, highly knowledgeable human store representative.
2. ALWAYS provide a correct, helpful, engaging response to ANY question the customer asks (about electronics, solar, general knowledge, business hours, prices, advice).
3. IF YOU ARE CONFUSED, UNCERTAIN, OR THE CUSTOMER'S REQUEST IS BROAD/UNCATALOGUED (e.g., 'I want to buy oil', 'Do you have batteries?'):
   - DO NOT give up or drop out.
   - FEEL FREE TO ASK CLARIFYING QUESTIONS! Ask friendly follow-up questions to narrow down exactly what they need (e.g. 'Are you looking for cooking groundnut oil or solar inverter oil?', 'What capacity solar battery do you need?').
4. If an item is not in the store catalog, mention nicely that you can check stock with the manager, ask clarifying details, and suggest related items.
5. Keep your tone warm, professional, and authentic (Nigerian retail English style). Use bullet points and emoji tastefully.
"""

class MultiDimensionalAIEnsemble:
    """Multi-Model Open Source Ensemble Engine"""

    def __init__(self):
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.hf_token = os.environ.get("HF_TOKEN")

    def generate_ensemble_reply(self, customer_query: str, catalog_context: str, chat_history: str = "") -> dict:
        """
        Executes multi-dimensional open-source AI generation with interactive clarification guarantee.
        """
        prompt = f"""STORE CATALOG CONTEXT:
{catalog_context}

RECENT CHAT HISTORY:
{chat_history}

CUSTOMER QUERY:
"{customer_query}"

Provide a warm, human, completely accurate response. If the query is ambiguous or out-of-catalog, ask clarifying follow-up questions!"""

        # ── DIMENSION 1: GROQ OPEN-SOURCE LLAMA 3.3 70B ──────────────────
        if self.groq_key:
            try:
                from groq import Groq
                client = Groq(api_key=self.groq_key)
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": ENSEMBLE_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,
                    max_tokens=400
                )
                res_text = completion.choices[0].message.content.strip()
                if res_text:
                    return {
                        "success": True,
                        "reply": res_text,
                        "architecture": "Groq_Llama_3.3_70B_Ensemble",
                        "needs_clarification": "?" in res_text
                    }
            except Exception as e:
                logger.warning(f"[AIEnsemble] Groq primary failed: {e}")

        # ── DIMENSION 2: GEMINI 1.5 FLASH BACKUP ─────────────────────────
        if self.gemini_key:
            try:
                from google import genai
                client = genai.Client(api_key=self.gemini_key)
                res = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=f"{ENSEMBLE_SYSTEM_PROMPT}\n\n{prompt}"
                )
                if res and res.text and res.text.strip():
                    return {
                        "success": True,
                        "reply": res.text.strip(),
                        "architecture": "Gemini_Flash_Ensemble",
                        "needs_clarification": "?" in res.text
                    }
            except Exception as e:
                logger.warning(f"[AIEnsemble] Gemini backup failed: {e}")

        # ── DIMENSION 3: HUGGINGFACE OPEN-SOURCE HUB (Qwen 2.5 72B) ──────
        try:
            from open_source_chat_matrix import open_source_matrix
            hf_res = open_source_matrix.generate_open_source_response(prompt, ENSEMBLE_SYSTEM_PROMPT)
            if hf_res.get("success"):
                return {
                    "success": True,
                    "reply": hf_res["reply"],
                    "architecture": "HuggingFace_Qwen2.5_Ensemble",
                    "needs_clarification": "?" in hf_res["reply"]
                }
        except Exception as e:
            logger.warning(f"[AIEnsemble] HuggingFace Hub failed: {e}")

        # ── DIMENSION 4: DETERMINISTIC CLARIFICATION SAFETY NET ───────────
        # Guaranteed response — NEVER SILENT
        clean_q = customer_query.strip().lower()
        fallback_reply = (
            f"🤖 *[Teeslux Global Store Consultant]*\n\n"
            f"Thank you for asking about '{customer_query}'! To make sure I get you the exact right information or price:\n\n"
            f"❓ Could you clarify a few details? (For example: what specific size, model, or capacity are you looking for?)\n\n"
            f"💡 You can also reply *#1* to browse our available store catalog, or reply *#human* to speak directly with our store manager!"
        )
        return {
            "success": True,
            "reply": fallback_reply,
            "architecture": "Deterministic_Clarification_Safety_Net",
            "needs_clarification": True
        }

ai_ensemble = MultiDimensionalAIEnsemble()
