import os
import base64
import requests

MONNIFY_BASE_URL = os.getenv("MONNIFY_BASE_URL", "https://sandbox.monnify.com")
MONNIFY_API_KEY = os.getenv("MONNIFY_API_KEY")
MONNIFY_SECRET_KEY = os.getenv("MONNIFY_SECRET_KEY")
MONNIFY_CONTRACT_CODE = os.getenv("MONNIFY_CONTRACT_CODE")

def get_monnify_token():
    """Generates an OAuth2 access token using Monnify API & Secret keys."""
    url = f"{MONNIFY_BASE_URL}/api/v1/auth/login"
    
    # Basic Auth string (apiKey:secretKey encoded in Base64)
    credentials = f"{MONNIFY_API_KEY}:{MONNIFY_SECRET_KEY}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }
    
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.json()["responseBody"]["accessToken"]
    else:
        print("Monnify Auth Failed:", response.text)
        return None

def initialize_payment(amount: float, customer_name: str, customer_phone: str, payment_ref: str):
    """Initializes a transaction and returns a Monnify checkout link."""
    token = get_monnify_token()
    if not token:
        return None

    url = f"{MONNIFY_BASE_URL}/api/v1/merchant/transactions/init-transaction"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Standard dummy email format for phone numbers if missing
    clean_phone = customer_phone.replace("@s.whatsapp.net", "")
    customer_email = f"{clean_phone}@customer.com"

    payload = {
        "amount": amount,
        "customerName": customer_name,
        "customerEmail": customer_email,
        "paymentReference": payment_ref,
        "paymentDescription": "WhatsApp Order Payment",
        "currencyCode": "NGN",
        "contractCode": MONNIFY_CONTRACT_CODE,
        "paymentMethods": ["CARD", "ACCOUNT_TRANSFER"]
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    
    if data.get("requestSuccessful"):
        return data["responseBody"]["checkoutUrl"]
    else:
        print("Payment Init Failed:", data)
        return None