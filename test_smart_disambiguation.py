import sys, os
sys.stdout.reconfigure(encoding='utf-8')

from database import get_tenant_by_instance, get_tenant_catalog
from semantic_catalog_engine import semantic_catalog

tenant = get_tenant_by_instance("store-bot")
catalog = get_tenant_catalog(tenant)

print("=" * 70)
print("TESTING SMART MULTI-CANDIDATE DISAMBIGUATION ENGINE")
print("=" * 70)

queries = [
    "1.5kva",
    "solar",
    "generator",
    "24k gold"
]

for q in queries:
    res = semantic_catalog.search(q, catalog)
    print(f"\nQUERY: '{q}' | MATCHED: {res.get('matched')} | METHOD: {res.get('method')}")
    print("-" * 50)
    print(res.get("reply"))
    print("=" * 70)
