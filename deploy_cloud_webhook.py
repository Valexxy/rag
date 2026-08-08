"""
====================================================================
AUTOMATED CLOUD WEBHOOK REGISTRATION SCRIPT
====================================================================
Updates Evolution API on Render to point incoming WhatsApp messages to your
cloud backend server URL so the system operates 24/7 with zero local processes!
"""

import sys, os, requests
sys.stdout.reconfigure(encoding='utf-8')

EVO_URL = os.environ.get("EVOLUTION_API_URL", "https://evolution-api-latest-gxue.onrender.com")
EVO_KEY = os.environ.get("EVOLUTION_API_KEY", "F84B4F845BC6-464A-AD0E-553FD1046981")
INSTANCE_NAME = "store-bot"

def register_cloud_webhook(target_backend_url: str):
    """
    Registers the cloud backend URL as the official 24/7 webhook endpoint.
    Example: target_backend_url = "https://sovereign-ai-backend.onrender.com"
    """
    clean_url = target_backend_url.rstrip("/")
    webhook_target = f"{clean_url}/webhook/whatsapp/{INSTANCE_NAME}"

    print("=" * 65)
    print("REGISTERING 24/7 CLOUD WEBHOOK TARGET")
    print("=" * 65)
    print(f"  Evolution API Server: {EVO_URL}")
    print(f"  Target Cloud Webhook: {webhook_target}")
    print("=" * 65)

    payload = {
        "webhook": {
            "enabled": True,
            "url": webhook_target,
            "events": ["MESSAGES_UPSERT"]
        }
    }

    try:
        resp = requests.post(
            f"{EVO_URL}/webhook/set/{INSTANCE_NAME}",
            headers={"apikey": EVO_KEY, "Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        print(f"\nResponse Code: {resp.status_code}")
        print("Response Payload:", resp.json())

        if resp.status_code in [200, 201]:
            print(f"\n✅ SUCCESS: 24/7 Cloud Webhook registered! Evolution API will now send all incoming WhatsApp messages to '{webhook_target}'.")
        else:
            print("\n❌ Webhook registration failed — check API key or instance status.")
    except Exception as e:
        print(f"\n❌ Error setting webhook: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cloud_url = sys.argv[1]
    else:
        cloud_url = input("Enter your public backend URL (e.g. https://sovereign-ai.onrender.com): ").strip()
    
    if cloud_url:
        register_cloud_webhook(cloud_url)
    else:
        print("No URL provided.")
