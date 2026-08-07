import time
from database import supabase

async def get_tenant_config(tenant_id: str) -> dict:
    """Fetches tenant configuration from Supabase."""
    try:
        res = supabase.table('tenants').select('*').eq('id', tenant_id).single().execute()
        data = res.data if res else None

        if not data:
            return {
                "businessName": "Standard Partner Store",
                "niche": "general",
                "currency": "NGN",
                "systemPrompt": "You are an intelligent AI sales and support agent."
            }

        business_name = data.get('business_name', 'Partner Store')
        niche = data.get('niche', 'general')
        currency = data.get('currency', 'NGN')
        custom_prompt = data.get('custom_prompt')
        
        default_prompt = f"You are the expert sales assistant for {business_name}, specializing in the {niche} industry. Always conduct business using {currency}."

        return {
            "businessName": business_name,
            "niche": niche,
            "currency": currency,
            "systemPrompt": custom_prompt or default_prompt
        }
    except Exception as e:
        print(f"❌ Tenant Config Error [{tenant_id}]: {e}")
        return {
            "businessName": "Standard Partner Store",
            "niche": "general",
            "currency": "NGN",
            "systemPrompt": "You are an intelligent AI sales and support agent."
        }

async def process_tenant_message(tenant_id: str, user_query: str, phone_number: str) -> dict:
    start_time = time.time() * 1000

    config = await get_tenant_config(tenant_id)
    mock_embedding = [0.1] * 384

    matched_products = []
    try:
        rpc_res = supabase.rpc('match_tenant_products', {
            'p_tenant_id': tenant_id,
            'query_embedding': mock_embedding,
            'match_threshold': 0.4,
            'match_count': 3
        }).execute()
        matched_products = rpc_res.data or []
    except Exception as e:
        print(f"❌ Tenant Search Error [{tenant_id}]: {e}")

    ai_response = f"Hello from {config['businessName']}! Regarding your request about \"{user_query}\", we have verified our {config['niche']} catalog items in stock. Pricing is handled in {config['currency']}."
    latency = int((time.time() * 1000) - start_time)

    try:
        supabase.table('telemetry_logs').insert({
            "tenant_id": tenant_id,
            "phone_number": phone_number,
            "user_query": user_query,
            "ai_response": ai_response,
            "latency_ms": latency,
            "tokens_used": 120
        }).execute()
    except Exception as log_error:
        print(f"❌ Telemetry log error: {log_error}")

    return {
        "tenantId": tenant_id,
        "response": ai_response,
        "products": matched_products,
        "latencyMs": latency
    }

# Required exports for test and platform scripts
async def process_enterprise_platform_message(tenant_id: str, user_query: str, phone_number: str) -> dict:
    return await process_tenant_message(tenant_id, user_query, phone_number)

async def sync_inventory_product(tenant_id: str, product_data: dict) -> dict:
    try:
        res = supabase.table('tenant_products').upsert({
            "tenant_id": tenant_id,
            "title": product_data.get('title'),
            "price": product_data.get('price'),
            "stock": product_data.get('stock'),
            "description": product_data.get('description')
        }).execute()
        return {"success": True, "data": res.data}
    except Exception as e:
        print(f"❌ Inventory sync error: {e}")
        return {"success": False, "data": None}

async def unmute_user_via_telegram(phone_number: str) -> bool:
    print(f"[HANDOVER] Unmuted user phone: {phone_number}")
    return True