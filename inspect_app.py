import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/futuristic_app.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
print("NAVBAR BUTTONS:")
idx1 = text.find('<div class="nts">')
print(text[idx1:idx1+800])

print("\nPAGE IDS FOUND:")
pages = re.findall(r'id="pg-[^"]+"', text)
print(pages)

print("\nSWITCH TAB FUNCTION:")
idx2 = text.find('function switchTab')
print(text[idx2:idx2+800])
