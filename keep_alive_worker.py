import time
import requests
import threading

def run_keep_alive_loop():
    print("[24/7 KEEP-ALIVE WORKER ACTIVE]: Preventing system sleep across all nodes...")
    
    EVO_URL = "https://evolution-api-latest-gxue.onrender.com"
    EVO_KEY = "F84B4F845BC6-464A-AD0E-553FD1046981"
    PUBLIC_WEBHOOK = "https://verlene-retrouss-eldora.ngrok-free.dev/webhook/whatsapp/store-bot"
    PUBLIC_BASE = "https://verlene-retrouss-eldora.ngrok-free.dev"
    
    counter = 0
    while True:
        try:
            # 1. Ping Local Server
            requests.get("http://127.0.0.1:8000/", timeout=5)
        except Exception:
            pass

        try:
            # 2. Ping Active NGROK Tunnel
            requests.get(PUBLIC_BASE, headers={"ngrok-skip-browser-warning": "true"}, timeout=5)
        except Exception:
            pass

        # Every 60 seconds: Ping Evolution API on Render to keep it awake!
        if counter % 2 == 0:
            try:
                requests.get(f"{EVO_URL}/instance/fetchInstances", headers={"apikey": EVO_KEY}, timeout=10)
            except Exception:
                pass

        # Every 3 minutes: Enforce Active Webhook URL
        if counter % 6 == 0:
            try:
                w_res = requests.get(f"{EVO_URL}/webhook/find/store-bot", headers={"apikey": EVO_KEY}, timeout=8)
                if w_res.status_code == 200:
                    current_url = w_res.json().get("url", "")
                    if current_url != PUBLIC_WEBHOOK:
                        print(f"[KEEP-ALIVE ENFORCER]: Updating webhook from {current_url} to {PUBLIC_WEBHOOK}")
                        requests.post(
                            f"{EVO_URL}/webhook/set/store-bot",
                            headers={"apikey": EVO_KEY, "Content-Type": "application/json"},
                            json={"webhook": {"enabled": True, "url": PUBLIC_WEBHOOK, "events": ["MESSAGES_UPSERT"]}},
                            timeout=8
                        )
            except Exception as e:
                print(f"[KEEP-ALIVE WARNING]: Webhook check exception: {e}")

        counter += 1
        time.sleep(30)

def start_keep_alive_background_thread():
    t = threading.Thread(target=run_keep_alive_loop, daemon=True)
    t.start()
    print("[KEEP-ALIVE THREAD STARTED]: 24/7 anti-sleep worker background thread initialized.")

if __name__ == "__main__":
    run_keep_alive_loop()
