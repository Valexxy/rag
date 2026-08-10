"""
====================================================================
ORDER ENGINE VERIFICATION TEST
====================================================================
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from order_placement_engine import order_placement_engine

tenant = {
    "business_name": "Teeslux Global Electronics & Solar",
    "manager_phone": "2348072015725",
    "catalog": [
        {"id": "1", "name": "550W Monocrystalline Solar Panel", "price": 120000.0},
        {"id": "2", "name": "1.5kVA Dual Solar Generator", "price": 185000.0}
    ]
}

res = order_placement_engine.process_buy_command("#buy 2", "2348072015725", tenant)
print("====================================================================")
print("🧾 CUSTOMER RECEIPT CARD:")
print("====================================================================")
print(res["customer_reply"])
print("\n====================================================================")
print("🚨 MANAGER ALERT CARD:")
print("====================================================================")
print(res["manager_alert"])
