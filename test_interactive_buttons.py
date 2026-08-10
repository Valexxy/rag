"""
====================================================================
META NATIVE INTERACTIVE BUTTONS & LIST MENU TEST
====================================================================
"""
import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
from whatsapp_interactive_buttons import whatsapp_interactive

token = "EAAMgsrreXPYBSPLhSw7pvMv7LFq7vJRGuQbfk2vXY30sTZAkYw84s6zvymbKUb7kmzpaqY4YoXRj79joY6GaKZAGHICV8pqkrPc76texKYVqX0Smjf6gk6Pv3ACutxF3Ay4ByerlhWHtLpme8rRO0zTAMASbQ4JKW7UnbmF6cCZAPIIeV2n1cPo0IGEBFg1jwZDZD"
phone_id = "1242614362274985"
to_phone = "2348072015725"

url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 1. Send Interactive Quick Buttons
buttons = [
    {"id": "btn_catalog", "title": "📦 Browse Products"},
    {"id": "btn_buy", "title": "🛍️ Place Order"},
    {"id": "btn_human", "title": "📞 Call Manager"}
]
payload1 = whatsapp_interactive.build_quick_buttons_payload(
    to_phone=to_phone,
    body_text="Welcome to Teeslux Global! Tap any button below to navigate or place an order:",
    buttons=buttons
)

print("====================================================================")
print("🚀 SENDING NATIVE META QUICK BUTTONS TO WHATSAPP...")
print("====================================================================")
req1 = urllib.request.Request(url, headers=headers, data=json.dumps(payload1).encode('utf-8'))
try:
    with urllib.request.urlopen(req1, timeout=10) as r:
        print("✅ SUCCESS Buttons Sent! Status:", r.status)
        print("Response:", r.read().decode('utf-8'))
except Exception as e:
    print("❌ ERROR sending buttons:", e)

# 2. Send Interactive Dropdown List Menu
payload2 = whatsapp_interactive.build_list_menu_payload(
    to_phone=to_phone,
    body_text="Tap the menu button below to open our full store options & navigation list:"
)

print("\n====================================================================")
print("🚀 SENDING NATIVE META DROPDOWN LIST MENU TO WHATSAPP...")
print("====================================================================")
req2 = urllib.request.Request(url, headers=headers, data=json.dumps(payload2).encode('utf-8'))
try:
    with urllib.request.urlopen(req2, timeout=10) as r:
        print("✅ SUCCESS Menu Sent! Status:", r.status)
        print("Response:", r.read().decode('utf-8'))
except Exception as e:
    print("❌ ERROR sending list menu:", e)
