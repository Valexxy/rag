"""
TRACE QUERY: 'do you sell cigarette'
"""

import sys, json, time, requests
sys.stdout.reconfigure(encoding='utf-8')

from database import get_tenant_by_instance, get_tenant_catalog
from sovereign_ai_brain import sovereign_brain
from character_engine import generate_live_character_reply

tenant = get_tenant_by_instance("store-bot")

query = "do you sell cigarette"
print("Tracing Query:", query)

# 1. Test live endpoint on Render Cloud
url = f"https://rag-403h.onrender.com/api/test-chat?query={requests.utils.quote(query)}"
r = requests.get(url)
print("\nLIVE RENDER CLOUD RESPONSE:")
print("Status Code:", r.status_code)
print("Payload:", json.dumps(r.json(), indent=2))
