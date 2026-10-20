-- ============================================================================
-- YAZIO-NEXT: PRODUCTION DATABASE SCHEMA (SQLite Offline-First & PostgreSQL)
-- Built directly from the analyzed YAZIO data model, stripped of ad-tech bloat
-- and enhanced with AI Token Sentinel & Freemium quota tracking.
-- ============================================================================

-- 1. USER PROFILE & GOALS (Based on extracted `user` & `userSettings` tables)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE,
    first_name TEXT NOT NULL DEFAULT '',
    gender TEXT NOT NULL CHECK (gender IN ('female', 'male', 'other')),
    birth_date TEXT NOT NULL,                  -- ISO YYYY-MM-DD (e.g. '1969-04-17')
    height_cm REAL NOT NULL,                   -- e.g. 170.0
    start_weight_kg REAL NOT NULL,             -- e.g. 77.1
    current_weight_kg REAL NOT NULL,           -- e.g. 77.1
    target_weight_kg REAL NOT NULL,            -- e.g. 74.0
    weight_change_per_week_kg REAL NOT NULL,   -- e.g. -0.6 (lose 0.6 kg/week)
    activity_degree TEXT NOT NULL DEFAULT 'moderately_active', -- PAL level
    overall_goal TEXT NOT NULL DEFAULT 'lose_weight',          -- lose_weight, maintain, build_muscle, gain_weight
    diet_type TEXT NOT NULL DEFAULT 'classic',                 -- classic, pescatarian, vegetarian, vegan, keto, low_carb
    weekend_buffer_mode TEXT NOT NULL DEFAULT 'none',          -- none, sat_sun, fri_sat_sun, fri_sat
    daily_calorie_goal INTEGER NOT NULL,       -- Calculated base target (e.g. 1843)
    protein_goal_g INTEGER NOT NULL,           -- Calculated target (e.g. 112)
    carbs_goal_g INTEGER NOT NULL,             -- Calculated target (e.g. 202)
    fat_goal_g INTEGER NOT NULL,               -- Calculated target (e.g. 59)
    energy_unit TEXT NOT NULL DEFAULT 'kcal',  -- kcal, kj
    weight_unit TEXT NOT NULL DEFAULT 'kg',    -- kg, lb
    height_unit TEXT NOT NULL DEFAULT 'cm',    -- cm, ft_in
    serving_unit TEXT NOT NULL DEFAULT 'g',    -- g, oz
    food_database_country TEXT NOT NULL DEFAULT 'DE', -- DE, AT, CH, US, GB, etc.
    language_code TEXT NOT NULL DEFAULT 'de',  -- de, en, ru
    premium_type TEXT NOT NULL DEFAULT 'free', -- free, pro_trial, pro_annual, pro_monthly
    free_ai_scans_used INTEGER NOT NULL DEFAULT 0,
    free_ai_scans_limit INTEGER NOT NULL DEFAULT 3,
    fast_log_minimalist_mode INTEGER NOT NULL DEFAULT 1, -- 1 = No mascot/chest popups!
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. USER NOTIFICATION & TRACKER SETTINGS (Based on `userSettings`)
CREATE TABLE IF NOT EXISTS user_settings (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    account_training_energy INTEGER NOT NULL DEFAULT 1,
    use_water_tracker INTEGER NOT NULL DEFAULT 1,
    water_goal_ml INTEGER NOT NULL DEFAULT 2500,
    show_food_notification INTEGER NOT NULL DEFAULT 1,
    show_water_notification INTEGER NOT NULL DEFAULT 1,
    show_weight_notification INTEGER NOT NULL DEFAULT 1,
    show_fasting_notification INTEGER NOT NULL DEFAULT 1
);

-- 3. PRODUCTS & BARCODES CACHE (Open Food Facts DE/EU + USDA + Custom)
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,               -- Barcode (EAN-13/UPC) or UUID
    barcode TEXT,
    name TEXT NOT NULL,
    producer TEXT,
    country_code TEXT DEFAULT 'DE',
    energy_kcal_100g REAL NOT NULL,
    protein_g_100g REAL NOT NULL,
    carbs_g_100g REAL NOT NULL,
    sugar_g_100g REAL DEFAULT 0,
    fat_g_100g REAL NOT NULL,
    saturated_fat_g_100g REAL DEFAULT 0,
    fiber_g_100g REAL DEFAULT 0,
    salt_g_100g REAL DEFAULT 0,
    default_serving_label TEXT DEFAULT 'Portion',
    default_serving_grams REAL DEFAULT 100.0,
    is_verified INTEGER NOT NULL DEFAULT 1,
    source TEXT NOT NULL DEFAULT 'openfoodfacts', -- openfoodfacts, usda, ai_vision, user_custom
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);

-- 4. DIARY CONSUMED ITEMS (Meals: breakfast, lunch, dinner, snack)
CREATE TABLE IF NOT EXISTS consumed_items (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    log_date TEXT NOT NULL,                    -- YYYY-MM-DD (Supports free pre-tracking for tomorrow!)
    meal_section TEXT NOT NULL CHECK (meal_section IN ('breakfast', 'lunch', 'dinner', 'snack')),
    product_id TEXT REFERENCES products(product_id),
    custom_name TEXT NOT NULL,
    serving_label TEXT DEFAULT 'g',
    amount_grams REAL NOT NULL,
    calories_kcal INTEGER NOT NULL,
    protein_g REAL NOT NULL,
    carbs_g REAL NOT NULL,
    fat_g REAL NOT NULL,
    tracking_method TEXT NOT NULL DEFAULT 'manual', -- manual, barcode, ai_photo, ai_voice, quick_add
    inserted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_consumed_user_date ON consumed_items(user_id, log_date);

-- 5. RECENTLY ADDED PRODUCTS (Based on `recentlyAddedProduct` for 1-Tap Swipe Logging)
CREATE TABLE IF NOT EXISTS recently_added_products (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id TEXT NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    serving_label TEXT,
    amount_grams REAL NOT NULL,
    insertion_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 6. INTERMITTENT FASTING (Based on `fastingPlan`)
CREATE TABLE IF NOT EXISTS fasting_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    protocol_type TEXT NOT NULL DEFAULT '16_8', -- 16_8 (Free), 18_6 (PRO), 20_4 (PRO), 14_10
    start_date TEXT NOT NULL,
    start_eating_at TEXT NOT NULL,              -- e.g. '12:00'
    end_eating_at TEXT NOT NULL,                -- e.g. '20:00'
    is_active INTEGER NOT NULL DEFAULT 1
);

-- 7. WATER INTAKE LOG (Based on `pendingWaterIntake`)
CREATE TABLE IF NOT EXISTS water_intake_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    log_date TEXT NOT NULL,                    -- YYYY-MM-DD
    intake_ml INTEGER NOT NULL,                -- e.g. 250
    logged_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 8. WEIGHT & BODY VALUES LOG (Based on `pendingWeightInsert`)
CREATE TABLE IF NOT EXISTS weight_logs (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    log_date TEXT NOT NULL,                    -- YYYY-MM-DD
    kilograms REAL NOT NULL,
    note TEXT,
    PRIMARY KEY (user_id, log_date)
);

-- 9. DAILY FEELINGS & SYMPTOMS (Based on `pendingFeeling`)
CREATE TABLE IF NOT EXISTS feeling_logs (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    log_date TEXT NOT NULL,
    note TEXT,
    tags_added TEXT NOT NULL DEFAULT '[]',     -- JSON array of mood/digestion/energy tags
    PRIMARY KEY (user_id, log_date)
);

-- 10. RECIPES & GROCERY LIST (Based on `recipe`, `recipeNutrient`, `recipeServing`, `groceryList`)
CREATE TABLE IF NOT EXISTS recipes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    difficulty TEXT NOT NULL DEFAULT 'easy',
    is_free_recipe INTEGER NOT NULL DEFAULT 0, -- 1 = Free, 0 = PRO
    image_url TEXT,
    portion_count INTEGER NOT NULL DEFAULT 2,
    preparation_time_minutes INTEGER NOT NULL DEFAULT 20,
    calories_per_portion INTEGER NOT NULL,
    protein_per_portion_g REAL NOT NULL,
    carbs_per_portion_g REAL NOT NULL,
    fat_per_portion_g REAL NOT NULL,
    tags_json TEXT NOT NULL DEFAULT '[]',      -- e.g. ["high_protein", "quick", "classic"]
    instructions_json TEXT NOT NULL DEFAULT '[]',
    servings_json TEXT NOT NULL DEFAULT '[]',
    locale TEXT NOT NULL DEFAULT 'de'
);

CREATE TABLE IF NOT EXISTS grocery_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipe_id TEXT,
    item_name TEXT NOT NULL,
    portion_count REAL NOT NULL DEFAULT 1.0,
    is_bought INTEGER NOT NULL DEFAULT 0
);

-- 11. FEATURE ACCESS SWITCHES (Entitlements, see app/config/paywall_config.json)
-- Usage counters for limited features (e.g. quota 'ai_scans' = 3 free AI scans)
CREATE TABLE IF NOT EXISTS feature_usage_counters (
    user_id INTEGER NOT NULL,
    quota_key TEXT NOT NULL,
    used INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, quota_key)
);

-- Every access decision (allowed / blocked) for beta usage analytics
CREATE TABLE IF NOT EXISTS feature_access_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    feature_key TEXT NOT NULL,
    allowed INTEGER NOT NULL,
    reason TEXT NOT NULL,                      -- beta_all_open, pro_subscriber, free_feature, within_free_limit, free_limit_reached, pro_required
    mode TEXT NOT NULL,                        -- beta_all_open, production
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_feature_events_feature ON feature_access_events(feature_key, reason);

-- 14. TELEMETRY & PERFORMANCE DIAGNOSTICS (Button Clicks & Barcode/Search Speed)
CREATE TABLE IF NOT EXISTS telemetry_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL DEFAULT 1,
    button_key TEXT NOT NULL,                  -- e.g. 'btn_barcode_open', 'barcode_lookup', 'search_local', 'search_online_de'
    button_label_ru TEXT NOT NULL,             -- Human-readable label in Russian
    target_value TEXT,                         -- Barcode, search query, or product name
    data_source TEXT NOT NULL DEFAULT 'local', -- 'sqlite_cache', 'openfoodfacts_live', 'gemini_ai', 'ui_action'
    duration_ms REAL NOT NULL DEFAULT 0.0,     -- Execution time in milliseconds
    status TEXT NOT NULL DEFAULT 'success',    -- 'success', 'not_found', 'error'
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_telemetry_button ON telemetry_events(button_key);
CREATE INDEX IF NOT EXISTS idx_telemetry_created ON telemetry_events(created_at DESC);
