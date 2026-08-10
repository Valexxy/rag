"""
====================================================================
STRICT TENANT 2-TIER CLASSIFICATION TEST SUITE
====================================================================
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from strict_domain_guardrail import strict_domain_guardrail

tenant = {
    "business_name": "Teeslux Global Electronics & Solar",
    "manager_phone": "2348072015725",
    "catalog": [
        {"name": "550W Monocrystalline Solar Panel", "keywords": ["solar", "panel"]},
        {"name": "1.5kVA Dual Solar Generator", "keywords": ["generator", "1.5kva"]}
    ]
}

print("====================================================================")
print("🛡️ TESTING 2-TIER SMART DOMAIN CLASSIFICATION")
print("====================================================================")

# 1. Test In-Domain Business Query
res1 = strict_domain_guardrail.classify_query("How much is 1.5kva generator?", tenant)
assert res1 == "IN_DOMAIN", f"Expected IN_DOMAIN, got {res1}"
print("✅ PASS 1 | In-Domain Query -> [IN_DOMAIN]")

# 2. Test Business Lead Out-of-Catalog Query
res2 = strict_domain_guardrail.classify_query("Do you sell laptop chargers?", tenant)
assert res2 == "BUSINESS_OUT_OF_CATALOG", f"Expected BUSINESS_OUT_OF_CATALOG, got {res2}"
card2 = strict_domain_guardrail.handle_business_out_of_catalog("Do you sell laptop chargers?", "2348072015725", tenant)
assert card2["manager_alert"] is not None
print("✅ PASS 2 | Business Out-of-Catalog -> [BUSINESS_OUT_OF_CATALOG] (Manager Alerted)")

# 3. Test Rubbish Off-Topic Query (UEFA / Football)
res3 = strict_domain_guardrail.classify_query("Who won UEFA yesterday?", tenant)
assert res3 == "RUBBISH_OFF_TOPIC", f"Expected RUBBISH_OFF_TOPIC, got {res3}"
card3 = strict_domain_guardrail.handle_rubbish_off_topic(tenant)
assert card3["manager_alert"] is None  # ZERO Manager Distraction!
print("✅ PASS 3 | Rubbish Off-Topic (UEFA) -> [RUBBISH_OFF_TOPIC] (Clean Notice, ZERO Manager Distraction)")

print("====================================================================")
print("💯 100% 2-TIER CLASSIFICATION PASSED PERFECTLY!")
print("====================================================================")
