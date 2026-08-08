"""
╔══════════════════════════════════════════════════════════════════╗
║   SAAS ROBUSTNESS STRESS TEST — ALL EDGE CASE SCENARIOS         ║
║   Tests: Multi-tenant | Edge cases | All intents | Languages    ║
╚══════════════════════════════════════════════════════════════════╝
"""
import sys, os, time
sys.stdout.reconfigure(encoding='utf-8')
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'

from dotenv import load_dotenv
load_dotenv()

# ── 1. API KEY VERIFICATION ──────────────────────────────────────
print('='*65)
print('STEP 1: API KEY VERIFICATION')
print('='*65)

groq_key = os.environ.get('GROQ_API_KEY','')
gemini_key = os.environ.get('GEMINI_API_KEY','')
hf_token = os.environ.get('HF_TOKEN','')

groq_status = 'MISSING'
gemini_status = 'MISSING'

if groq_key and groq_key != 'please_add_your_groq_key_here':
    try:
        from groq import Groq
        client = Groq(api_key=groq_key)
        resp = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[{'role':'user','content':'Reply with just the word: ACTIVE'}],
            max_tokens=5, temperature=0
        )
        result = resp.choices[0].message.content.strip()
        groq_status = f'ACTIVE - Llama 3.3 70B responded: "{result}"'
    except Exception as e:
        groq_status = f'ERROR: {str(e)[:80]}'
else:
    groq_status = 'KEY MISSING OR PLACEHOLDER'

print(f'  Groq:   {groq_status}')
print(f'  Gemini: {"FOUND" if gemini_key else "MISSING"}')
print(f'  HF:     {"FOUND" if hf_token else "MISSING"}')

# ── 2. SOVEREIGN BRAIN LIVE INTENT CLASSIFICATION ───────────────
print()
print('='*65)
print('STEP 2: GROQ LLAMA 3.3 70B — LIVE INTENT CLASSIFICATION')
print('='*65)

from sovereign_ai_brain import sovereign_brain
print(f'  Groq available:   {sovereign_brain._model_status["groq_available"]}')
print(f'  Gemini available: {sovereign_brain._model_status["gemini_available"]}')
print(f'  Operational:      {sovereign_brain.is_operational}')
print()

# Multi-tenant fake catalog for testing
catalog_retail = [
    {'name': '550W Monocrystalline Solar Panel', 'price': 120000, 'description': 'Grade-A panel for inverter system'},
    {'name': '20,000 mAh Solar Power Bank', 'price': 18500, 'description': 'Dual USB fast charge solar bank'},
    {'name': '1.5kVA Dual Solar Generator', 'price': 185000, 'description': 'Silent hybrid generator'},
    {'name': '50kg Premium White Rice Bag', 'price': 60000, 'description': 'Long grain parboiled rice'},
    {'name': '24K Gold Bar Bullion (1-Gram)', 'price': 68500, 'description': 'LBMA certified 999.9 purity gold'},
]

catalog_real_estate = [
    {'name': '3-Bedroom Flat Awka', 'price': 25000000, 'description': 'Fully tiled 3BR flat in GRA Awka'},
    {'name': '5-Bedroom Duplex Onitsha', 'price': 85000000, 'description': 'Luxury duplex with BQ in GRA Onitsha'},
]

catalog_salon = [
    {'name': 'Hair Fixing (Closure)', 'price': 15000, 'description': 'Brazilian closure hair installation'},
    {'name': 'Pedicure & Manicure', 'price': 5000, 'description': 'Full nail treatment service'},
]

# Comprehensive test cases: (message, expected_intent, description)
intent_tests = [
    # ── Normal customer queries ──
    ('Hi',                                   'GREETING',       'Single word greeting'),
    ('Hello',                                'GREETING',       'Hello greeting'),
    ('Good morning',                         'GREETING',       'Morning greeting'),
    ('Hey',                                  'GREETING',       'Casual greeting'),
    ('1',                                    'MENU_OPTION',    'Menu option 1'),
    ('2',                                    'MENU_OPTION',    'Menu option 2'),
    ('5',                                    'MENU_OPTION',    'Menu option 5'),
    ('#trust',                               'COMMAND',        'Hash command'),
    ('#buy',                                 'COMMAND',        'Buy command'),

    # ── Product queries ──
    ('do you have solar panels',             'CATALOG_QUERY',  'Direct product query'),
    ('Good morning do you have solar panels','CATALOG_QUERY',  'Greeting + product query'),
    ('how much is your generator',           'CATALOG_QUERY',  'Price inquiry'),
    ('what types of power bank do you have', 'CATALOG_QUERY',  'Product type inquiry'),
    ('I need rice bags please',              'CATALOG_QUERY',  'Product request'),
    ('show me your gold',                    'CATALOG_QUERY',  'Show product'),

    # ── Human escalation — various phrasings ──
    ('i need human help for further enquiries', 'HUMAN_REQUEST', 'Human help - original bug'),
    ('please connect me to a manager',       'HUMAN_REQUEST',  'Connect to manager'),
    ('I want to speak with someone',         'HUMAN_REQUEST',  'Speak with someone'),
    ('can i talk to the owner',              'HUMAN_REQUEST',  'Talk to owner'),
    ('this is urgent i need help now',       'HUMAN_REQUEST',  'Urgent human needed'),

    # ── Purchase intent ──
    ('i want to buy the solar panel',        'PURCHASE',       'Buy intent explicit'),
    ('how do i pay',                         'PURCHASE',       'Payment inquiry'),
    ('i want to order 2 bags of rice',       'PURCHASE',       'Order request'),

    # ── General questions ──
    ('where is your store',                  'GENERAL',        'Location question'),
    ('what are your business hours',         'GENERAL',        'Hours question'),
    ('do you do home delivery',              'GENERAL',        'Delivery question'),
    ('what is your return policy',           'GENERAL',        'Policy question'),

    # ── Edge cases ──
    ('hmm',                                  None,             'Very short ambiguous'),
    ('ok',                                   None,             'One word'),
    ('SOLAR PANEL PRICE????',               'CATALOG_QUERY',  'All caps + punctuation'),
    ('abcdefg gibberish nonsense xyz123',    None,             'Gibberish'),
    ('pls i wan buy generator how much e go cost', 'CATALOG_QUERY', 'Nigerian Pidgin English'),
    ('I dey find rice wey e no too expensive',     'CATALOG_QUERY', 'Pidgin - rice query'),
    ('oga i wan see your oga for matter wey concern my money', 'HUMAN_REQUEST', 'Pidgin - speak to manager'),
]

print(f'Running {len(intent_tests)} intent classification tests against Groq Llama 3.3 70B...')
print()

passed = failed = skipped = 0
results = []

for i, (msg, expected_intent, desc) in enumerate(intent_tests):
    try:
        t_start = time.time()
        result = sovereign_brain.classify_intent(
            message=msg,
            catalog=catalog_retail,
            conversation_history=''
        )
        t_ms = (time.time() - t_start) * 1000
        got = result['intent']
        source = result.get('source', '?')
        confidence = result.get('confidence', 0)

        if expected_intent is None:
            # No strict expectation — just verify it doesn't crash
            icon = 'SKIP'
            skipped += 1
        elif got == expected_intent:
            icon = 'PASS'
            passed += 1
        else:
            icon = 'FAIL'
            failed += 1

        results.append((icon, msg, got, expected_intent, t_ms, source, confidence, desc))
    except Exception as e:
        results.append(('ERR', msg, 'EXCEPTION', expected_intent, 0, 'error', 0, str(e)[:60]))
        failed += 1

# Print results
for icon, msg, got, exp, t_ms, source, conf, desc in results:
    prefix = f'  [{icon}]'
    msg_col = f'"{msg[:38]}"'
    if icon == 'PASS':
        print(f'{prefix} {msg_col:<42} → {got:<16} ({t_ms:.0f}ms, {source})')
    elif icon == 'FAIL':
        print(f'{prefix} {msg_col:<42} → GOT:{got:<14} EXPECTED:{exp:<14} ({t_ms:.0f}ms)')
    elif icon == 'SKIP':
        print(f'{prefix} {msg_col:<42} → {got:<16} [no strict expectation] ({t_ms:.0f}ms)')
    else:
        print(f'{prefix} {msg_col:<42} → ERROR: {got}')

print()
print('='*65)
print(f'INTENT TEST RESULT: {passed} PASSED | {failed} FAILED | {skipped} FLEXIBLE')
print('='*65)

# ── 3. MULTI-TENANT CONTEXT TEST ────────────────────────────────
print()
print('='*65)
print('STEP 3: MULTI-TENANT CONTEXT TEST')
print('='*65)

tenants = [
    ('Teeslux Electronics Store', 'retail', catalog_retail),
    ('GRA Properties Ltd', 'real_estate', catalog_real_estate),
    ('Queens Beauty Salon', 'salon', catalog_salon),
    ('Empty Store (no catalog)', 'retail', []),
]

for biz_name, niche, cat in tenants:
    result = sovereign_brain.classify_intent(
        message='do you have what i need for my home',
        catalog=cat,
        conversation_history=''
    )
    print(f'  Tenant: {biz_name:<35} | Intent: {result["intent"]:<16} | Conf: {result["confidence"]:.2f}')

# ── 4. SEMANTIC SEARCH ROBUSTNESS ───────────────────────────────
print()
print('='*65)
print('STEP 4: SEMANTIC SEARCH — FULL ACCURACY TEST')
print('='*65)

from semantic_catalog_engine import SemanticCatalogEngine
sc = SemanticCatalogEngine()
print(f'  Embedder: {"sentence-transformers all-MiniLM-L6-v2" if sc._embedder_ready else "TF-IDF fallback"}')
print()

search_tests = [
    # (query, product_query_from_ai, expected_item_fragment, should_match)
    ('do you have solar panels',                  'solar panel',     '550W',         True),
    ('good morning do you have solar panels',     'solar panel',     '550W',         True),
    ('how much is the power bank',                'power bank',      'Power Bank',   True),
    ('do you sell generators or inverters',       'generator',       'Generator',    True),
    ('something to charge my phone with no light','power bank',      'Power Bank',   True),
    ('panels for my solar inverter system',       'solar panel',     '550W',         True),
    ('pls i wan buy generator how much e go cost','generator',       'Generator',    True),
    ('i need rice bags please',                   'rice',            'Rice',         True),
    ('current price of gold bullion',             'gold',            'Gold',         True),
    ('i need human help for further enquiries',   None,              None,           False),
    ('connect me to manager',                     None,              None,           False),
    ('where is the store',                        None,              None,           False),
    ('good morning',                              None,              None,           False),
    ('what is your return policy',                None,              None,           False),
    ('oga i want to speak to the oga',            None,              None,           False),
]

s_passed = s_failed = 0
for full_msg, ai_product_q, expected_frag, should_match in search_tests:
    result = sc.search_with_intent(ai_product_q, full_msg, catalog_retail)
    matched = result['matched']
    got_name = result.get('item', {}).get('name', '') if matched else ''
    score = result['score']

    if matched == should_match:
        if should_match and expected_frag and expected_frag.lower() not in got_name.lower():
            icon = 'FAIL (wrong item)'
            s_failed += 1
        else:
            icon = 'PASS'
            s_passed += 1
    else:
        icon = 'FAIL'
        s_failed += 1

    detail = f'→ {got_name[:35]} ({score:.3f})' if matched else f'NO MATCH ({score:.3f})'
    print(f'  [{icon[:4]}] "{full_msg[:42]:<44}" {detail}')

print()
print('='*65)
print(f'SEMANTIC TEST RESULT: {s_passed} PASSED | {s_failed} FAILED')
print('='*65)

print()
print('='*65)
print(f'OVERALL: Intent {passed}/{passed+failed} | Semantic {s_passed}/{s_passed+s_failed}')
if failed == 0 and s_failed == 0:
    print('ALL SYSTEMS GO — SOVEREIGN AI IS PRODUCTION READY')
else:
    print(f'ISSUES FOUND: {failed + s_failed} need attention')
print('='*65)
