"""
====================================================================
PREMIUM META & TELEGRAM FEATURES TEST SUITE
====================================================================
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from premium_meta_telegram_engine import premium_meta_telegram_engine

tenant = {
    "business_name": "Teeslux Global Electronics & Solar",
    "manager_phone": "2348072015725",
    "store_address": "Onitsha Main Market, Anambra State, Nigeria"
}

test_commands = [
    ("/start", "slash_menu"),
    ("/catalog", "slash_catalog"),
    ("/track #TSX-99881", "slash_track"),
    ("/location", "slash_location"),
    ("/support", "slash_support")
]

print("====================================================================")
print("🚀 TESTING TELEGRAM-STYLE SLASH COMMANDS & META PREMIUM FEATURES")
print("====================================================================")

for cmd, expected_type in test_commands:
    res = premium_meta_telegram_engine.process_slash_command(cmd, "2348072015725", tenant)
    assert res is not None, f"Failed on command: {cmd}"
    assert res["type"] == expected_type, f"Expected {expected_type}, got {res['type']}"
    print(f"✅ PASS | Command: '{cmd}' -> Executed: [{res['type'].upper()}]")

print("====================================================================")
print("💯 ALL PREMIUM META & TELEGRAM FEATURES PASSED 100% PERFECTLY!")
print("====================================================================")
