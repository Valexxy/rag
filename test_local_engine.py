import sys, os
sys.stdout.reconfigure(encoding='utf-8')

# Simulate what happens when BOTH Groq and Gemini are unavailable
os.environ['GROQ_API_KEY'] = ''
os.environ['GEMINI_API_KEY'] = ''

from database import get_tenant_by_instance, get_tenant_catalog
from multi_dimensional_ai_ensemble import MultiDimensionalAIEnsemble

ensemble = MultiDimensionalAIEnsemble()
tenant = get_tenant_by_instance('store-bot')
catalog = get_tenant_catalog(tenant['id'])
cat_summary = "\n".join([f"- {i.get('name')}: N{i.get('price'):,}" for i in catalog if isinstance(i, dict)])

queries = [
    "do you sell radios",
    "what is your address",
    "do you sell solar panels",
    "whats your price for the 550w panel",
    "do you deliver to Lagos",
    "can i pay with bank transfer",
    "what time do you open",
    "which market can i get oil",
    "do you sell cigarettes",
    "do you have generator",
]

print("=== LOCAL ENGINE RESPONSE TEST (No Groq, No Gemini) ===\n")
for q in queries:
    res = ensemble.generate_ensemble_reply(
        customer_query=q,
        catalog_context=cat_summary,
        chat_history='',
        tenant=tenant,
        catalog=catalog
    )
    arch = res.get('architecture', '?')
    snippet = res.get('reply', '')[:110].replace('\n', ' ')
    print(f"Q: {q}")
    print(f"  [{arch}]")
    print(f"  {snippet}...")
    print()
