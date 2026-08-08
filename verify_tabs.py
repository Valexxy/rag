with open('static/futuristic_app.html', 'r', encoding='utf-8') as f:
    text = f.read()

tabs = ['home', 'dir', 'analytics', 'prices', 'ai', 'signals', 'trust', 'loyalty', 'news', 'forex', 'customs', 'map', 'wa', 'qr', 'supply', 'features', 'pref', 'legal']

missing = []
for t in tabs:
    if f'id="pg-{t}"' not in text:
        missing.append(t)

if not missing:
    print("SUCCESS: All 18 tabs match their page containers perfectly!")
else:
    print("MISSING TABS:", missing)
