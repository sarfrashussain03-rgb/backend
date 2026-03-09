-- =============================================
-- Migration 001: Enhance schema for wholesale UI
-- =============================================

-- 1. BANNERS TABLE (for homepage carousel)
CREATE TABLE IF NOT EXISTS banners (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    subtitle TEXT,
    image_url TEXT,
    badge_text VARCHAR(50),
    badge_color VARCHAR(20) DEFAULT '#FB923C',
    button_text VARCHAR(50) DEFAULT 'View Offer',
    link_type VARCHAR(30) DEFAULT 'category',  -- 'category', 'product', 'url'
    link_value TEXT,  -- category_id, product_id, or URL
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. ENHANCE PRODUCTS TABLE
-- Add columns only if they don't exist (safe idempotent migration)
DO $$
BEGIN
    -- badge: BESTSELLER, HOT, NEW, PROMO, etc.
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='products' AND column_name='badge') THEN
        ALTER TABLE products ADD COLUMN badge VARCHAR(30);
    END IF;

    -- original_price: for strikethrough display
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='products' AND column_name='original_price') THEN
        ALTER TABLE products ADD COLUMN original_price NUMERIC(10,2);
    END IF;

    -- packaging info: e.g. "24 packs per carton"
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='products' AND column_name='packaging') THEN
        ALTER TABLE products ADD COLUMN packaging TEXT;
    END IF;

    -- moq_text: minimum order quantity label
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='products' AND column_name='moq_text') THEN
        ALTER TABLE products ADD COLUMN moq_text VARCHAR(100);
    END IF;

    -- is_popular: for "Most Popular" section
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='products' AND column_name='is_popular') THEN
        ALTER TABLE products ADD COLUMN is_popular BOOLEAN DEFAULT FALSE;
    END IF;

    -- is_featured: for featured products
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='products' AND column_name='is_featured') THEN
        ALTER TABLE products ADD COLUMN is_featured BOOLEAN DEFAULT FALSE;
    END IF;

    -- brand
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='products' AND column_name='brand') THEN
        ALTER TABLE products ADD COLUMN brand VARCHAR(100);
    END IF;
END $$;

-- 3. ENHANCE CATEGORIES TABLE
DO $$
BEGIN
    -- malay_name: subtitle in Malay
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='categories' AND column_name='malay_name') THEN
        ALTER TABLE categories ADD COLUMN malay_name VARCHAR(150);
    END IF;

    -- sort_order
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='categories' AND column_name='sort_order') THEN
        ALTER TABLE categories ADD COLUMN sort_order INTEGER DEFAULT 0;
    END IF;

    -- icon: emoji or icon name
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='categories' AND column_name='icon') THEN
        ALTER TABLE categories ADD COLUMN icon VARCHAR(50);
    END IF;

    -- product_count: cached count for display
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='categories' AND column_name='product_count') THEN
        ALTER TABLE categories ADD COLUMN product_count INTEGER DEFAULT 0;
    END IF;
END $$;

-- 4. ENHANCE INVENTORY TABLE
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='inventory' AND column_name='restock_date') THEN
        ALTER TABLE inventory ADD COLUMN restock_date DATE;
    END IF;
END $$;
