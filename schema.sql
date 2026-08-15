-- =============================================================
-- Enterprise Multi-Tenant AI Commerce SaaS — Supabase PostgreSQL Schema
-- Version 2026.4 — Hardened Anti-Fraud & Dual Payment Engine
-- =============================================================

-- 1. Enable UUID Extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. Tenants Table (Stores WABA IDs, Monnify & Paystack API Credentials)
CREATE TABLE IF NOT EXISTS public.tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instance_name TEXT UNIQUE NOT NULL,       -- Evolution / Meta instance identifier
    business_name TEXT NOT NULL,
    owner_phone TEXT NOT NULL,                -- Business owner/admin WhatsApp number (+234...)
    waba_id TEXT UNIQUE,
    phone_number_id TEXT UNIQUE,
    business_niche TEXT DEFAULT 'retail',
    currency TEXT DEFAULT 'NGN',
    system_prompt_override TEXT,
    monnify_api_key TEXT,
    monnify_secret_key TEXT,
    monnify_contract_code TEXT,
    paystack_secret_key TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Products Table (Tenant-Isolated, With Stock & Native Image Cards)
CREATE TABLE IF NOT EXISTS public.products (
    id SERIAL PRIMARY KEY,
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    price NUMERIC(12, 2) NOT NULL CHECK (price > 0),
    stock INT NOT NULL CHECK (stock >= 0),
    description TEXT,
    image_url TEXT,                           -- High-res Native WhatsApp Product Image URL
    media_gallery JSONB DEFAULT '[]'::jsonb,  -- Additional photos/videos
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, name)
);

-- 4. Orders Table (With Partial Payment, Overpayment & Verification Tracking)
CREATE TABLE IF NOT EXISTS public.orders (
    id SERIAL PRIMARY KEY,
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    customer_phone TEXT NOT NULL,
    product_id TEXT,

    quantity INT DEFAULT 1 CHECK (quantity > 0),
    amount_expected NUMERIC(12, 2) NOT NULL,
    amount_paid NUMERIC(12, 2) DEFAULT 0.00,
    payment_reference TEXT UNIQUE NOT NULL,
    virtual_account_number TEXT,
    bank_name TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'underpaid', 'PENDING_HUMAN_VERIFICATION', 'paid', 'PAID_APPROVED', 'failed', 'refunded')),
    delivery_metadata JSONB DEFAULT '{}'::jsonb, -- Landmark directions & WhatsApp GPS pins
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Customer Ledgers (Stores Credit, Wallet Balances & Customer Memory)
CREATE TABLE IF NOT EXISTS public.customer_ledgers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    phone_number TEXT NOT NULL,
    ledger_type TEXT DEFAULT 'GENERAL',        -- E.g. 'STORE_CREDIT', 'WALLET_BALANCE', 'GENERAL'
    balance NUMERIC(12, 2) DEFAULT 0.00,
    data JSONB DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, phone_number, ledger_type)
);

-- 6. Bot Mutes / Human Takeover Circuit Breaker Table
CREATE TABLE IF NOT EXISTS public.bot_mutes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    phone_number TEXT NOT NULL,
    muted BOOLEAN DEFAULT TRUE,
    reason TEXT DEFAULT 'HUMAN_TAKEOVER',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, phone_number)
);

-- Enable Row-Level Security (RLS)
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;

-- Sub-second Performance & Security Indexes
CREATE INDEX IF NOT EXISTS idx_tenant_instance ON public.tenants(instance_name);
CREATE INDEX IF NOT EXISTS idx_products_tenant ON public.products(tenant_id, name);
CREATE INDEX IF NOT EXISTS idx_orders_tenant_phone ON public.orders(tenant_id, customer_phone);
CREATE INDEX IF NOT EXISTS idx_orders_reference ON public.orders(payment_reference);
CREATE INDEX IF NOT EXISTS idx_customer_ledgers_phone ON public.customer_ledgers(tenant_id, phone_number);

-- =============================================================
-- ATOMIC STOCK RESERVATION & CUMULATIVE PAYMENT STORED PROCEDURE
-- Uses Pessimistic Locking (FOR UPDATE) to prevent race conditions
-- =============================================================
CREATE OR REPLACE FUNCTION process_atomic_purchase(
    p_tenant_id UUID, 
    p_product_id TEXT, 
    p_quantity INT, 
    p_customer_phone TEXT, 
    p_reference TEXT,
    p_amount_received NUMERIC(12, 2)
) RETURNS JSONB AS $$
DECLARE
    v_stock INT;
    v_price NUMERIC(12, 2);
    v_expected NUMERIC(12, 2);
    v_existing_paid NUMERIC(12, 2) := 0.00;
    v_new_total_paid NUMERIC(12, 2);
    v_order_id INT;
    v_surplus NUMERIC(12, 2);
BEGIN
    -- 1. Lock Product Row for Update (Pessimistic Locking)
    SELECT stock, price INTO v_stock, v_price 
    FROM products 
    WHERE id::text = p_product_id AND tenant_id = p_tenant_id 
    FOR UPDATE;


    IF NOT FOUND THEN
        RETURN jsonb_build_object('success', false, 'reason', 'PRODUCT_NOT_FOUND');
    END IF;

    v_expected := v_price * p_quantity;

    -- 2. Check if Order Reference Already Exists
    SELECT id, amount_paid INTO v_order_id, v_existing_paid
    FROM orders
    WHERE payment_reference = p_reference AND tenant_id = p_tenant_id;

    v_new_total_paid := v_existing_paid + p_amount_received;

    -- 3. Handle Stock Deduction & Order Status Transitions
    IF v_new_total_paid < v_expected THEN
        -- PARTIAL PAYMENT / UNDERPAID
        IF v_order_id IS NOT NULL THEN
            UPDATE orders 
            SET amount_paid = v_new_total_paid, status = 'underpaid', updated_at = NOW() 
            WHERE id = v_order_id;
        ELSE
            INSERT INTO orders (tenant_id, customer_phone, product_id, quantity, amount_expected, amount_paid, payment_reference, status)
            VALUES (p_tenant_id, p_customer_phone, p_product_id, p_quantity, v_expected, v_new_total_paid, p_reference, 'underpaid');
        END IF;

        RETURN jsonb_build_object(
            'success', false, 
            'reason', 'UNDERPAID', 
            'amount_paid', v_new_total_paid, 
            'amount_expected', v_expected, 
            'balance_due', v_expected - v_new_total_paid
        );
    END IF;

    -- 4. FULL OR OVERPAYMENT REACHED: Check Stock Availability
    IF v_stock < p_quantity THEN
        RETURN jsonb_build_object('success', false, 'reason', 'OUT_OF_STOCK', 'available_stock', v_stock);
    END IF;

    -- Deduct Stock
    UPDATE products SET stock = stock - p_quantity WHERE id::text = p_product_id AND tenant_id = p_tenant_id;


    -- Record / Update Order as PENDING_HUMAN_VERIFICATION (Mandatory Human Protocol)
    IF v_order_id IS NOT NULL THEN
        UPDATE orders 
        SET amount_paid = v_new_total_paid, status = 'PENDING_HUMAN_VERIFICATION', updated_at = NOW() 
        WHERE id = v_order_id;
    ELSE
        INSERT INTO orders (tenant_id, customer_phone, product_id, quantity, amount_expected, amount_paid, payment_reference, status)
        VALUES (p_tenant_id, p_customer_phone, p_product_id, p_quantity, v_expected, v_new_total_paid, p_reference, 'PENDING_HUMAN_VERIFICATION');
    END IF;

    -- 5. Handle Overpayment Surplus -> Log in customer_ledgers as STORE_CREDIT
    IF v_new_total_paid > v_expected THEN
        v_surplus := v_new_total_paid - v_expected;
        INSERT INTO customer_ledgers (tenant_id, phone_number, ledger_type, balance, data)
        VALUES (p_tenant_id, p_customer_phone, 'STORE_CREDIT', v_surplus, jsonb_build_object('last_overpayment_ref', p_reference))
        ON CONFLICT (tenant_id, phone_number, ledger_type)
        DO UPDATE SET balance = customer_ledgers.balance + v_surplus, updated_at = NOW();

        RETURN jsonb_build_object(
            'success', true, 
            'status', 'PENDING_HUMAN_VERIFICATION', 
            'overpaid', true, 
            'surplus', v_surplus
        );
    END IF;

    RETURN jsonb_build_object('success', true, 'status', 'PENDING_HUMAN_VERIFICATION', 'overpaid', false);
END;
$$ LANGUAGE plpgsql;