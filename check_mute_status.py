"""
CHECK AND CLEAR BOT MUTE STATUS FOR TEST PHONE NUMBERS
"""

import sys, os
sys.stdout.reconfigure(encoding='utf-8')

from database import supabase, get_tenant_by_instance, is_tenant_bot_muted, unmute_tenant_bot

tenant = get_tenant_by_instance("store-bot")
tid = tenant.get("id")

test_phones = ["2348072015725", "2347061114753"]

print("=" * 65)
print("BOT MUTE STATUS CHECK")
print("=" * 65)
print(f"Tenant ID: {tid}")

for phone in test_phones:
    muted = is_tenant_bot_muted(tid, phone)
    print(f"  Phone {phone}: Muted = {muted}")
    if muted:
        unmute_tenant_bot(tid, phone)
        print(f"  ✅ Unmuted {phone} successfully!")

print("\n--- ALL BOT MUTES CLEARED IN SUPABASE ---")
