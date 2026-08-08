"""
TEST LIVE WHATSAPP MESSAGE DISPATCH VIA EVOLUTION API ON RENDER
"""

import sys, os
sys.stdout.reconfigure(encoding='utf-8')

from evolution_interactive import send_whatsapp_message

test_phone = "2348072015725"
test_msg = (
    "🛍️ *[Teeslux Store — Product Found]*\n\n"
    "✅ *24K Gold Bar Bullion (1-Gram)*\n"
    "💰 *Fixed Price:* ₦68,500.00\n"
    "📦 *Status:* In Stock\n"
    "📝 *Details:* 999.9 Fine Investment Gold Bar with LBMA & Assay certificate\n\n"
    "💬 Reply *#buy* to place your order, or *#human* to speak with our manager."
)

print(f"Sending test WhatsApp message for '24k gold' to {test_phone}...")
success = send_whatsapp_message("store-bot", test_phone, test_msg)
print(f"Result: {'✅ SENT SUCCESSFULLY' if success else '❌ FAILED TO SEND'}")
