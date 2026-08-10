"""
====================================================================
GAME-CHANGER INNOVATIONS TEST SUITE
====================================================================
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from opportunity_lead_engine import opportunity_lead_engine
from cross_sell_engine import cross_sell_engine
from quote_generator_engine import quote_generator_engine

tenant = {
    "business_name": "Teeslux Global Electronics & Solar",
    "manager_phone": "2348072015725",
    "store_address": "Onitsha Main Market, Anambra State, Nigeria",
    "catalog": [
        {"name": "550W Monocrystalline Solar Panel", "price": 120000},
        {"name": "1.5kVA Dual Solar Generator", "price": 185000}
    ]
}

print("====================================================================")
print("🚀 TESTING 3 GAME-CHANGER INNOVATIONS")
print("====================================================================")

# 1. Test Opportunity Sourcing Lead Engine
res1 = opportunity_lead_engine.evaluate_opportunity("Can you supply 100 sets of solar streetlights?", "2348072015725", tenant)
assert res1 is not None and "sourcing_opportunity" in res1["type"]
print("✅ PASS 1 | Opportunity Lead Engine -> [SOURCING_OPPORTUNITY] (Manager Alerted with Sourcing Lead)")

# 2. Test Smart Cross-Sell Add-ons
res2 = cross_sell_engine.get_cross_sell_addons("550w solar panel")
assert res2 is not None and "Battery Rack" in res2
print("✅ PASS 2 | Cross-Sell Engine -> Smart Add-on Accessories Recommended")

# 3. Test Quotation Generator Engine
res3 = quote_generator_engine.generate_quotation("Send me a quote for 4 solar panels", "2348072015725", tenant)
assert res3 is not None and "OFFICIAL PROFORMA QUOTATION" in res3["customer_reply"]
print("✅ PASS 3 | Quote Generator Engine -> Instant Formal WhatsApp Proforma Invoice Issued")

print("====================================================================")
print("💯 ALL 3 GAME-CHANGER INNOVATIONS PASSED 100% PERFECTLY!")
print("====================================================================")
