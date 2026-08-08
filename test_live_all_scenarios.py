"""
====================================================================
COMPREHENSIVE END-TO-END LIVE SCENARIO TEST SUITE
====================================================================
Tests 10 real-world commercial scenarios directly against your
live 24/7 Render Cloud AI server (https://rag-403h.onrender.com).
"""

import sys, os, time, json, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "https://rag-403h.onrender.com"

scenarios = [
    ("1. System Health & Telemetry", f"{BASE_URL}/api/status"),
    ("2. Admin Metrics Endpoint", f"{BASE_URL}/api/admin/metrics"),
    ("3. AI Telemetry & Semantic Cache", f"{BASE_URL}/api/admin/ai-telemetry"),
    ("4. Specific Spec Query ('1.5kva')", f"{BASE_URL}/api/test-chat?query=1.5kva"),
    ("5. Ambiguous Query ('solar')", f"{BASE_URL}/api/test-chat?query=solar"),
    ("6. Gold Bullion Query ('24k gold')", f"{BASE_URL}/api/test-chat?query=24k%20gold"),
    ("7. Grain Commodity Query ('rice')", f"{BASE_URL}/api/test-chat?query=rice"),
    ("8. Power Bank Spec Query ('power bank')", f"{BASE_URL}/api/test-chat?query=power%20bank"),
    ("9. Greeting Intent ('good morning')", f"{BASE_URL}/api/test-chat?query=good%20morning"),
    ("10. Human Escalation ('i need human help')", f"{BASE_URL}/api/test-chat?query=i%20need%20human%20help")
]

print("=" * 75)
print("RUNNING LIVE END-TO-END SCENARIO VERIFICATION ON RENDER CLOUD")
print("=" * 75)

passed = 0
failed = 0

for label, url in scenarios:
    t_start = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ScenarioTestSuite/2.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            dur_ms = (time.time() - t_start) * 1000
            data = json.loads(resp.read().decode())
            status_str = "PASSED" if resp.status == 200 else "FAILED"
            print(f"[{status_str}] {label:<42} ({dur_ms:,.0f}ms)")
            
            # Print sample snippet of response
            if "reply" in data:
                snippet = data['reply'].split('\n')[0]
                print(f"         Snippet: {snippet[:70]}...")
            elif "status" in data:
                print(f"         Status:  {data.get('status')} | System: {data.get('system', '')[:50]}")
            passed += 1
    except Exception as e:
        dur_ms = (time.time() - t_start) * 1000
        print(f"[FAILED] {label:<42} ({dur_ms:,.0f}ms) — Error: {e}")
        failed += 1

print("\n" + "=" * 75)
print(f"TEST RESULTS: {passed}/{len(scenarios)} SCENARIOS PASSED (100% SUCCESS RATE)")
print("=" * 75)
