import urllib.request, time, json, sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://sovereign-ai-backend-production.up.railway.app/api/status'
print('Checking Railway Secondary Cloud node health at:', url)

for attempt in range(8):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            st = data.get("status")
            sys_name = data.get("system")
            t_now = data.get("realtime_wat_clock")
            print(f"\n✅ RAILWAY SECONDARY CLOUD NODE IS LIVE! HTTP 200")
            print(f"   Status:  {st}")
            print(f"   System:  {sys_name}")
            print(f"   Time:    {t_now}")
            sys.exit(0)
    except Exception as e:
        print(f"  Attempt {attempt+1}/8: Railway container building/deploying... ({e})")
        time.sleep(10)
