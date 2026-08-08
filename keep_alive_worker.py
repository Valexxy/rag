"""
====================================================================
24/7 ZERO-SLEEP CLOUD HEARTBEAT WORKER
====================================================================
Keeps both Render cloud web services (Python AI backend + Evolution API)
100% active, hot, and awake 24/7/365 to eliminate cold-start delays.
"""

import time
import requests
import threading

def run_keep_alive_loop():
    print("[24/7 ZERO-SLEEP CLOUD WORKER ACTIVE]: Preventing container sleep across all nodes...")
    
    EVO_URL = "https://evolution-api-latest-gxue.onrender.com"
    EVO_KEY = "F84B4F845BC6-464A-AD0E-553FD1046981"
    BACKEND_URL = "https://rag-403h.onrender.com"
    PUBLIC_WEBHOOK = "https://rag-403h.onrender.com/webhook/whatsapp/store-bot"
    
    counter = 0
    while True:
        try:
            # 1. Ping Python Backend Health Endpoint (keeps backend awake)
            requests.get(f"{BACKEND_URL}/api/status", headers={"User-Agent": "ZeroSleepHeartbeat/2.0"}, timeout=5)
        except Exception:
            pass

        try:
            # 2. Ping Evolution API Instance List (keeps Evolution API awake)
            requests.get(f"{EVO_URL}/instance/fetchInstances", headers={"apikey": EVO_KEY}, timeout=10)
        except Exception:
            pass

        # Every 3 minutes: Verify & enforce production webhook URL
        if counter % 3 == 0:
            try:
                w_res = requests.get(f"{EVO_URL}/webhook/find/store-bot", headers={"apikey": EVO_KEY}, timeout=8)
                if w_res.status_code == 200:
                    current_url = w_res.json().get("url", "")
                    if current_url != PUBLIC_WEBHOOK:
                        print(f"[KEEP-ALIVE ENFORCER]: Updating webhook target to {PUBLIC_WEBHOOK}")
                        requests.post(
                            f"{EVO_URL}/webhook/set/store-bot",
                            headers={"apikey": EVO_KEY, "Content-Type": "application/json"},
                            json={"webhook": {"enabled": True, "url": PUBLIC_WEBHOOK, "events": ["MESSAGES_UPSERT"]}},
                            timeout=8
                        )
            except Exception as e:
                pass

        counter += 1
        time.sleep(60)  # Ping every 60 seconds

def start_keep_alive_background_thread():
    t = threading.Thread(target=run_keep_alive_loop, daemon=True)
    t.start()
    print("[KEEP-ALIVE THREAD STARTED]: 24/7 anti-sleep cloud worker thread initialized.")

if __name__ == "__main__":
    run_keep_alive_loop()
