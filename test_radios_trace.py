"""
TRACE QUERY: 'do you sell radios'
"""

import sys, json, time
sys.stdout.reconfigure(encoding='utf-8')

from database import get_tenant_by_instance, get_tenant_catalog
from sovereign_ai_brain import sovereign_brain
from semantic_catalog_engine import semantic_catalog
from character_engine import generate_live_character_reply

tenant = get_tenant_by_instance("store-bot")
catalog = get_tenant_catalog(tenant["id"])

query = "do you sell radios"
print("Tracing Query:", query)

# 1. Intent classification
t0 = time.time()
intent_res = sovereign_brain.classify_intent(query, catalog)
print(f"Intent Classification ({time.time()-t0:.2f}s):", intent_res)

# 2. Semantic search
t1 = time.time()
sem_res = semantic_catalog.search_with_intent(intent_res.get("product_query"), query, catalog)
print(f"Semantic Catalog Search ({time.time()-t1:.2f}s):", sem_res)

# 3. Full Character Engine
t2 = time.time()
char_res = generate_live_character_reply(tenant, "2348072015725", query, "")
print(f"Character Engine Output ({time.time()-t2:.2f}s):")
print(json.dumps(char_res, indent=2))
