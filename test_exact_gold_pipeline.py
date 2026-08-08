import sys, os
sys.stdout.reconfigure(encoding='utf-8')
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

from dotenv import load_dotenv
load_dotenv()

from database import get_tenant_by_instance
from character_engine import generate_live_character_reply

tenant = get_tenant_by_instance("store-bot")

res = generate_live_character_reply(
    tenant=tenant,
    customer_phone="2348072015725",
    latest_query="24k gold",
    conversation_history=""
)

print("=" * 60)
print("LIVE RESPONSE FOR '24k gold':")
print("=" * 60)
print(res.get("reply"))
print("=" * 60)
print("SOURCE:", res.get("source"))
print("IS TRANSFER:", res.get("is_human_transfer"))
