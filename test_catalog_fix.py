import sys, ast
sys.stdout.reconfigure(encoding='utf-8')

# 1. Syntax check both files
for fname in ['main.py', 'local_ai_brain.py']:
    with open(fname, 'r', encoding='utf-8') as f:
        src = f.read()
    try:
        ast.parse(src)
        print(f'✅ {fname} — syntax clean')
    except SyntaxError as e:
        print(f'❌ {fname} syntax error at line {e.lineno}: {e.msg}')

# 2. Simulate exact messages against the catalog matcher
print()
print('--- CATALOG MATCH SIMULATION (min score = 10) ---')
from local_ai_brain import LocalAIBrain
brain = LocalAIBrain()

fake_tenant = {
    'id': 'test',
    'business_name': 'Teeslux Store',
    'catalog': [
        {'name': '550W Monocrystalline Solar Panel', 'price': 120000, 'description': 'High Efficiency 21.5% Grade-A Monocrystalline Solar Panel for Inverter System', 'status': 'In Stock'},
        {'name': '20,000 mAh Solar Power Bank', 'price': 18500, 'description': 'Dual USB fast charge solar bank with LED torch light', 'status': 'In Stock'},
        {'name': '1.5kVA Dual Solar Generator', 'price': 185000, 'description': 'Silent Petrol-Solar Hybrid Generator', 'status': 'In Stock'},
        {'name': '50kg Premium White Rice Bag', 'price': 60000, 'description': 'Grade A long grain parboiled rice', 'status': 'In Stock'},
        {'name': '24K Gold Bar Bullion (1-Gram)', 'price': 68500, 'description': 'LBMA certified 999.9 purity gold', 'status': 'In Stock'},
    ]
}

# (message, should_catalog_match)
test_cases = [
    ('i need human help for further enquiries', False),  # Was the bug — must NOT match catalog
    ('do you sell power bank, how many types do you have', True),
    ('do you have solar panels', True),
    ('Good morning do you have solar panels', True),
    ('i want to buy rice', True),
    ('do you have gold', True),
    ('generator for sale', True),
    ('good morning', False),  # Pure greeting — must NOT match catalog
    ('where is the store', False),  # No product keywords
    ('what is your return policy', False),  # No product keywords
    ('i need a human agent please', False),  # Human request — must NOT match catalog
    ('connect me to manager', False),  # Human request — must NOT match catalog
]

passed = 0
failed = 0
for msg, should_match in test_cases:
    result = brain.match_catalog_product(fake_tenant, msg)
    matched = result.get('matched', False)
    item_name = ''
    if matched and 'reply' in result:
        import re
        m = re.search(r'\*Item:\* (.+)', result['reply'])
        item_name = m.group(1) if m else ''
    
    ok = matched == should_match
    icon = '✅' if ok else '❌'
    status_word = 'MATCHED' if matched else 'NO MATCH'
    expected_word = 'MATCH' if should_match else 'NO MATCH'
    detail = f'→ {item_name}' if matched else ''
    print(f'{icon} [{status_word}|expected {expected_word}] "{msg[:50]}" {detail}')
    if ok:
        passed += 1
    else:
        failed += 1

print()
print(f'--- RESULT: {passed} PASSED | {failed} FAILED ---')
