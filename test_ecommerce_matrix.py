"""
====================================================================
E-COMMERCE MASTER MATRIX TEST SUITE
====================================================================
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from ecommerce_master_intelligence import ecommerce_intelligence

tenant = {
    "business_name": "Teeslux Global Electronics & Solar",
    "manager_phone": "2348072015725"
}

test_queries = [
    ("I want to buy 50 solar panels wholesale for resale", "wholesale"),
    ("My inverter is faulty and not working, I need warranty repair", "after_sales_warranty"),
    ("How much will it cost to ship 3 generators to Abuja?", "logistics"),
    ("Can I pay cash on delivery or transfer to your bank account?", "payment_options"),
    ("I need a certified technician for home solar panel installation", "installation"),
    ("Can you give me a special discount on the 3.5kva inverter?", "haggling"),
]

print("====================================================================")
print("🚀 TESTING MASTER E-COMMERCE INTELLIGENCE MATRIX")
print("====================================================================")

for q, expected_type in test_queries:
    res = ecommerce_intelligence.analyze_and_route(q, "2348072015725", tenant)
    assert res is not None, f"Failed on query: {q}"
    assert res["type"] == expected_type, f"Expected {expected_type}, got {res['type']}"
    print(f"✅ PASS | Query: '{q[:40]}...' -> Detected Intent: [{res['type'].upper()}]")

print("====================================================================")
print("💯 ALL REAL-WORLD E-COMMERCE SCENARIOS PASSED 100% PERFECTLY!")
print("====================================================================")
