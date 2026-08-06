import os
import base64
import requests

DEFAULT_MONNIFY_BASE_URL = os.getenv("MONNIFY_BASE_URL", "https://sandbox.monnify.com")

def get_tenant_monnify_token(tenant: dict) -> str:
    """Authenticates with Monnify using tenant credentials."""
    api_key = tenant.get("monnify_api_key") or os.getenv("MONNIFY_API_KEY")
    secret_key = tenant.get("monnify_secret_key") or os.getenv("MONNIFY_SECRET_KEY")
    
    url = f"{DEFAULT_MONNIFY_BASE_URL}/api/v1/auth/login"
    credentials = f"{api_key}:{secret_key}"
    encoded = base64.b64encode(credentials.encode()).decode()
    
    headers = {"Authorization": f"Basic {encoded}"}
    response = requests.post(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()["responseBody"]["accessToken"]
    return None

def create_tenant_payment_link(tenant: dict, amount: float, customer_phone: str, payment_ref: str, description: str = "Payment") -> str:
    """Generates a dynamic payment checkout link for a tenant."""
    token = get_tenant_monnify_token(tenant)
    if not token:
        return None

    contract_code = tenant.get("monnify_contract_code") or os.getenv("MONNIFY_CONTRACT_CODE")
    url = f"{DEFAULT_MONNIFY_BASE_URL}/api/v1/merchant/transactions/init-transaction"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    clean_phone = customer_phone.replace("@s.whatsapp.net", "")
    customer_email = f"{clean_phone}@customer.com"

    payload = {
        "amount": amount,
        "customerName": f"Customer {clean_phone[-4:]}",
        "customerEmail": customer_email,
        "paymentReference": payment_ref,
        "paymentDescription": description,
        "currencyCode": tenant.get("currency", "NGN"),
        "contractCode": contract_code,
        "paymentMethods": ["CARD", "ACCOUNT_TRANSFER"]
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    
    if data.get("requestSuccessful"):
        return data["responseBody"]["checkoutUrl"]
    return None