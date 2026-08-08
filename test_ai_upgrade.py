import ast, sys, os
sys.stdout.reconfigure(encoding='utf-8')
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

files = ['main.py','sovereign_ai_brain.py','semantic_catalog_engine.py','rag_engine.py','character_engine.py','local_ai_brain.py']
all_ok = True
for f in files:
    with open(f, 'r', encoding='utf-8') as fh:
        src = fh.read()
    try:
        ast.parse(src)
        print(f'  ✅  {f}')
    except SyntaxError as e:
        print(f'  ❌  {f} line {e.lineno}: {e.msg}')
        all_ok = False

print()
print('All syntax OK' if all_ok else 'SYNTAX ERRORS FOUND')

# Live semantic search test
print()
print('='*60)
print('LIVE SEMANTIC SEARCH TEST (sentence-transformers)')
print('='*60)

from semantic_catalog_engine import SemanticCatalogEngine
sc = SemanticCatalogEngine()
print(f'Embedder ready: {sc._embedder_ready}')
print(f'Method: {"semantic (all-MiniLM-L6-v2)" if sc._embedder_ready else "TF-IDF fallback"}')
print()

catalog = [
    {'name': '550W Monocrystalline Solar Panel', 'price': 120000, 'description': 'High Efficiency 21.5% Grade-A Monocrystalline Solar Panel for Inverter System'},
    {'name': '20,000 mAh Solar Power Bank', 'price': 18500, 'description': 'Dual USB fast charge solar bank with LED torch light'},
    {'name': '1.5kVA Dual Solar Generator', 'price': 185000, 'description': 'Silent Petrol-Solar Hybrid Generator'},
    {'name': '50kg Premium White Rice Bag', 'price': 60000, 'description': 'Grade A long grain parboiled rice'},
    {'name': '24K Gold Bar Bullion (1-Gram)', 'price': 68500, 'description': 'LBMA certified 999.9 purity gold bar'},
]

tests = [
    ('i need human help for further enquiries',           False, None),
    ('do you have solar panels',                          True,  '550W Monocrystalline Solar Panel'),
    ('good morning do you have solar panels',             True,  '550W Monocrystalline Solar Panel'),
    ('how much is the power bank',                        True,  '20,000 mAh Solar Power Bank'),
    ('do you sell generators or inverters',               True,  '1.5kVA Dual Solar Generator'),
    ('do you have rice',                                  True,  '50kg Premium White Rice Bag'),
    ('what is the price of gold',                         True,  '24K Gold Bar Bullion (1-Gram)'),
    ('i want to connect to a manager',                    False, None),
    ('where is your store',                               False, None),
    ('something to charge my phone with no light',        True,  '20,000 mAh Solar Power Bank'),
    ('panels for my solar inverter system',               True,  '550W Monocrystalline Solar Panel'),
    ('i need further enquiries',                          False, None),
    ('connect me to the store owner',                     False, None),
]

passed = failed = 0
for msg, should_match, expected_name in tests:
    result = sc.search(msg, catalog)
    matched = result['matched']
    got_name = result.get('item', {}).get('name', '') if matched else ''
    score = result['score']

    ok = (matched == should_match)
    # Also verify the correct item was returned when a match is expected
    if should_match and matched and expected_name:
        if expected_name.lower() not in got_name.lower():
            ok = False  # Wrong item returned

    icon = 'PASS' if ok else 'FAIL'
    if ok: passed += 1
    else: failed += 1

    detail = f'-> {got_name[:35]} ({score:.3f})' if matched else f'(no match, score={score:.3f})'
    expected = f'expect: {expected_name}' if should_match else 'expect: no match'
    print(f'  [{icon}] {msg[:45]:<46} {detail} [{expected}]')

print()
print(f'RESULT: {passed}/{passed+failed} PASSED | {failed} FAILED')
