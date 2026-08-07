-- 1. Tenants Table (Stores business profiles, credentials, and owner contact)
CREATE TABLE IF NOT EXISTS public.tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instance_name TEXT UNIQUE NOT NULL, -- Evolution API instance name
    business_name TEXT NOT NULL,
    owner_phone TEXT NOT NULL,          -- WhatsApp number of business owner/admin
    niche TEXT DEFAULT 'E-commerce',
    currency TEXT DEFAULT 'NGN',
    ai_persona TEXT DEFAULT 'You are a professional, helpful operations manager.',
    monnify_api_key TEXT,
    monnify_secret_key TEXT,
    monnify_contract_code TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Multi-Tenant Products & Services Catalog
CREATE TABLE IF NOT EXISTS public.tenant_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    price NUMERIC(12, 2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    category TEXT DEFAULT 'General',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Universal Flexible Customer Ledgers (For Savings, Bookings, Memberships, Custom Specs)
CREATE TABLE IF NOT EXISTS public.tenant_custom_ledgers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    customer_phone TEXT NOT NULL,
    ledger_type TEXT DEFAULT 'GENERAL', -- e.g., SAVINGS_SCHEME, APPOINTMENT, MEMBERSHIP
    data JSONB DEFAULT '{}'::jsonb,      -- E.g. {"contributed": 250000, "remaining": 350000}
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, customer_phone, ledger_type)
);

-- 4. Customer Contact Registry (For WhatsApp Broadcasts)
CREATE TABLE IF NOT EXISTS public.tenant_customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    customer_phone TEXT NOT NULL,
    customer_name TEXT,
    last_active TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, customer_phone)
);

-- 5. Multi-Tenant Transactions Ledger
CREATE TABLE IF NOT EXISTS public.tenant_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    customer_phone TEXT NOT NULL,
    payment_reference TEXT UNIQUE NOT NULL,
    transaction_reference TEXT,
    amount NUMERIC(12, 2) NOT NULL,
    status TEXT DEFAULT 'PENDING',
    checkout_url TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Bot Mutes (Muting per business instance & phone number)
CREATE TABLE IF NOT EXISTS public.tenant_bot_mutes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    customer_phone TEXT NOT NULL,
    muted_until TIMESTAMPTZ NOT NULL,
    UNIQUE(tenant_id, customer_phone)
);

-- Indexes for sub-second database operations
CREATE INDEX IF NOT EXISTS idx_tenant_instance ON public.tenants(instance_name);
CREATE INDEX IF NOT EXISTS idx_products_tenant ON public.tenant_products(tenant_id);
CREATE INDEX IF NOT EXISTS idx_custom_ledger ON public.tenant_custom_ledgers(tenant_id, customer_phone);
CREATE INDEX IF NOT EXISTS idx_trans_ref ON public.tenant_transactions(payment_reference);