import sys, os, requests, json
sys.stdout.reconfigure(encoding='utf-8')

url_base = os.environ.get("EVOLUTION_API_URL", "https://evolution-api-latest-gxue.onrender.com").rstrip("/")
key = os.environ.get("EVOLUTION_API_KEY", "F84B4F845BC6-464A-AD0E-553FD1046981")
headers = {"apikey": key, "Content-Type": "application/json"}
url = f"{url_base}/message/sendText/store-bot"

payload = {
    "number": "2348072015725",
    "text": "🤖 [Sovereign AI Direct Live Test System Check]"
}

print(f"Posting directly to Evolution API: {url}")
try:
    res = requests.post(url, json=payload, headers=headers, timeout=15)
    print(f"Status Code: {res.status_code}")
    print(f"Response Payload:\n{json.dumps(res.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
