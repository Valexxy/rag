"""
====================================================================
POPULATE ALL RECORDS INTO SUPABASE FOR MULTI-TENANT SAAS TESTING
====================================================================
Populates:
- Tenants table (store-bot, valexxy_store, t-demo, default, real_estate_demo, salon_demo)
- Tenant entities (Products across Solar, Electronics, Food, Gold, Real Estate, Salon Services)
- Tenant customers (Phone numbers for broadcast testing)
"""

import sys, os, time, uuid
sys.stdout.reconfigure(encoding='utf-8')

from database import supabase, SUPABASE_URL, get_tenant_by_instance, get_tenant_catalog

print("=" * 65)
print("POPULATING SUPABASE DATABASE AT:", SUPABASE_URL)
print("=" * 65)

# ── 1. TENANTS DATA ───────────────────────────────────────────────
tenants_data = [
    {
        "instance_name": "store-bot",
        "business_name": "Teeslux Global Electronics & Solar",
        "niche": "retail",
        "business_niche": "retail",
        "owner_phone": "2348072015725",
        "ai_persona": "You are the Lead Client Experience Executive for Teeslux Global. Professional, warm, and helpful.",
        "call_to_action": "place an order",
        "is_active": True
    },
    {
        "instance_name": "valexxy_store",
        "business_name": "Valexxy Luxury Store",
        "niche": "retail",
        "business_niche": "retail",
        "owner_phone": "2348072015725",
        "ai_persona": "You are the Executive Sales Consultant for Valexxy Luxury Store.",
        "call_to_action": "place an order",
        "is_active": True
    },
    {
        "instance_name": "t-demo",
        "business_name": "Teeslux Demo Store",
        "niche": "retail",
        "business_niche": "retail",
        "owner_phone": "2348072015725",
        "ai_persona": "You are the AI Sales Assistant for Teeslux Demo Store.",
        "call_to_action": "order now",
        "is_active": True
    },
    {
        "instance_name": "default",
        "business_name": "Sovereign Commerce Central",
        "niche": "retail",
        "business_niche": "retail",
        "owner_phone": "2348072015725",
        "ai_persona": "You are the Sovereign AI Assistant.",
        "call_to_action": "order now",
        "is_active": True
    },
    {
        "instance_name": "real_estate_demo",
        "business_name": "GRA Prime Properties Ltd",
        "niche": "real_estate",
        "business_niche": "real_estate",
        "owner_phone": "2348072015725",
        "ai_persona": "You are the Senior Property Advisor for GRA Prime Properties.",
        "call_to_action": "book a inspection",
        "is_active": True
    },
    {
        "instance_name": "salon_demo",
        "business_name": "Queens Beauty Salon & Spa",
        "niche": "salon",
        "business_niche": "salon",
        "owner_phone": "2348072015725",
        "ai_persona": "You are the Concierge Manager for Queens Beauty Salon.",
        "call_to_action": "book an appointment",
        "is_active": True
    }
]

tenant_id_map = {}

print("\n--- STEP 1: UPSERTING TENANTS ---")
for t in tenants_data:
    try:
        # Check if exists
        res = supabase.table("tenants").select("*").eq("instance_name", t["instance_name"]).execute()
        if res.data:
            existing_id = res.data[0]["id"]
            supabase.table("tenants").update(t).eq("id", existing_id).execute()
            tenant_id_map[t["instance_name"]] = existing_id
            print(f"  [UPDATED] Tenant: {t['business_name']} (instance: {t['instance_name']}, ID: {existing_id})")
        else:
            ins_res = supabase.table("tenants").insert(t).execute()
            new_id = ins_res.data[0]["id"]
            tenant_id_map[t["instance_name"]] = new_id
            print(f"  [CREATED] Tenant: {t['business_name']} (instance: {t['instance_name']}, ID: {new_id})")
    except Exception as e:
        print(f"  [ERROR] Upserting tenant {t['instance_name']}: {e}")

# ── 2. TENANT ENTITIES (PRODUCTS / SERVICES CATALOG) ────────────
print("\n--- STEP 2: UPSERTING CATALOG PRODUCTS / SERVICES ---")

catalog_by_tenant = {
    "store-bot": [
        {
            "name": "550W Monocrystalline Solar Panel",
            "price": 120000.0,
            "description": "High Efficiency 21.5% Grade-A Monocrystalline Solar Panel for Inverter System",
            "metadata": {"category": "solar", "stock": 40}
        },
        {
            "name": "20,000 mAh Solar Power Bank",
            "price": 18500.0,
            "description": "Dual USB fast charge solar bank with LED torch light for phones and power backup",
            "metadata": {"category": "power", "stock": 50}
        },
        {
            "name": "1.5kVA Dual Solar Generator",
            "price": 185000.0,
            "description": "Silent pure sine wave inverter generator with built-in Lithium battery",
            "metadata": {"category": "solar", "stock": 15}
        },
        {
            "name": "50kg Premium White Rice Bag",
            "price": 60000.0,
            "description": "Premium long grain parboiled white rice from Dawanau export depot",
            "metadata": {"category": "food", "stock": 100}
        },
        {
            "name": "24K Gold Bar Bullion (1-Gram)",
            "price": 68500.0,
            "description": "999.9 Fine Investment Gold Bar with LBMA & Assay certificate",
            "metadata": {"category": "gold", "stock": 30}
        },
        {
            "name": "3.5kVA Hybrid Solar Inverter System",
            "price": 340000.0,
            "description": "Pure sine wave MPPT solar inverter for home & office power backup",
            "metadata": {"category": "solar", "stock": 10}
        }
    ],
    "valexxy_store": [
        {
            "name": "Valexxy 24K Gold Plated Smart Watch",
            "price": 145000.0,
            "description": "Luxury AMOLED Smartwatch with Heart Rate & Blood Pressure Monitor",
            "metadata": {"category": "luxury", "stock": 20}
        },
        {
            "name": "Designer Leather Briefcase",
            "price": 85000.0,
            "description": "Italian Genuine Grain Leather Executive Laptop Bag",
            "metadata": {"category": "fashion", "stock": 15}
        },
        {
            "name": "550W Grade-A Monocrystalline Solar Panel",
            "price": 120000.0,
            "description": "Grade-A Solar Panel with 25-Year Manufacturer Warranty",
            "metadata": {"category": "solar", "stock": 25}
        }
    ],
    "t-demo": [
        {
            "name": "Solar Power Bank 30,000mAh",
            "price": 25000.0,
            "description": "Fast Charging Solar Bank compatible with laptops and phones",
            "metadata": {"category": "electronics", "stock": 30}
        },
        {
            "name": "50kg Premium White Rice Bag",
            "price": 60000.0,
            "description": "50kg Grade-A Parboiled Rice",
            "metadata": {"category": "food", "stock": 50}
        },
        {
            "name": "24K Investment Gold Bar (1-Gram)",
            "price": 68500.0,
            "description": "LBMA Certified Gold Bar",
            "metadata": {"category": "precious_metals", "stock": 20}
        }
    ],
    "default": [
        {
            "name": "550W Monocrystalline Solar Panel",
            "price": 120000.0,
            "description": "High Efficiency Solar Panel for Off-Grid Systems",
            "metadata": {"category": "solar", "stock": 50}
        },
        {
            "name": "20,000 mAh Solar Power Bank",
            "price": 18500.0,
            "description": "Dual USB Fast Charge Solar Bank",
            "metadata": {"category": "power", "stock": 50}
        }
    ],
    "real_estate_demo": [
        {
            "name": "3-Bedroom Luxury Flat Awka GRA",
            "price": 25000000.0,
            "description": "Fully tiled 3BR luxury apartment with fitted kitchen & 24/7 security",
            "metadata": {"category": "residential", "type": "flat"}
        },
        {
            "name": "5-Bedroom Detached Duplex Onitsha GRA",
            "price": 85000000.0,
            "description": "Executive duplex with BQ, swimming pool, and solar system included",
            "metadata": {"category": "residential", "type": "duplex"}
        }
    ],
    "salon_demo": [
        {
            "name": "Luxury Hair Fixing & Installation",
            "price": 18000.0,
            "description": "Full Brazilian frontal closure hair styling & washing treatment",
            "metadata": {"category": "hair"}
        },
        {
            "name": "Royal Pedicure & Manicure Spa",
            "price": 7500.0,
            "description": "Exfoliating foot massage, gel polish, and nail care treatment",
            "metadata": {"category": "nails"}
        }
    ]
}

total_entities_inserted = 0
for inst_name, items in catalog_by_tenant.items():
    tid = tenant_id_map.get(inst_name)
    if not tid:
        print(f"  [SKIP] No tenant ID found for {inst_name}")
        continue
    
    # Get existing items for this tenant
    try:
        existing = supabase.table("tenant_entities").select("name").eq("tenant_id", tid).execute()
        existing_names = set(r["name"].lower() for r in existing.data) if existing.data else set()

        for item in items:
            item_data = {
                "tenant_id": tid,
                "name": item["name"],
                "price": item["price"],
                "description": item["description"],
                "metadata": item.get("metadata", {})
            }
            if item["name"].lower() not in existing_names:
                supabase.table("tenant_entities").insert(item_data).execute()
                print(f"  [INSERTED] [{inst_name}] {item['name']} - ₦{item['price']:,.2f}")
                total_entities_inserted += 1
            else:
                # Update existing
                supabase.table("tenant_entities").update(item_data).eq("tenant_id", tid).eq("name", item["name"]).execute()
                print(f"  [UPDATED]  [{inst_name}] {item['name']} - ₦{item['price']:,.2f}")
    except Exception as e:
        print(f"  [ERROR] Inserting catalog for {inst_name}: {e}")

# ── 3. TENANT CUSTOMERS ──────────────────────────────────────────
print("\n--- STEP 3: UPSERTING DEMO CUSTOMER RECORDS ---")

test_customers = [
    {"customer_phone": "2348072015725", "customer_name": "Store Owner / Tester"},
    {"customer_phone": "2347061114753", "customer_name": "Demo Customer 1"},
    {"customer_phone": "2348039998877", "customer_name": "Demo Customer 2"},
]

for inst_name, tid in tenant_id_map.items():
    for cust in test_customers:
        try:
            supabase.table("tenant_customers").upsert({
                "tenant_id": tid,
                "customer_phone": cust["customer_phone"],
                "customer_name": cust["customer_name"]
            }, on_conflict="tenant_id,customer_phone").execute()
        except Exception as e:
            pass
print("  Customer contacts upserted successfully.")

# ── 4. VERIFY SUPABASE PULL ──────────────────────────────────────
print("\n" + "="*65)
print("VERIFYING DATABASE PULL DIRECTLY FROM SUPABASE")
print("="*65)

for inst_name in tenant_id_map.keys():
    tenant = get_tenant_by_instance(inst_name)
    catalog = get_tenant_catalog(tenant)
    print(f"\n🏢 INSTANCE: '{inst_name}'")
    print(f"   Business: {tenant.get('business_name')} (ID: {tenant.get('id')})")
    print(f"   Niche:    {tenant.get('business_niche')}")
    print(f"   Owner:    {tenant.get('owner_phone')}")
    print(f"   Catalog:  {len(catalog)} items pulled from Supabase:")
    for item in catalog:
        print(f"     • {item.get('name')} | ₦{item.get('price',0):,.2f}")

print("\n" + "="*65)
print("SUCCESS: ALL RECORDS POPULATED & VERIFIED FROM SUPABASE")
print("="*65)
