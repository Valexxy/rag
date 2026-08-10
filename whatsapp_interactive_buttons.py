"""
====================================================================
META OFFICIAL WHATSAPP NATIVE INTERACTIVE BUTTONS & LIST MENUS (v2026)
====================================================================
Generates native WhatsApp interactive quick-reply buttons and dropdown list menus
for easy customer navigation, back/front menu browsing, and instant order triggers.
"""

import json
import urllib.request
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("WhatsAppInteractive")

class WhatsAppInteractiveEngine:
    """Generates official Meta interactive buttons, list menus, and navigation components."""

    def build_quick_buttons_payload(
        self,
        to_phone: str,
        body_text: str,
        buttons: List[Dict[str, str]],
        header_text: str = "Teeslux Global Electronics & Solar",
        footer_text: str = "Tap a button below to navigate"
    ) -> dict:
        """Formats native Meta 3-button quick reply payload."""
        formatted_buttons = []
        for b in buttons[:3]:  # Meta allows max 3 buttons per message
            formatted_buttons.append({
                "type": "reply",
                "reply": {
                    "id": b.get("id", "btn_id"),
                    "title": b.get("title", "Button")[:20]  # Meta limit 20 chars
                }
            })

        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {"type": "text", "text": header_text},
                "body": {"text": body_text},
                "footer": {"text": footer_text},
                "action": {
                    "buttons": formatted_buttons
                }
            }
        }

    def build_list_menu_payload(
        self,
        to_phone: str,
        body_text: str,
        menu_button_title: str = "📋 Open Navigation Menu",
        sections: Optional[List[dict]] = None,
        header_text: str = "Main Navigation Menu",
        footer_text: str = "Select an option from the menu"
    ) -> dict:
        """Formats native Meta dropdown list menu payload."""
        if not sections:
            sections = [
                {
                    "title": "Catalog & Ordering",
                    "rows": [
                        {"id": "menu_catalog", "title": "📦 Browse Products", "description": "View in-stock solar, generator & inverter items"},
                        {"id": "menu_buy", "title": "🛍️ Place Order (#buy)", "description": "Connect with store manager to order"}
                    ]
                },
                {
                    "title": "Logistics & Support",
                    "rows": [
                        {"id": "menu_shipping", "title": "🚚 Shipping & Rates", "description": "Nationwide delivery timelines & fees"},
                        {"id": "menu_payment", "title": "💳 Payment Options", "description": "Bank transfer details & POD rules"},
                        {"id": "menu_human", "title": "📞 Connect with Manager", "description": "Direct human manager assistance"}
                    ]
                }
            ]

        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": header_text},
                "body": {"text": body_text},
                "footer": {"text": footer_text},
                "action": {
                    "button": menu_button_title[:20],
                    "sections": sections
                }
            }
        }


whatsapp_interactive = WhatsAppInteractiveEngine()
