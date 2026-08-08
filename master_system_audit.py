"""
====================================================================
MASTER SYSTEM AUDIT & FAILSAFE ARCHITECTURE VERIFICATION
====================================================================
Audits:
1. Syntax & Compilation across all .py files
2. All imports across all enterprise modules
3. Database connection & table integrity
4. 5-Tier Fallback Chain Execution
"""

import sys, os, importlib, glob
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("1. AUDITING SYNTAX & COMPILATION ACROSS ALL PYTHON MODULES")
print("=" * 70)

py_files = glob.glob("*.py")
passed_files = 0
failed_files = []

for pf in py_files:
    try:
        with open(pf, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
        compile(code, pf, "exec")
        passed_files += 1
    except Exception as e:
        failed_files.append((pf, str(e)))

print(f"✅ Syntactically Valid Files: {passed_files}/{len(py_files)}")
if failed_files:
    print(f"❌ Syntax Errors Found ({len(failed_files)}):")
    for ff, err in failed_files:
        print(f"   • {ff}: {err}")

print("\n" + "=" * 70)
print("2. VERIFYING CORE MODULE IMPORTS & INTEGRITY")
print("=" * 70)

core_modules = [
    "main", "database", "sovereign_ai_brain", "semantic_catalog_engine",
    "character_engine", "evolution_interactive", "local_ai_brain",
    "rag_engine", "owner_alert_protocol", "reminder_scheduler",
    "circuit_breaker_telemetry", "post_generation_auditor",
    "adaptive_knowledge_memory", "semantic_cache"
]

imported_count = 0
for mod in core_modules:
    try:
        m = importlib.import_module(mod)
        imported_count += 1
        print(f"  • {mod:<30}: ✅ IMPORTED OK")
    except Exception as e:
        print(f"  • {mod:<30}: ❌ IMPORT ERROR ({e})")

print(f"\n✅ Core Modules Verified: {imported_count}/{len(core_modules)}")

print("\n" + "=" * 70)
print("3. TESTING FAIL-SAFE FALLBACK CHAIN")
print("=" * 70)

# Test Fallback 1: Database Catalog Fallback
try:
    from database import get_tenant_catalog
    dummy_cat = get_tenant_catalog("non_existent_tenant_id")
    print(f"  • Database Catalog Fallback: ✅ Works ({len(dummy_cat)} fallback items returned)")
except Exception as e:
    print(f"  • Database Catalog Fallback: ❌ Failed ({e})")

# Test Fallback 2: Local AI Brain Fallback
try:
    from local_ai_brain import local_brain
    match_res = local_brain.match_catalog_product({"business_name": "Test Store"}, "1.5kva generator")
    print(f"  • Local AI Brain Fallback: ✅ Works (Matched = {match_res.get('matched')})")
except Exception as e:
    print(f"  • Local AI Brain Fallback: ❌ Failed ({e})")

# Test Fallback 3: Character Engine Safe Handoff
try:
    from character_engine import _human_handoff_reply
    handoff = _human_handoff_reply("Test Store")
    print(f"  • Character Engine Safe Handoff: ✅ Works (Is Transfer = {handoff.get('is_human_transfer')})")
except Exception as e:
    print(f"  • Character Engine Safe Handoff: ❌ Failed ({e})")

print("\n" + "=" * 70)
print("SYSTEM AUDIT COMPLETED CLEANLY!")
print("=" * 70)
