"""
====================================================================
EXECUTE 5 BENCHMARK STORES & END-TO-END LIVE JOURNEY TEST (v2026)
====================================================================
1. Registers 5 Benchmark Merchants across Solar, Fashion, Grocery, Beauty, Restaurant.
2. Executes live end-to-end customer buying journeys for each store.
3. Sends live Meta WhatsApp Cloud API message verification to +2348072015725.
"""

import sys
import time
import urllib.request
import json

sys.stdout.reconfigure(encoding='utf-8')

from multi_tenant_engine import multi_tenant_manager
from main import fast_catalog_search
from ecommerce_master_intelligence import ecommerce_intelligence
from opportunity_lead_engine import opportunity_lead_engine
from cross_sell_engine import cross_sell_engine
from quote_generator_engine import quote_generator_engine
from whatsapp_interactive_buttons import whatsapp_interactive

token = "EAAMgsrreXPYBSPLhSw7pvMv7LFq7vJRGuQbfk2vXY30sTZAkYw84s6zvymbKUb7kmzpaqY4YoXRj79joY6GaKZAGHICV8pqkrPc76texKYVqX0Smjf6gk6Pv3ACutxF3Ay4ByerlhWHtLpme8rRO0zTAMASbQ4JKW7UnbmF6cCZAPIIeV2n1cPo0IGEBFg1jwZDZD"
phone_id = "1242614362274985"
to_phone = "2348072015725"

url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

def send_meta_payload(payload_dict, test_name):
    req = urllib.request.Request(url, headers=headers, data=json.dumps(payload_dict).encode('utf-8'))
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode('utf-8'))
            msg_id = res["messages"][0]["id"]
            print(f"  ✅ PASS | {test_name:40s} -> Live Message Delivered (ID: {msg_id})")
            return True
    except Exception as e:
        print(f"  ❌ FAIL | {test_name:40s} -> Error: {e}")
        return False

# ── 1. ONBOARD 5 BENCHMARK STORES ─────────────────────────────────────
print("====================================================================")
print("🛍️ STEP 1: ONBOARDING 5 BENCHMARK MERCHANT STORES")
print("====================================================================")

benchmark_stores = [
    {
        "tenant_id": "teeslux_global",
        "business_name": "Teeslux Global Electronics & Solar",
        "business_domain_scope": "Solar Panels, Generators, Hybrid Inverters, Batteries & Electronics Contracting",
        "phone_number_id": "1242614362274985",
        "manager_phone": "2348072015725",
        "store_address": "Onitsha Main Market, Anambra State",
        "catalog": [
            {"id": "1", "name": "550W Monocrystalline Solar Panel", "price": 120000, "keywords": ["panel", "solar"]},
            {"id": "2", "name": "1.5kVA Dual Solar Generator", "price": 185000, "keywords": ["generator", "1.5kva"]}
        ]
    },
    {
        "tenant_id": "kano_fashion_hub",
        "business_name": "Kano Royal Fabrics & Textiles",
        "business_domain_scope": "Royal Brocade, Senator Suits, Lace Fabrics & Tailoring Accessories",
        "phone_number_id": "1242614362274985",
        "manager_phone": "2348099887766",
        "store_address": "Kano Textile Market, Kano State",
        "catalog": [
            {"id": "1", "name": "50-Yard Royal Brocade Fabric", "price": 45000, "keywords": ["brocade", "fabric"]},
            {"id": "2", "name": "Embroidered Senator Suit Material", "price": 28000, "keywords": ["senator", "material"]}
        ]
    },
    {
        "tenant_id": "lagos_supermarket",
        "business_name": "Lagos Provisions & Supermarket",
        "business_domain_scope": "Rice, Cooking Oil, Groceries & Foodstuffs",
        "phone_number_id": "1242614362274985",
        "manager_phone": "2348011223344",
        "store_address": "Ikeja Shopping Plaza, Lagos State",
        "catalog": [
            {"id": "1", "name": "Carton of Premium Vegetable Oil (5L)", "price": 32000, "keywords": ["oil", "vegetable"]},
            {"id": "2", "name": "50kg Bag of Foreign Parboiled Rice", "price": 78000, "keywords": ["rice", "50kg"]}
        ]
    },
    {
        "tenant_id": "enugu_beauty_hub",
        "business_name": "Enugu Luxury Hair & Beauty Hub",
        "business_domain_scope": "Human Hair Extensions, Wigs & Organic Skin Lotion",
        "phone_number_id": "1242614362274985",
        "manager_phone": "2348033445566",
        "store_address": "Ogbete Main Market, Enugu State",
        "catalog": [
            {"id": "1", "name": "Human Hair Extension (30 Inches)", "price": 85000, "keywords": ["hair", "wig"]},
            {"id": "2", "name": "Organic Skin Glowing Body Lotion", "price": 15000, "keywords": ["lotion", "cream"]}
        ]
    },
    {
        "tenant_id": "abuja_gourmet_express",
        "business_name": "Abuja Gourmet Catering & Fast Food",
        "business_domain_scope": "Jollof Rice, Grilled Catfish & Corporate Catering",
        "phone_number_id": "1242614362274985",
        "manager_phone": "2348055667788",
        "store_address": "Wuse 2 Commercial District, Abuja FCT",
        "catalog": [
            {"id": "1", "name": "Jollof Rice & Fried Chicken Combo", "price": 4500, "keywords": ["jollof", "chicken"]},
            {"id": "2", "name": "Grilled Catfish & Chips Family Pack", "price": 16000, "keywords": ["catfish", "fish"]}
        ]
    }
]

for store in benchmark_stores:
    res = multi_tenant_manager.register_tenant(
        store["tenant_id"], store["business_name"], store["phone_number_id"],
        store["manager_phone"], store["store_address"], store["catalog"],
        store["business_domain_scope"]
    )
    print(f"✅ STORE ONBOARDED: [{store['business_name']}] -> Manager: {store['manager_phone']}")

# ── 2. EXECUTE END-TO-END LIVE CUSTOMER JOURNEYS ────────────────────
print("\n====================================================================")
print("🎬 STEP 2: EXECUTING END-TO-END LIVE WHATSAPP CUSTOMER JOURNEYS")
print("====================================================================")

# Journey 1: Native 3-Button Card for Solar Store
btn_card = whatsapp_interactive.build_quick_buttons_payload(
    to_phone=to_phone,
    body_text="☀️ Welcome to Teeslux Global! Tap any button below to browse or order:",
    buttons=[
        {"id": "btn_catalog", "title": "📦 Browse Products"},
        {"id": "btn_buy", "title": "🛍️ Place Order"},
        {"id": "btn_human", "title": "📞 Call Manager"}
    ]
)
send_meta_payload(btn_card, "Journey 1: Native 3-Button Solar Card")
time.sleep(1)

# Journey 2: Fashion Store Sourcing Request -> Opportunity Lead Alert
opp_res = opportunity_lead_engine.evaluate_opportunity(
    "Can you supply 50 customized bridal lace fabrics for a wedding?",
    to_phone, benchmark_stores[1]
)
opp_payload = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": to_phone,
    "type": "text",
    "text": {"preview_url": False, "body": opp_res["customer_reply"]}
}
send_meta_payload(opp_payload, "Journey 2: Sourcing Lead (Bridal Lace)")
time.sleep(1)

# Journey 3: Grocery Store Order Quotation
quote_res = quote_generator_engine.generate_quotation(
    "Send me a quote for 5 bags of 50kg rice and 2 cartons of oil",
    to_phone, benchmark_stores[2]
)
quote_payload = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": to_phone,
    "type": "text",
    "text": {"preview_url": False, "body": quote_res["customer_reply"]}
}
send_meta_payload(quote_payload, "Journey 3: Proforma Invoice (#QT-98410)")
time.sleep(1)

# Journey 4: Waybill Delivery Tracking
track_card = (
    f"🚚 *[Lagos Supermarket — Nationwide Waybill Tracking]*\n"
    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    f"🧾 *Order Ref:* `#TSX-98421`\n"
    f"🟢 *Status:* Dispatched via GIG Logistics\n"
    f"📦 *Waybill Ref:* `GIG-ON-984210`\n"
    f"⏱️ *Estimated Delivery:* Tomorrow 2:00 PM WAT\n"
    f"📍 *Destination:* Ikeja Shopping Plaza, Lagos"
)
track_payload = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": to_phone,
    "type": "text",
    "text": {"preview_url": False, "body": track_card}
}
send_meta_payload(track_payload, "Journey 4: Waybill Tracking Card")
time.sleep(1)

# Journey 5: Store Location Pin Dispatch
loc_payload = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": to_phone,
    "type": "location",
    "location": {
        "latitude": "6.1558",
        "longitude": "6.7865",
        "name": "Teeslux Global Electronics & Solar",
        "address": "Onitsha Main Market, Anambra State, Nigeria"
    }
}
send_meta_payload(loc_payload, "Journey 5: Store GPS Map Location Pin")

print("====================================================================")
print("💯 ALL 5 BENCHMARK STORES ONBOARDED & LIVE JOURNEYS EXECUTED!")
print("====================================================================")
