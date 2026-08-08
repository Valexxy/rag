"""
DEBUG SCRIPT: TESTING '24k gold' QUERY PROCESSING PIPELINE
"""

import sys, os, json, time
sys.stdout.reconfigure(encoding='utf-8')
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

from dotenv import load_dotenv
load_dotenv()

from database import get_tenant_by_instance, get_tenant_catalog
from sovereign_ai_brain import sovereign_brain
from semantic_catalog_engine import semantic_catalog
from character_engine import generate_live_character_reply

print("=" * 60)
print("DEBUGGING QUERY: '24k gold'")
print("=" * 60)

tenant = get_tenant_by_instance("store-bot")
print(f"1. Tenant loaded: '{tenant.get('business_name')}' (ID: {tenant.get('id')})")

catalog = get_tenant_catalog(tenant)
print(f"2. Catalog size from database: {len(catalog)} items")
for item in catalog:
    print(f"   • {item.get('name')} (Price: ₦{item.get('price',0):,.2f})")

query = "24k gold"

# 3. Intent Classification
intent_res = sovereign_brain.classify_intent(
    message=query,
    catalog=catalog,
    conversation_history=""
)
print(f"\n3. Sovereign Brain Intent Classification:")
print(f"   Intent:        {intent_res.get('intent')}")
print(f"   Product Query: {intent_res.get('product_query')}")
print(f"   Confidence:    {intent_res.get('confidence')}")
print(f"   Source:        {intent_res.get('source')}")

# 4. Semantic Search
search_res = semantic_catalog.search_with_intent(
    product_query=intent_res.get("product_query"),
    full_message=query,
    catalog=catalog
)
print(f"\n4. Semantic Catalog Search Result:")
print(f"   Matched:       {search_res.get('matched')}")
print(f"   Matched Item:  {search_res.get('item', {}).get('name') if search_res.get('matched') else None}")
print(f"   Score:         {search_res.get('score')}")
print(f"   Method:        {search_res.get('method')}")

# 5. Character Engine Reply Generation
reply_res = generate_live_character_reply(
    message=query,
    tenant_id=tenant.get("id"),
    customer_phone="2348072015725"
)
print(f"\n5. Character Engine Live Reply Generation:")
print(f"   Reply Text:\n{reply_res.get('reply')}")
print(f"   Is Transfer:   {reply_res.get('is_human_transfer')}")

print("\n" + "=" * 60)
