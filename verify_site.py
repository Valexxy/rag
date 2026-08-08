import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

r = requests.get('http://127.0.0.1:8000/')
print("Status Code:", r.status_code)
print("Payload Size:", len(r.text))

# Verify all 14 navbar tabs & page IDs are present with full rich content
tabs = ['home', 'dir', 'analytics', 'prices', 'ai', 'trust', 'news', 'forex', 'customs', 'map', 'wa', 'qr', 'about', 'contact']
for t in tabs:
    present = f'id="pg-{t}"' in r.text
    print(f"Page 'pg-{t}' present:", present)

print("\nWA Bot Page full card present:", 'Teeslux Solar & Tech Bot' in r.text)
print("Spot Prices table present:", '24 Active Commodities Across Regional Hubs' in r.text)
print("Customs calculator present:", 'Landed Cost Calculator' in r.text)
print("QR generator present:", 'DYNAMIC QR GENERATOR' in r.text)
