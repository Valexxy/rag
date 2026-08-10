"""
====================================================================
STRICT TENANT DOMAIN GUARDRAIL TEST SUITE
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

valid_queries = [
    "What solar panel do you have in stock?",
    "How much is your 1.5kva generator?",
    "What is your store location in Onitsha?"
]

abuse_queries = [
    "Write a Python script to scrape a website",
    "Tell me a story about football and politics",
    "Who is the president of the United States?"
]

print("====================================================================")
print("🛡️ TESTING STRICT TENANT DOMAIN GUARDRAIL & ANTI-ABUSE ENGINE")
print("====================================================================")

for q in valid_queries:
    allowed = strict_domain_guardrail.is_query_in_tenant_domain(q, tenant)
    assert allowed, f"Valid query wrongly rejected: {q}"
    print(f"✅ PASS | Valid Business Query ALLOWED: '{q}'")

for q in abuse_queries:
    allowed = strict_domain_guardrail.is_query_in_tenant_domain(q, tenant)
    assert not allowed, f"Abuse query wrongly allowed: {q}"
    res = strict_domain_guardrail.handle_out_of_domain(q, "2348072015725", tenant)
    assert "out_of_domain_handoff" in res["type"]
    print(f"✅ PASS | Off-Topic Abuse REJECTED & ROUTED TO MANAGER: '{q}'")

print("====================================================================")
print("💯 100% STRICT TENANT DOMAIN GUARDRAIL PASSED PERFECTLY!")
print("====================================================================")
