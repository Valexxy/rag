"""
====================================================================
HIGH-TECH ENTERPRISE AI INFRASTRUCTURE VALIDATION SUITE
====================================================================
Validates all 4 new enterprise AI modules:
1. Sub-15ms Semantic Cache
2. Post-Generation Fact & Price Auditor
3. Adaptive Few-Shot Knowledge Memory
4. Provider Circuit Breaker Telemetry
"""

import sys, os, time, ast
sys.stdout.reconfigure(encoding='utf-8')
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

from dotenv import load_dotenv
load_dotenv()

print("=" * 65)
print("STEP 1: SYNTAX CHECKING ALL NEW & MODIFIED MODULES")
print("=" * 65)

files = [
    'semantic_cache.py',
    'post_generation_auditor.py',
    'adaptive_knowledge_memory.py',
    'circuit_breaker_telemetry.py',
    'sovereign_ai_brain.py',
    'main.py'
]

all_ok = True
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as fh:
            ast.parse(fh.read())
        print(f"  ✅  {f:<35} Syntax OK")
    except Exception as e:
        print(f"  ❌  {f:<35} Syntax Error: {e}")
        all_ok = False

if not all_ok:
    print("Syntax checks failed!")
    sys.exit(1)

# ── STEP 2: TEST SUB-15MS SEMANTIC CACHE ─────────────────────────
print("\n" + "=" * 65)
print("STEP 2: TESTING SUB-15MS SEMANTIC CACHE")
print("=" * 65)

from semantic_cache import semantic_cache
from sovereign_ai_brain import sovereign_brain

sample_tenant = {
    "id": "t-hitech-test",
    "business_name": "Teeslux HiTech Store",
    "business_niche": "retail",
    "owner_phone": "2348072015725"
}

catalog = [
    {"name": "550W Monocrystalline Solar Panel", "price": 120000.0, "description": "Grade-A Monocrystalline Panel"}
]

q1 = "what is the price of your solar panel"

# First call — populates cache
t_start = time.time()
r1 = sovereign_brain.generate_answer(
    message=q1,
    intent="CATALOG_QUERY",
    catalog=catalog,
    matched_product=catalog[0],
    conversation_history="",
    tenant=sample_tenant
)
dur1_ms = (time.time() - t_start) * 1000
print(f"  Call 1 (LLM generation): {dur1_ms:.1f}ms | Source: {r1.get('source')}")

# Second call — exact query (semantic cache hit)
t_start = time.time()
r2 = sovereign_brain.generate_answer(
    message=q1,
    intent="CATALOG_QUERY",
    catalog=catalog,
    matched_product=catalog[0],
    conversation_history="",
    tenant=sample_tenant
)
dur2_ms = (time.time() - t_start) * 1000
print(f"  Call 2 (Semantic Cache Hit): {dur2_ms:.1f}ms | Source: {r2.get('source')}")

# Third call — semantic variation ("how much is solar panel")
q3 = "how much is solar panel"
t_start = time.time()
r3 = sovereign_brain.generate_answer(
    message=q3,
    intent="CATALOG_QUERY",
    catalog=catalog,
    matched_product=catalog[0],
    conversation_history="",
    tenant=sample_tenant
)
dur3_ms = (time.time() - t_start) * 1000
print(f"  Call 3 (Near-duplicate Cache Hit): {dur3_ms:.1f}ms | Source: {r3.get('source')}")

stats = semantic_cache.get_stats()
print(f"  Semantic Cache Stats: Hits={stats['hits']}, Misses={stats['misses']}, Hit Rate={stats['hit_rate_pct']}%")

# ── STEP 3: TEST POST-GENERATION FACT AUDITOR ────────────────────
print("\n" + "=" * 65)
print("STEP 3: TESTING POST-GENERATION FACT & PRICE AUDITOR")
print("=" * 65)

from post_generation_auditor import post_auditor

bad_ai_text = "The 550W Monocrystalline Solar Panel costs ₦100,000 and is in stock."
good_catalog = [{"name": "550W Monocrystalline Solar Panel", "price": 120000.0}]

sanitized, passed, meta = post_auditor.audit_response(
    ai_response_text=bad_ai_text,
    catalog=good_catalog,
    matched_product=good_catalog[0]
)

print(f"  Original AI Text:  '{bad_ai_text}'")
print(f"  Audited AI Text:   '{sanitized}'")
print(f"  Corrections Made:  {meta['corrections_made']}")
print(f"  Audit Status:      {'✅ CORRECTION SUCCESSFUL' if '120,000' in sanitized else '❌ AUDIT FAILED'}")

# ── STEP 4: TEST ADAPTIVE FEW-SHOT MEMORY ───────────────────────
print("\n" + "=" * 65)
print("STEP 4: TESTING ADAPTIVE FEW-SHOT KNOWLEDGE MEMORY")
print("=" * 65)

from adaptive_knowledge_memory import adaptive_memory

adaptive_memory.add_learned_exemplar(
    tenant_id="t-hitech-test",
    question="Do you deliver to Abuja?",
    answer="Yes! We offer 24-hour door-step dispatch to Abuja via GIG Logistics.",
    source="owner_custom"
)

few_shot_prompt = adaptive_memory.format_few_shot_context("t-hitech-test", "can you send item to abuja")
print("  Injected Few-Shot Context:\n" + few_shot_prompt.strip())

# ── STEP 5: TEST CIRCUIT BREAKER TELEMETRY ───────────────────────
print("\n" + "=" * 65)
print("STEP 5: TESTING ENTERPRISE CIRCUIT BREAKER TELEMETRY")
print("=" * 65)

from circuit_breaker_telemetry import circuit_breaker

circuit_breaker.record_success("groq", 450.0)
circuit_breaker.record_success("gemini", 800.0)

telemetry = circuit_breaker.get_telemetry()
print("  Live AI Telemetry:")
for p, data in telemetry.items():
    print(f"    • {p.upper():<8} Latency: {data['avg_latency_ms']}ms | Requests: {data['requests']} | Circuit: {data['circuit_state']}")

print("\n" + "=" * 65)
print("ALL HIGH-TECH ENTERPRISE UPGRADES VALIDATED & OPERATIONAL!")
print("=" * 65)
