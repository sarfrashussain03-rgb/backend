| table_name           | column_name         | data_type                   | is_nullable | column_default                      |
| -------------------- | ------------------- | --------------------------- | ----------- | ----------------------------------- |
| banners              | id                  | uuid                        | NO          | gen_random_uuid()                   |
| banners              | title               | character varying           | NO          | null                                |
| banners              | subtitle            | text                        | YES         | null                                |
| banners              | image_url           | text                        | YES         | null                                |
| banners              | badge_text          | character varying           | YES         | null                                |
| banners              | badge_color         | character varying           | YES         | '#FB923C'::character varying        |
| banners              | button_text         | character varying           | YES         | 'View Offer'::character varying     |
| banners              | link_type           | character varying           | YES         | 'category'::character varying       |
| banners              | link_value          | text                        | YES         | null                                |
| banners              | sort_order          | integer                     | YES         | 0                                   |
| banners              | is_active           | boolean                     | YES         | true                                |
| banners              | created_at          | timestamp without time zone | YES         | now()                               |
| business_details     | id                  | uuid                        | NO          | gen_random_uuid()                   |
| business_details     | user_id             | uuid                        | YES         | null                                |
| business_details     | business_name       | character varying           | YES         | null                                |
| business_details     | ssm_number          | character varying           | YES         | null                                |
| business_details     | ssm_document_url    | text                        | YES         | null                                |
| business_details     | business_address    | text                        | YES         | null                                |
| business_details     | approved_by         | uuid                        | YES         | null                                |
| business_details     | approved_at         | timestamp without time zone | YES         | null                                |
| business_details     | created_at          | timestamp without time zone | YES         | CURRENT_TIMESTAMP                   |
| cart_items           | id                  | uuid                        | NO          | gen_random_uuid()                   |
| cart_items           | cart_id             | uuid                        | YES         | null                                |
| cart_items           | product_id          | uuid                        | YES         | null                                |
| cart_items           | quantity            | integer                     | NO          | null                                |
| cart_items           | unit_price_snapshot | numeric                     | YES         | null                                |
| carts                | id                  | uuid                        | NO          | gen_random_uuid()                   |
| carts                | user_id             | uuid                        | YES         | null                                |
| carts                | updated_at          | timestamp without time zone | YES         | CURRENT_TIMESTAMP                   |
| categories           | id                  | uuid                        | NO          | gen_random_uuid()                   |
| categories           | name                | character varying           | NO          | null                                |
| categories           | description         | text                        | YES         | null                                |
| categories           | image_url           | text                        | YES         | null                                |
| categories           | parent_id           | uuid                        | YES         | null                                |
| categories           | is_active           | boolean                     | YES         | true                                |
| categories           | created_at          | timestamp without time zone | YES         | CURRENT_TIMESTAMP                   |
| categories           | malay_name          | character varying           | YES         | null                                |
| categories           | sort_order          | integer                     | YES         | 0                                   |
| categories           | icon                | character varying           | YES         | null                                |
| categories           | product_count       | integer                     | YES         | 0                                   |
| inventory            | product_id          | uuid                        | NO          | null                                |
| inventory            | stock_quantity      | integer                     | YES         | 0                                   |
| inventory            | restock_date        | timestamp without time zone | YES         | null                                |
| order_items          | id                  | uuid                        | NO          | gen_random_uuid()                   |
| order_items          | order_id            | uuid                        | YES         | null                                |
| order_items          | product_id          | uuid                        | YES         | null                                |
| order_items          | sku                 | character varying           | YES         | null                                |
| order_items          | barcode             | character varying           | YES         | null                                |
| order_items          | quantity            | integer                     | YES         | null                                |
| order_items          | unit_price          | numeric                     | YES         | null                                |
| order_items          | subtotal            | numeric                     | YES         | null                                |
| orders               | id                  | uuid                        | NO          | gen_random_uuid()                   |
| orders               | user_id             | uuid                        | YES         | null                                |
| orders               | order_number        | character varying           | YES         | null                                |
| orders               | total_amount        | numeric                     | YES         | null                                |
| orders               | shipping_method     | character varying           | YES         | null                                |
| orders               | delivery_date       | date                        | YES         | null                                |
| orders               | order_source        | character varying           | YES         | null                                |
| orders               | payment_status      | character varying           | YES         | 'pending'::character varying        |
| orders               | order_status        | character varying           | YES         | 'pending'::character varying        |
| orders               | created_at          | timestamp without time zone | YES         | CURRENT_TIMESTAMP                   |
| product_images       | id                  | uuid                        | NO          | gen_random_uuid()                   |
| product_images       | product_id          | uuid                        | YES         | null                                |
| product_images       | image_url           | text                        | YES         | null                                |
| product_images       | sort_order          | integer                     | YES         | 0                                   |
| product_tier_pricing | id                  | uuid                        | NO          | gen_random_uuid()                   |
| product_tier_pricing | product_id          | uuid                        | YES         | null                                |
| product_tier_pricing | min_qty             | integer                     | NO          | null                                |
| product_tier_pricing | max_qty             | integer                     | YES         | null                                |
| product_tier_pricing | unit_price          | numeric                     | NO          | null                                |
| products             | id                  | uuid                        | NO          | gen_random_uuid()                   |
| products             | category_id         | uuid                        | YES         | null                                |
| products             | name                | character varying           | NO          | null                                |
| products             | sku                 | character varying           | NO          | null                                |
| products             | barcode             | character varying           | YES         | null                                |
| products             | description         | text                        | YES         | null                                |
| products             | base_unit           | character varying           | YES         | null                                |
| products             | weight              | character varying           | YES         | null                                |
| products             | is_halal            | boolean                     | YES         | false                               |
| products             | status              | character varying           | YES         | 'active'::character varying         |
| products             | created_at          | timestamp without time zone | YES         | CURRENT_TIMESTAMP                   |
| products             | badge               | character varying           | YES         | null                                |
| products             | original_price      | numeric                     | YES         | null                                |
| products             | packaging           | text                        | YES         | null                                |
| products             | moq_text            | character varying           | YES         | null                                |
| products             | is_popular          | boolean                     | YES         | false                               |
| products             | is_featured         | boolean                     | YES         | false                               |
| products             | brand               | character varying           | YES         | null                                |
| users                | id                  | uuid                        | NO          | gen_random_uuid()                   |
| users                | firebase_uid        | character varying           | NO          | null                                |
| users                | name                | character varying           | YES         | null                                |
| users                | email               | character varying           | YES         | null                                |
| users                | phone               | character varying           | YES         | null                                |
| users                | role                | character varying           | YES         | 'wholesale_user'::character varying |
| users                | account_status      | character varying           | YES         | 'pending'::character varying        |
| users                | is_active           | boolean                     | YES         | true                                |
| users                | created_at          | timestamp without time zone | YES         | CURRENT_TIMESTAMP                   |