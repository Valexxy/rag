-- =============================================================
-- Enterprise Multi-Tenant AI Commerce SaaS - Supabase Schema
-- =============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Tenants Table (Stores business profiles & instances)
CREATE TABLE IF NOT EXISTS public.tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instance_name TEXT UNIQUE NOT NULL, -- Evolution API instance name
    business_name TEXT NOT NULL,
    owner_phone TEXT NOT NULL,          -- Business owner/admin WhatsApp number
    business_niche TEXT DEFAULT 'retail',
    currency TEXT DEFAULT 'NGN',
    ai_persona TEXT DEFAULT 'You are a helpful customer service assistant.',
    monnify_api_key TEXT,
    monnify_secret_key TEXT,
    monnify_contract_code TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Universal Tenant Offerings / Products / Services Catalog
CREATE TABLE IF NOT EXISTS public.tenant_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    price NUMERIC(12, 2) NOT NULL DEFAULT 0,
    description TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,  -- E.g. {"stock": 10, "duration": "30 mins", "location": "Lagos"}
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Customer Ledgers (Flexible JSON records per customer)
CREATE TABLE IF NOT EXISTS public.customer_ledgers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    phone_number TEXT NOT NULL,
    ledger_type TEXT DEFAULT 'GENERAL',
    data JSONB DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, phone_number, ledger_type)
);

-- 4. Customer Contact Registry (For WhatsApp Broadcasts)
CREATE TABLE IF NOT EXISTS public.tenant_customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    phone_number TEXT NOT NULL,
    customer_name TEXT,
    last_active TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, phone_number)
);

-- 5. Multi-Tenant Transactions Ledger
CREATE TABLE IF NOT EXISTS public.tenant_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    phone_number TEXT NOT NULL,
    payment_reference TEXT UNIQUE NOT NULL,
    transaction_reference TEXT,
    amount NUMERIC(12, 2) NOT NULL,
    status TEXT DEFAULT 'PENDING',
    checkout_url TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Bot Mutes (Human Takeover Management)
CREATE TABLE IF NOT EXISTS public.bot_mutes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    phone_number TEXT NOT NULL,
    muted BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, phone_number)
);

-- Sub-second Performance Indexes
CREATE INDEX IF NOT EXISTS idx_tenant_instance ON public.tenants(instance_name);
CREATE INDEX IF NOT EXISTS idx_tenant_entities_tenant ON public.tenant_entities(tenant_id);
CREATE INDEX IF NOT EXISTS idx_customer_ledgers_phone ON public.customer_ledgers(tenant_id, phone_number);
CREATE INDEX IF NOT EXISTS idx_tenant_customers_phone ON public.tenant_customers(tenant_id, phone_number);
CREATE INDEX IF NOT EXISTS idx_bot_mutes_phone ON public.bot_mutes(tenant_id, phone_number);