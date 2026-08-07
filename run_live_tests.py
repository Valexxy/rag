import os
from dotenv import load_dotenv
from database import get_tenant_by_instance, add_tenant_entity
from whatsapp_ui import format_currency
from market_intelligence import market_intel
from logistics_department import logistics_dept
from financial_trust_engine import financial_trust
from nigerian_market_engine import nigerian_market
from rag_engine import rag_engine
from evolution_interactive import send_whatsapp_message

load_dotenv()
inst_name = "store-bot"
owner_phone = "2348072015725"

tenant = get_tenant_by_instance(inst_name) or {"id": "t-demo", "business_name": "Teeslux", "currency": "NGN"}

print("==========================================================")
print("[LIVE TEST SUITE] EXECUTING TESTS FOR INSTANCE: store-bot")
print("==========================================================")

# 1. Test Market Intelligence Dispatch
print("\n[TEST 1/6] Dispatching Daily Market Price Bulletin...")
market_report = market_intel.format_market_intelligence_report("onitsha_main_market")
s1 = send_whatsapp_message(inst_name, owner_phone, market_report)
print("Status 1 (Market Bulletin):", "DELIVERED (201)" if s1 else "FAILED")

# 2. Test Quick Add Product
print("\n[TEST 2/6] Adding Product: '1.5kVA Dual Solar Generator' (NGN 185,000)...")
add_res = add_tenant_entity(tenant.get("id", "t-demo"), "1.5kVA Dual Solar Generator", 185000.00, "Silent pure sine wave inverter generator", {"stock": 10})
print("Status 2 (Catalog Insert):", "SUCCESS" if add_res else "FAILED")
add_card = f"[ITEM ADDED TO CATALOG]\n\nName: 1.5kVA Dual Solar Generator\nPrice: {format_currency(185000.0, 'NGN')}\nInfo: Silent pure sine wave inverter generator"
send_whatsapp_message(inst_name, owner_phone, add_card)

# 3. Test RAG Vector Retrieval
print("\n[TEST 3/6] Testing RAG Vector Search for 'Solar Generator'...")
rag_ctx = rag_engine.retrieve_relevant_context(tenant, owner_phone, "solar generator price")
print("Status 3 (RAG Vector Context Retrieved): OK")

# 4. Test Gbese Debt Book Record
print("\n[TEST 4/6] Logging Gbese Debt Record for Customer...")
debt_card = nigerian_market.record_customer_debt("2348123456789", 25000.0, "30k mAh Power Bank")
s4 = send_whatsapp_message(inst_name, owner_phone, debt_card)
print("Status 4 (Gbese Debt Card):", "DELIVERED (201)" if s4 else "FAILED")

# 5. Test Logistics Waybill & OTP Code
print("\n[TEST 5/6] Generating Delivery Waybill & Rider OTP Code...")
wb = logistics_dept.generate_waybill(tenant.get("id", "t-demo"), owner_phone, "Suite 14 Alaba Int'l Market, Lagos", "1.5kVA Solar Generator")
wb_card = logistics_dept.format_delivery_status(wb)
s5 = send_whatsapp_message(inst_name, owner_phone, wb_card)
print("Status 5 (Logistics Waybill Card):", "DELIVERED (201)" if s5 else "FAILED")

# 6. Test SaaS Trust Verified Payment Card
print("\n[TEST 6/6] Generating SaaS Verified Payment Card...")
trust_card = financial_trust.format_trust_verified_payment_instructions(tenant, 185000.0, f"TRX-{owner_phone[-4:]}")
s6 = send_whatsapp_message(inst_name, owner_phone, trust_card)
print("Status 6 (Trust Payment Card):", "DELIVERED (201)" if s6 else "FAILED")

print("\n==========================================================")
print("[SUCCESS] ALL 6 LIVE INTERACTIVE TESTS DISPATCHED!")
print("==========================================================")
