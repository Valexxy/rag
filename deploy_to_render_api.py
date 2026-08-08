"""
====================================================================
100% AUTOMATED RENDER CLOUD DEPLOYMENT SCRIPT (Node.js High-Performance Engine)
====================================================================
Configures Render Web Service 'rag' with Node.js Fastify/Express engine:
- Build Command: npm install
- Start Command: node server.js
- Live URL: https://rag-403h.onrender.com
- Webhook Target: https://rag-403h.onrender.com/webhook/whatsapp/store-bot
"""

import sys, os, requests, json
sys.stdout.reconfigure(encoding='utf-8')

RENDER_API_KEY = "rnd_wCr8IGCSsS4sS7ZwIqbHUOCcPWge"
SERVICE_ID = "srv-d9oh8h1t0dsc73b1r0r0"  # Existing service 'rag'
HEADERS = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

print("=" * 70)
print("1. UPDATING RENDER WEB SERVICE CONFIGURATION TO NODE.JS HIGH-PERFORMANCE ENGINE")
print("=" * 70)

# Patch service details for Node.js engine
patch_payload = {
    "serviceDetails": {
        "env": "node",
        "buildCommand": "npm install",
        "startCommand": "node server.js"
    }
}

try:
    r_patch = requests.patch(f"https://api.render.com/v1/services/{SERVICE_ID}", json=patch_payload, headers=HEADERS, timeout=15)
    print(f"Service Patch Status: {r_patch.status_code}")
except Exception as e:
    print(f"Service patch warning: {e}")

print("\n--- TRIGGERING FRESH RENDER DEPLOYMENT ---")
r_deploy = requests.post(f"https://api.render.com/v1/services/{SERVICE_ID}/deploys", json={"clearCache": "clear"}, headers=HEADERS, timeout=15)
print(f"Deploy Trigger Info: {r_deploy.status_code}")

print("\n" + "=" * 70)
print("2. REGISTERING 24/7 CLOUD WEBHOOK ON EVOLUTION API")
print("=" * 70)

EVO_URL = "https://evolution-api-latest-gxue.onrender.com"
EVO_KEY = "F84B4F845BC6-464A-AD0E-553FD1046981"
PUBLIC_WEBHOOK = "https://rag-403h.onrender.com/webhook/whatsapp/store-bot"

try:
    w_res = requests.post(
        f"{EVO_URL}/webhook/set/store-bot",
        headers={"apikey": EVO_KEY, "Content-Type": "application/json"},
        json={"webhook": {"enabled": True, "url": PUBLIC_WEBHOOK, "events": ["MESSAGES_UPSERT"]}},
        timeout=10
    )
    print(f"Webhook Registration Status: {w_res.status_code}")
    print(f"Webhook Payload: {w_res.json()}")
except Exception as e:
    print(f"Webhook registration warning: {e}")

print("\n" + "=" * 70)
print("🎉 NODE.JS HIGH-PERFORMANCE CLOUD DEPLOYMENT TRIGGERED!")
print("  Live Service: https://rag-403h.onrender.com")
print("  Live Webhook: https://rag-403h.onrender.com/webhook/whatsapp/store-bot")
print("=" * 70)
