import time
from pyngrok import ngrok

def start_247_ngrok_tunnel():
    print("[24/7 NGROK DAEMON]: Initializing 24/7 NGROK production tunnel...", flush=True)
    try:
        tunnels = ngrok.get_tunnels()
        if tunnels:
            for t in tunnels:
                print(f"[EXISTING NGROK TUNNEL]: {t.public_url}", flush=True)
                if "ngrok-free.dev" in t.public_url:
                    return t.public_url

        tunnel = ngrok.connect(8000)
        print(f"[24/7 NGROK ESTABLISHED]: {tunnel.public_url}", flush=True)
        return tunnel.public_url
    except Exception as e:
        print(f"[NGROK ERROR]: {e}", flush=True)
        return None

if __name__ == "__main__":
    url = start_247_ngrok_tunnel()
    print(f"ACTIVE 24/7 NGROK URL: {url}", flush=True)
    while True:
        time.sleep(3600)
