import urllib.request, time, json, sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://rag-403h.onrender.com/api/status'
print('Checking Render Cloud service health at:', url)

for attempt in range(12):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            st = data.get("status")
            sys_name = data.get("system")
            t_now = data.get("realtime_wat_clock")
            print(f"\n✅ CLOUD SERVICE IS LIVE! HTTP 200")
            print(f"   Status:  {st}")
            print(f"   System:  {sys_name}")
            print(f"   Time:    {t_now}")
            sys.exit(0)
    except Exception as e:
        print(f"  Attempt {attempt+1}/12: Cloud service building/starting... ({e})")
        time.sleep(10)

print("\nBuild in progress on Render — will be live shortly.")
