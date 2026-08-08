"""
TESTING SMART PURCHASE & UNCATALOGUED PRODUCT HANDLING
"""

import sys, os
sys.stdout.reconfigure(encoding='utf-8')

from database import get_tenant_by_instance, get_tenant_catalog
from semantic_catalog_engine import semantic_catalog
from local_ai_brain import local_brain

tenant = get_tenant_by_instance("store-bot")
catalog = get_tenant_catalog(tenant["id"])

query = "I want to buy groundnut oil"
print("Query:", query)

# Search catalog
res = semantic_catalog.search_with_intent("groundnut oil", query, catalog)
print("Semantic Catalog Result:", res)

match_local = local_brain.match_catalog_product(tenant, query)
print("Local Brain Match:", match_local)
