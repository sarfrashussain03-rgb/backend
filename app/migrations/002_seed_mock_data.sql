-- =============================================
-- SEED 002: Mock data for wholesale UI
-- Run AFTER 001_enhance_schema.sql
-- =============================================

-- ========== UPDATE EXISTING CATEGORIES ==========
UPDATE categories SET malay_name = 'Sayur Segar', sort_order = 1, icon = '🥬', product_count = 6
WHERE id = '84b596d8-6a35-410e-b375-b938e42e9dce';

UPDATE categories SET malay_name = 'Buah-buahan', sort_order = 2, icon = '🍎', product_count = 4
WHERE id = '03fcbd74-b66b-41ba-b0a4-ac2f00008ce7';

UPDATE categories SET malay_name = 'Makanan Beku', sort_order = 3, icon = '🧊', product_count = 4
WHERE id = '2e591f67-5bde-4bb1-a320-cf4a33d3aa18';

UPDATE categories SET malay_name = 'Minuman', sort_order = 4, icon = '🥤', product_count = 4
WHERE id = '3e70605a-916f-486f-9475-188e53ff1534';

UPDATE categories SET malay_name = 'Rempah Ratus', sort_order = 5, icon = '🌶️', product_count = 4
WHERE id = '61bead0e-2952-4887-b112-a7128fb10ef0';

-- ========== UPDATE EXISTING PRODUCTS ==========
UPDATE products SET badge = 'HOT', original_price = 5.50, moq_text = 'Per kg', is_popular = true, brand = 'Local Farm', packaging = '10kg per box'
WHERE id = '9f2818a0-cdd2-4ae7-b287-fc7a6de04f5b';

UPDATE products SET badge = 'PROMO', original_price = 7.00, moq_text = 'Per kg', is_popular = true, brand = 'Local Farm', packaging = '5kg per bag'
WHERE id = '35db6389-4c2c-474f-8f30-85e543ec3a40';

UPDATE products SET badge = 'NEW', moq_text = 'Per kg', is_popular = true, brand = 'Import Co', packaging = '8kg per carton', is_featured = true
WHERE id = 'eaa2d791-a7c8-448b-b252-44646e10e3c7';

UPDATE products SET badge = 'BESTSELLER', moq_text = 'Per piece', is_popular = true, brand = 'Fresh Poultry', packaging = '12 pcs per carton', is_featured = true
WHERE id = 'dfc2c9ba-19b0-4698-b28b-fee4ffd32ef7';

UPDATE products SET moq_text = 'Per packet', is_popular = true, brand = 'Spice World', packaging = '20 packets per box'
WHERE id = 'a114dc65-ded6-4de0-8b57-1c80bebeba2f';

-- ========== ADD MORE PRODUCTS (Vegetables) ==========
INSERT INTO products (id, category_id, name, sku, barcode, description, base_unit, weight, is_halal, status, badge, original_price, moq_text, is_popular, brand, packaging)
VALUES
('f1a2b3c4-1111-4111-b111-111111111101', '84b596d8-6a35-410e-b375-b938e42e9dce',
 'Potato', 'SKU-POT-001', '1111111112', 'Fresh potato from Cameron Highlands. Perfect for frying, boiling, and baking. Premium grade A quality.', 'kg', '1kg', true, 'active', NULL, NULL, 'MOQ: 5 kg', false, 'Cameron Farm', '25kg per bag'),

('f1a2b3c4-1111-4111-b111-111111111102', '84b596d8-6a35-410e-b375-b938e42e9dce',
 'Onion Red', 'SKU-ONR-001', '1111111113', 'Indian red onion. Strong flavor, essential for all Malaysian cooking. Grade A selection.', 'kg', '1kg', true, 'active', 'PROMO', 4.50, 'Per kg', false, 'India Import', '20kg per bag'),

('f1a2b3c4-1111-4111-b111-111111111103', '84b596d8-6a35-410e-b375-b938e42e9dce',
 'Carrot', 'SKU-CAR-001', '1111111114', 'Fresh carrot from Australia. Sweet and crunchy, great for soups and salads.', 'kg', '1kg', true, 'active', NULL, NULL, 'MOQ: 3 kg', false, 'Aussie Fresh', '10kg per carton'),

('f1a2b3c4-1111-4111-b111-111111111104', '84b596d8-6a35-410e-b375-b938e42e9dce',
 'Cabbage', 'SKU-CAB-001', '1111111115', 'Fresh round cabbage. Crispy texture, ideal for stir-fry and coleslaw.', 'piece', '1 piece', true, 'active', NULL, NULL, 'Per piece', false, 'Local Farm', '6 pcs per box');

-- ========== ADD MORE PRODUCTS (Fruits) ==========
INSERT INTO products (id, category_id, name, sku, barcode, description, base_unit, weight, is_halal, status, badge, original_price, moq_text, is_popular, brand, packaging)
VALUES
('f1a2b3c4-2222-4222-b222-222222222201', '03fcbd74-b66b-41ba-b0a4-ac2f00008ce7',
 'Banana Berangan', 'SKU-BAN-001', '3333333334', 'Local Berangan banana. Sweet and fragrant. Popular dessert banana in Malaysia.', 'bunch', '1 bunch', true, 'active', 'HOT', NULL, 'Per bunch', true, 'Local Farm', '12 bunches per box'),

('f1a2b3c4-2222-4222-b222-222222222202', '03fcbd74-b66b-41ba-b0a4-ac2f00008ce7',
 'Orange Mandarin', 'SKU-ORM-001', '3333333335', 'Imported mandarin orange. Sweet and juicy, perfect for Chinese New Year.', 'kg', '1kg', true, 'active', NULL, NULL, 'MOQ: 5 kg', false, 'China Import', '10kg per carton'),

('f1a2b3c4-2222-4222-b222-222222222203', '03fcbd74-b66b-41ba-b0a4-ac2f00008ce7',
 'Watermelon', 'SKU-WAT-001', '3333333336', 'Fresh seedless watermelon. Sweet and refreshing fruit for hot weather.', 'piece', '1 piece', true, 'active', 'BESTSELLER', NULL, 'Per piece', false, 'Local Farm', '4 pcs per lot');

-- ========== ADD MORE PRODUCTS (Frozen Food) ==========
INSERT INTO products (id, category_id, name, sku, barcode, description, base_unit, weight, is_halal, status, badge, original_price, moq_text, is_popular, brand, packaging)
VALUES
('f1a2b3c4-3333-4333-b333-333333333301', '2e591f67-5bde-4bb1-a320-cf4a33d3aa18',
 'Frozen Prawns', 'SKU-FPR-001', '4444444445', 'IQF frozen prawns, size 31-40. Fresh from the sea, individually quick frozen for maximum freshness.', 'kg', '1kg', true, 'active', 'NEW', NULL, 'Per kg', true, 'Sea Fresh', '10kg per carton'),

('f1a2b3c4-3333-4333-b333-333333333302', '2e591f67-5bde-4bb1-a320-cf4a33d3aa18',
 'Fish Fillet', 'SKU-FFL-001', '4444444446', 'Frozen dory fish fillet. Boneless and skinless, easy to cook.', 'kg', '1kg', true, 'active', NULL, NULL, 'MOQ: 3 kg', false, 'Ocean Catch', '5kg per pack'),

('f1a2b3c4-3333-4333-b333-333333333303', '2e591f67-5bde-4bb1-a320-cf4a33d3aa18',
 'Frozen Mixed Vegetables', 'SKU-FMV-001', '4444444447', 'Mixed frozen vegetables: corn, carrots, peas, green beans. Convenience pack.', 'kg', '1kg', true, 'active', NULL, NULL, 'Per pack', false, 'Green Valley', '12 packs per carton');

-- ========== ADD MORE PRODUCTS (Beverages) ==========
INSERT INTO products (id, category_id, name, sku, barcode, description, base_unit, weight, is_halal, status, badge, original_price, moq_text, is_popular, brand, packaging)
VALUES
('f1a2b3c4-4444-4444-b444-444444444401', '3e70605a-916f-486f-9475-188e53ff1534',
 'Mineral Water 1.5L', 'SKU-MWT-001', '6666666661', 'Pure mineral water, 1.5L bottle. Essential hydration for everyday needs.', 'carton', '12 bottles', true, 'active', 'BESTSELLER', NULL, 'Per carton', true, 'Spritzer', '12 bottles per carton'),

('f1a2b3c4-4444-4444-b444-444444444402', '3e70605a-916f-486f-9475-188e53ff1534',
 'Milo 1kg', 'SKU-MIL-001', '6666666662', 'Nestle Milo chocolate malt drink powder. Malaysia''s favourite drink.', 'packet', '1kg', true, 'active', 'HOT', 22.00, 'MOQ: 6 packets', true, 'Nestle', '6 packets per carton'),

('f1a2b3c4-4444-4444-b444-444444444403', '3e70605a-916f-486f-9475-188e53ff1534',
 'Teh Tarik 3-in-1', 'SKU-TT3-001', '6666666663', 'Instant Teh Tarik (pulled milk tea) 3-in-1 sachets. Authentic Malaysian taste.', 'box', '15 sachets', true, 'active', NULL, NULL, 'MOQ: 12 boxes', false, 'Aik Cheong', '12 boxes per carton'),

('f1a2b3c4-4444-4444-b444-444444444404', '3e70605a-916f-486f-9475-188e53ff1534',
 'Soy Milk 1L', 'SKU-SOY-001', '6666666664', 'Fresh soy milk, unsweetened. Nutritious plant-based milk alternative.', 'pack', '1L', true, 'active', 'NEW', NULL, 'Per pack', false, 'Yeo''s', '12 packs per carton');

-- ========== ADD MORE PRODUCTS (Spices) ==========
INSERT INTO products (id, category_id, name, sku, barcode, description, base_unit, weight, is_halal, status, badge, original_price, moq_text, is_popular, brand, packaging)
VALUES
('f1a2b3c4-5555-4555-b555-555555555501', '61bead0e-2952-4887-b112-a7128fb10ef0',
 'Turmeric Powder', 'SKU-TUM-001', '5555555556', 'Premium turmeric powder. Essential spice for curry and rice dishes. Vibrant yellow color.', 'packet', '250g', true, 'active', NULL, NULL, 'MOQ: 10 packets', false, 'Baba''s', '20 packets per box'),

('f1a2b3c4-5555-4555-b555-555555555502', '61bead0e-2952-4887-b112-a7128fb10ef0',
 'Chilli Powder', 'SKU-CHP-001', '5555555557', 'Red chilli powder. Medium heat level, perfect for rendang and curry dishes.', 'packet', '250g', true, 'active', 'PROMO', 3.50, 'MOQ: 10 packets', true, 'Baba''s', '20 packets per box'),

('f1a2b3c4-5555-4555-b555-555555555503', '61bead0e-2952-4887-b112-a7128fb10ef0',
 'Cinnamon Sticks', 'SKU-CIN-001', '5555555558', 'Whole cinnamon sticks. Aromatic spice used in briyani and desserts.', 'packet', '100g', true, 'active', NULL, NULL, 'Per packet', false, 'Spice World', '30 packets per box');

-- ========== ADD ONE OUT-OF-STOCK PRODUCT ==========
INSERT INTO products (id, category_id, name, sku, barcode, description, base_unit, weight, is_halal, status, badge, original_price, moq_text, is_popular, brand, packaging)
VALUES
('f1a2b3c4-6666-4666-b666-666666666601', '84b596d8-6a35-410e-b375-b938e42e9dce',
 'Broccoli Imported', 'SKU-BRO-001', '1111111116', 'Fresh imported broccoli. Currently out of stock, restocking in 3 days.', 'kg', '1kg', true, 'inactive', NULL, NULL, 'Per kg', false, 'Aussie Fresh', '8kg per carton');

-- ========== TIER PRICING FOR NEW PRODUCTS ==========
INSERT INTO product_tier_pricing (id, product_id, min_qty, max_qty, unit_price) VALUES
-- Potato
('a1b2c3d4-1001-4001-a001-100000000001', 'f1a2b3c4-1111-4111-b111-111111111101', 1, 10, 3.50),
('a1b2c3d4-1001-4001-a001-100000000002', 'f1a2b3c4-1111-4111-b111-111111111101', 11, NULL, 3.00),
-- Onion Red
('a1b2c3d4-1002-4002-a002-100000000001', 'f1a2b3c4-1111-4111-b111-111111111102', 1, 5, 4.00),
('a1b2c3d4-1002-4002-a002-100000000002', 'f1a2b3c4-1111-4111-b111-111111111102', 6, NULL, 3.50),
-- Carrot
('a1b2c3d4-1003-4003-a003-100000000001', 'f1a2b3c4-1111-4111-b111-111111111103', 1, NULL, 6.00),
-- Cabbage
('a1b2c3d4-1004-4004-a004-100000000001', 'f1a2b3c4-1111-4111-b111-111111111104', 1, NULL, 2.50),
-- Banana
('a1b2c3d4-2001-4001-a001-200000000001', 'f1a2b3c4-2222-4222-b222-222222222201', 1, NULL, 4.50),
-- Orange
('a1b2c3d4-2002-4002-a002-200000000001', 'f1a2b3c4-2222-4222-b222-222222222202', 1, 5, 7.00),
('a1b2c3d4-2002-4002-a002-200000000002', 'f1a2b3c4-2222-4222-b222-222222222202', 6, NULL, 6.50),
-- Watermelon
('a1b2c3d4-2003-4003-a003-200000000001', 'f1a2b3c4-2222-4222-b222-222222222203', 1, NULL, 12.00),
-- Frozen Prawns
('a1b2c3d4-3001-4001-a001-300000000001', 'f1a2b3c4-3333-4333-b333-333333333301', 1, 5, 35.00),
('a1b2c3d4-3001-4001-a001-300000000002', 'f1a2b3c4-3333-4333-b333-333333333301', 6, NULL, 32.00),
-- Fish Fillet
('a1b2c3d4-3002-4002-a002-300000000001', 'f1a2b3c4-3333-4333-b333-333333333302', 1, NULL, 18.00),
-- Frozen Mixed Veg
('a1b2c3d4-3003-4003-a003-300000000001', 'f1a2b3c4-3333-4333-b333-333333333303', 1, NULL, 5.50),
-- Mineral Water
('a1b2c3d4-4001-4001-a001-400000000001', 'f1a2b3c4-4444-4444-b444-444444444401', 1, 10, 8.00),
('a1b2c3d4-4001-4001-a001-400000000002', 'f1a2b3c4-4444-4444-b444-444444444401', 11, NULL, 7.50),
-- Milo
('a1b2c3d4-4002-4002-a002-400000000001', 'f1a2b3c4-4444-4444-b444-444444444402', 1, 6, 20.50),
('a1b2c3d4-4002-4002-a002-400000000002', 'f1a2b3c4-4444-4444-b444-444444444402', 7, NULL, 19.00),
-- Teh Tarik
('a1b2c3d4-4003-4003-a003-400000000001', 'f1a2b3c4-4444-4444-b444-444444444403', 1, NULL, 6.50),
-- Soy Milk
('a1b2c3d4-4004-4004-a004-400000000001', 'f1a2b3c4-4444-4444-b444-444444444404', 1, NULL, 3.80),
-- Turmeric
('a1b2c3d4-5001-4001-a001-500000000001', 'f1a2b3c4-5555-4555-b555-555555555501', 1, NULL, 2.50),
-- Chilli Powder
('a1b2c3d4-5002-4002-a002-500000000001', 'f1a2b3c4-5555-4555-b555-555555555502', 1, 10, 3.00),
('a1b2c3d4-5002-4002-a002-500000000002', 'f1a2b3c4-5555-4555-b555-555555555502', 11, NULL, 2.70),
-- Cinnamon
('a1b2c3d4-5003-4003-a003-500000000001', 'f1a2b3c4-5555-4555-b555-555555555503', 1, NULL, 4.50),
-- Broccoli (out of stock)
('a1b2c3d4-6001-4001-a001-600000000001', 'f1a2b3c4-6666-4666-b666-666666666601', 1, NULL, 8.50);

-- ========== INVENTORY FOR NEW PRODUCTS ==========
INSERT INTO inventory (product_id, stock_quantity, restock_date) VALUES
('f1a2b3c4-1111-4111-b111-111111111101', 500, NULL),
('f1a2b3c4-1111-4111-b111-111111111102', 300, NULL),
('f1a2b3c4-1111-4111-b111-111111111103', 200, NULL),
('f1a2b3c4-1111-4111-b111-111111111104', 150, NULL),
('f1a2b3c4-2222-4222-b222-222222222201', 100, NULL),
('f1a2b3c4-2222-4222-b222-222222222202', 400, NULL),
('f1a2b3c4-2222-4222-b222-222222222203', 50, NULL),
('f1a2b3c4-3333-4333-b333-333333333301', 200, NULL),
('f1a2b3c4-3333-4333-b333-333333333302', 150, NULL),
('f1a2b3c4-3333-4333-b333-333333333303', 300, NULL),
('f1a2b3c4-4444-4444-b444-444444444401', 1000, NULL),
('f1a2b3c4-4444-4444-b444-444444444402', 500, NULL),
('f1a2b3c4-4444-4444-b444-444444444403', 600, NULL),
('f1a2b3c4-4444-4444-b444-444444444404', 200, NULL),
('f1a2b3c4-5555-4555-b555-555555555501', 400, NULL),
('f1a2b3c4-5555-4555-b555-555555555502', 350, NULL),
('f1a2b3c4-5555-4555-b555-555555555503', 200, NULL),
('f1a2b3c4-6666-4666-b666-666666666601', 0, '2026-02-27')
ON CONFLICT (product_id) DO UPDATE SET stock_quantity = EXCLUDED.stock_quantity, restock_date = EXCLUDED.restock_date;

-- ========== PRODUCT IMAGES FOR NEW PRODUCTS ==========
-- Using placeholder filenames (you can upload actual images to Supabase storage)
INSERT INTO product_images (id, product_id, image_url, sort_order) VALUES
('b1c2d3e4-1001-4001-b001-100000000001', 'f1a2b3c4-1111-4111-b111-111111111101', 'potato.jpg', 0),
('b1c2d3e4-1002-4002-b002-100000000001', 'f1a2b3c4-1111-4111-b111-111111111102', 'onion_red.jpg', 0),
('b1c2d3e4-1003-4003-b003-100000000001', 'f1a2b3c4-1111-4111-b111-111111111103', 'carrot.jpg', 0),
('b1c2d3e4-1004-4004-b004-100000000001', 'f1a2b3c4-1111-4111-b111-111111111104', 'cabbage.jpg', 0),
('b1c2d3e4-2001-4001-b001-200000000001', 'f1a2b3c4-2222-4222-b222-222222222201', 'banana.jpg', 0),
('b1c2d3e4-2002-4002-b002-200000000001', 'f1a2b3c4-2222-4222-b222-222222222202', 'orange.jpg', 0),
('b1c2d3e4-2003-4003-b003-200000000001', 'f1a2b3c4-2222-4222-b222-222222222203', 'watermelon.jpg', 0),
('b1c2d3e4-3001-4001-b001-300000000001', 'f1a2b3c4-3333-4333-b333-333333333301', 'prawns.jpg', 0),
('b1c2d3e4-3002-4002-b002-300000000001', 'f1a2b3c4-3333-4333-b333-333333333302', 'fish_fillet.jpg', 0),
('b1c2d3e4-3003-4003-b003-300000000001', 'f1a2b3c4-3333-4333-b333-333333333303', 'mixed_veg.jpg', 0),
('b1c2d3e4-4001-4001-b001-400000000001', 'f1a2b3c4-4444-4444-b444-444444444401', 'mineral_water.jpg', 0),
('b1c2d3e4-4002-4002-b002-400000000001', 'f1a2b3c4-4444-4444-b444-444444444402', 'milo.jpg', 0),
('b1c2d3e4-4003-4003-b003-400000000001', 'f1a2b3c4-4444-4444-b444-444444444403', 'teh_tarik.jpg', 0),
('b1c2d3e4-4004-4004-b004-400000000001', 'f1a2b3c4-4444-4444-b444-444444444404', 'soy_milk.jpg', 0),
('b1c2d3e4-5001-4001-b001-500000000001', 'f1a2b3c4-5555-4555-b555-555555555501', 'turmeric.jpg', 0),
('b1c2d3e4-5002-4002-b002-500000000001', 'f1a2b3c4-5555-4555-b555-555555555502', 'chilli_powder.jpg', 0),
('b1c2d3e4-5003-4003-b003-500000000001', 'f1a2b3c4-5555-4555-b555-555555555503', 'cinnamon.jpg', 0),
('b1c2d3e4-6001-4001-b001-600000000001', 'f1a2b3c4-6666-4666-b666-666666666601', 'broccoli.jpg', 0);

-- ========== BANNERS ==========
INSERT INTO banners (id, title, subtitle, image_url, badge_text, badge_color, button_text, link_type, link_value, sort_order, is_active) VALUES
('d1e2f3a4-0001-4001-c001-000000000001',
 'Fresh Vegetables Sale',
 'Get the best wholesale prices for fresh vegetables & more.',
 'banners/vegetables_banner.jpg',
 'BULK DEAL', '#FB923C', 'View Offer', 'category', '84b596d8-6a35-410e-b375-b938e42e9dce', 1, true),

('d1e2f3a4-0002-4002-c002-000000000002',
 'Frozen Food Festival',
 'Special prices on frozen meat and seafood. Limited time only!',
 'banners/frozen_banner.jpg',
 'SALE', '#EF4444', 'Shop Now', 'category', '2e591f67-5bde-4bb1-a320-cf4a33d3aa18', 2, true),

('d1e2f3a4-0003-4003-c003-000000000003',
 'New Arrivals: Beverages',
 'Check out our latest collection of beverages and drinks.',
 'banners/beverages_banner.jpg',
 'NEW', '#10B981', 'Explore', 'category', '3e70605a-916f-486f-9475-188e53ff1534', 3, true);

-- ========== UPDATE CATEGORY PRODUCT COUNTS ==========
UPDATE categories SET product_count = (
    SELECT COUNT(*) FROM products WHERE products.category_id = categories.id AND products.status = 'active'
);
