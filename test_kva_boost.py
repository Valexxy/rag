import sys, os
sys.stdout.reconfigure(encoding='utf-8')

from database import get_tenant_by_instance, get_tenant_catalog
from semantic_catalog_engine import semantic_catalog

tenant = get_tenant_by_instance("store-bot")
catalog = get_tenant_catalog(tenant)

test_queries = ["1.5kva", "3.5kva", "24k gold", "rice", "power bank", "solar panel"]

print("=" * 65)
print("TESTING SPECIFICATION MATCHER FOR ALL PRODUCT QUERIES")
print("=" * 65)

for q in test_queries:
    res = semantic_catalog.search(q, catalog)
    matched_name = res.get("item", {}).get("name") if res.get("matched") else "NO MATCH"
    print(f"Query: '{q:<12}' | Matched: {res.get('matched')} | Score: {res.get('score'):.4f} | Product: {matched_name}")

print("=" * 65)
