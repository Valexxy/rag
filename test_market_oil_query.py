"""
TRACE QUERY: 'which market can i get oil if you dont sell'
"""

import sys, json, requests
sys.stdout.reconfigure(encoding='utf-8')

from database import get_tenant_by_instance
from character_engine import generate_live_character_reply

tenant = get_tenant_by_instance("store-bot")

query = "which market can i get oil if you dont sell"
print("Tracing Query:", query)

res = generate_live_character_reply(
    tenant=tenant,
    customer_phone="2348072015725",
    latest_query=query,
    conversation_history=""
)

print("\nCHARACTER ENGINE RESULT:")
print(json.dumps(res, indent=2))
