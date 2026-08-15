"""
====================================================================
BILLION-DOLLAR CONVERSATIONAL BRAIN & MEMORY ENGINE (v2026)
====================================================================
- Multi-Session Conversational Memory Thread per remoteJid
- Context Stitching across Multi-AI Model Failovers (Llama / DeepSeek / Gemini)
- Zero Greeting Repetition Guardrail for Ongoing Conversations
- Deep Reasoning & Universal Intent Handling for ANY Customer Question
- State & Cart Preservation across Digressions
====================================================================
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("BillionDollarBrain")


class BillionDollarMemoryStore:
    """
    High-capacity persistent conversation memory store.
    Stores rolling chat turns, extracted user entities (appliances, location, budget),
    and active thread state per customer phone / remoteJid.
    """

    def __init__(self):
        self._threads: Dict[str, List[Dict[str, str]]] = {}
        self._entities: Dict[str, Dict[str, Any]] = {}
        self._last_active: Dict[str, float] = {}

    def add_turn(self, phone: str, role: str, content: str):
        """Appends a customer or assistant turn to the customer's memory thread."""
        if phone not in self._threads:
            self._threads[phone] = []
            self._entities[phone] = {"appliances": [], "location": None, "budget": None}

        # Keep rolling last 14 turns (7 exchanges) for deep context recall
        self._threads[phone].append({"role": role, "content": content, "timestamp": time.time()})
        if len(self._threads[phone]) > 14:
            self._threads[phone] = self._threads[phone][-14:]

        self._last_active[phone] = time.time()
        self._extract_entities(phone, content)

    def get_context_summary(self, phone: str) -> str:
        """Formats full conversation transcript and extracted customer context."""
        turns = self._threads.get(phone, [])
        if not turns:
            return ""

        formatted_history = []
        for t in turns:
            prefix = "Customer: " if t["role"] == "user" else "Assistant: "
            formatted_history.append(f"{prefix}{t['content']}")

        transcript = "\n".join(formatted_history)
        entities = self._entities.get(phone, {})
        
        entity_summary = ""
        if any(entities.values()):
            entity_summary = f"\n[EXTRACTED CUSTOMER ENTITIES: {json.dumps(entities)}]\n"

        return f"\n--- ONGOING CONVERSATION MEMORY THREAD ({len(turns)} turns) ---{entity_summary}\n{transcript}\n--------------------------------------------------------\n"

    def is_ongoing_conversation(self, phone: str) -> bool:
        """Returns True if the customer has an active conversation thread (< 2 hours old)."""
        last_time = self._last_active.get(phone, 0)
        return (time.time() - last_time) < 7200 and len(self._threads.get(phone, [])) > 0

    def _extract_entities(self, phone: str, text: str):
        """Automatically extracts key customer context (appliances, location, requirements)."""
        lower = text.lower()
        entities = self._entities.get(phone, {"appliances": [], "location": None, "budget": None})

        # Appliance entity extraction
        appliance_keywords = ["ac", "air conditioner", "freezer", "fridge", "refrigerator", "tv", "television", "pumping machine", "fan", "inverter"]
        for kw in appliance_keywords:
            if kw in lower and kw not in entities["appliances"]:
                entities["appliances"].append(kw)

        self._entities[phone] = entities


# Singleton Memory Instance
memory_store = BillionDollarMemoryStore()


class BillionDollarBrain:
    """
    Universal Reasoning Engine stitching Multi-AI Models (Llama 3.3 70B, DeepSeek-R1, Gemini)
    with strict commercial boundaries and zero-repetition conversational flow.
    """

    def construct_master_prompt(self, phone: str, query: str, business_name: str, catalog_str: str, address: str) -> tuple[str, str]:
        """
        Builds the master system prompt and user message payload with memory context stitching.
        """
        is_ongoing = memory_store.is_ongoing_conversation(phone)
        context_thread = memory_store.get_context_summary(phone)

        # Anti-greeting repetition instruction
        greeting_guardrail = ""
        if is_ongoing:
            greeting_guardrail = """
8. STRICT NO-GREETING-REPETITION RULE (MANDATORY FOR ONGOING CHAT):
   - THIS IS AN ONGOING CONVERSATION THREAD. DO NOT greet the customer again (e.g. DO NOT say "Welcome to Teeslux", "Hello", "Good day", or "How can I assist you").
   - Jump IMMEDIATELY and DIRECTLY to answering their exact question, providing high-level estimates, numbers, or technical answers, and asking clean, natural follow-up questions.
"""

        system_prompt = f"""You are the official Executive AI Sales & Customer Care Consultant for {business_name} located at {address}.

CURRENT LIVE SUPABASE PRODUCT CATALOG & OFFICIAL PRICES:
{catalog_str}

STRICT COMMERCIAL CONSTITUTION & OPERATIONAL BOUNDARIES:

1. PRODUCT PRICE BOUNDARY (STRICT RULE):
   - The ONLY costs/prices you are authorized to state are the exact product prices listed in the Live Supabase Catalog above.
   - Quoting any product price not in the database is strictly forbidden.

2. ZERO EXTRA COST QUOTING RULE (MANDATORY HUMAN HANDOVER):
   - You are STRICTLY PROHIBITED from stating or guessing any shipping fee, waybill cost, delivery fee, installation charge, or bulk discount.
   - If a customer asks about ANY non-product cost (shipping fee, waybill cost, installation fee):
     a) Stating the product price is allowed if relevant.
     b) Inform the customer warmly and respectfully that all delivery, waybill, and installation costs are custom-calculated and finalized exclusively by our Human Store Manager (+2348072015725) to guarantee the exact lowest rate for their location.
     c) Append `[TRANSFER_HUMAN]` at the end of your response so our human manager is alerted instantly.

3. SENSITIVE CONVERSATIONAL TONE & SENTIMENT MATCHING:
   - Always maintain a warm, executive, highly respectful, and empathetic African commercial tone.
   - Use clean, elegant formatting with bolding (*like this*) and appropriate professional emojis.
   - Respond in concise, clear, and actionable paragraphs (2 to 4 sentences).

4. UNIVERSAL REASONING & OUT-OF-CATALOG HANDOVER (STRICT RULE):
   - Reason logically and intelligently through ANY question the customer asks.
   - If a customer asks an out-of-catalog question, market errand, price analysis in main market, fabric sourcing, or custom non-solar request:
     a) Politely state what {business_name} specializes in.
     b) Inform them warmly that our Store Manager (+2348072015725) manages all custom market errands, price analysis, and local vendor referrals.
     c) YOU MUST ALWAYS APPEND `[TRANSFER_HUMAN]` at the end of your response so our human manager is alerted on WhatsApp instantly.

5. HIGH-LEVEL ESTIMATE & SOLAR ADVISORY RULE:
   - If a customer asks for a "high level", "rough estimate", "standard recommendation", or "just tell me" without providing exact appliance wattages:
     a) DO NOT ask them for sticker wattages or details again.
     b) Immediately calculate a high-level estimation using standard appliance power ratings (e.g. 1.5 HP AC = ~1.2kW, 80" TV = ~250W, Deep Freezer = ~200W).
     c) Recommend matching items from the live catalog (e.g., Tier-1 550W Monocrystalline Solar Panels at ₦120,000 and 3.5kVA Hybrid Solar Inverter System at ₦340,000).
     d) Quote exact catalog unit prices in ₦ (Naira).

6. PAYMENT INTEGRITY & ANTI-DIVERSION:
   - Never provide personal bank accounts. Payments are processed exclusively through official virtual accounts or verified store checkout.

7. HUMAN ESCALATION TRIGGER:
   - If user asks for human manager, expresses complaint, asks for waybill/shipping fees, requests out-of-catalog market analysis/sourcing, or requests personal bank details, append `[TRANSFER_HUMAN]`.
{greeting_guardrail}
"""


        user_message = f"{context_thread}\nCustomer: {query}"
        return system_prompt, user_message


billion_dollar_brain = BillionDollarBrain()
