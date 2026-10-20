"""
YAZIO-Next Main Backend Application (FastAPI).
Runs on local machine for development and deploys via Docker to production server.
Integrates:
- Exact calorie/macro engine (DGE 4.1/4.1/9.3 kcal/g + 30/40/25/5% meal budgets)
- Local SQLite database & Open Food Facts v2 integration
- Gemini 3.5 Flash AI food analysis & Gemini 3.1 Pro clinical doctor review
- Token Sentinel & User 4 isolation policy
"""

import os
import secrets
import sqlite3
import time
import json
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

from app.services.calorie_calculator import (
    build_personalized_plan,
    compute_meal_budgets,
    PersonalizedPlanResult,
    DIET_MACRO_SPLITS,
)
from app.services.food_database import FoodDatabaseService
from app.services.ai_nutrition import (
    AINutritionService,
    guard_prompt,
    FLASH_MODEL,
    PRO_DOCTOR_MODEL,
)
from app.services.entitlements import (
    EntitlementService,
    InvalidConfigError,
    UnknownFeatureError,
    VALID_MODES,
    VALID_TIERS,
)

app = FastAPI(
    title="YAZIO-Next API",
    description="Clean-room nutrition, fasting, and meal tracking API",
    version="1.0.0",
)

# Enable CORS for mobile app & web prototype
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "yazio_next.db")
food_service = FoodDatabaseService()
ai_service = AINutritionService()
entitlements = EntitlementService(db_path=DB_PATH)

# Admin token protects the paywall control endpoints. MUST be set via env on the server.
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "dev-local-token")


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def record_telemetry_event(
    button_key: str,
    button_label_ru: str,
    target_value: Optional[str] = None,
    data_source: str = "local",
    duration_ms: float = 0.0,
    status: str = "success",
    user_id: int = 1,
) -> None:
    """Persist button click and barcode/search latency metrics into SQLite `telemetry_events`."""
    try:
        conn = get_db_connection()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS telemetry_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1,
                button_key TEXT NOT NULL,
                button_label_ru TEXT NOT NULL,
                target_value TEXT,
                data_source TEXT NOT NULL DEFAULT 'local',
                duration_ms REAL NOT NULL DEFAULT 0.0,
                status TEXT NOT NULL DEFAULT 'success',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            INSERT INTO telemetry_events (
                user_id, button_key, button_label_ru, target_value,
                data_source, duration_ms, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                button_key,
                button_label_ru,
                target_value,
                data_source,
                round(float(duration_ms), 2),
                status,
            ),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def require_feature(user_id: int, feature_key: str, consume: bool = False) -> Dict[str, Any]:
    """
    Single gate used by every paid/limited endpoint.
    Raises HTTP 402 with paywall info if the user may not use the feature.
    """
    try:
        decision = entitlements.check(user_id, feature_key, consume=consume)
    except UnknownFeatureError:
        raise HTTPException(status_code=500, detail=f"Feature '{feature_key}' missing in paywall_config.json")
    if not decision.allowed:
        raise HTTPException(
            status_code=402,
            detail={"error": "paywall", **decision.to_dict()},
        )
    return decision.to_dict()


def require_admin(token: Optional[str]) -> None:
    if not token or not secrets.compare_digest(token, ADMIN_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid or missing X-Admin-Token")


DEMO_RECIPES = [
    (
        "rec_blueberry_shake", "Blueberry Coconut Shake",
        "Schneller, proteinreicher Shake mit Blaubeeren und Kokosmilch",
        "easy", 1, 1, 5, 358, 24.5, 42.0, 8.5,
        '["breakfast", "high_protein", "easy", "300_400_kcal"]', "de",
    ),
    (
        "rec_quark_bowl", "High Protein Quark Bowl",
        "Magerquark mit Beeren, Chiasamen und Mandelmus",
        "easy", 1, 1, 3, 285, 35.0, 22.0, 4.0,
        '["snack", "high_protein", "easy", "200_300_kcal"]', "de",
    ),
    (
        "rec_salmon_bowl", "Lachs-Bowl mit Quinoa und Avocado",
        "Omega-3-reiche Bowl mit Ofenlachs, Quinoa, Avocado und Edamame",
        "medium", 0, 2, 25, 545, 38.0, 42.0, 24.0,
        '["dinner", "high_protein", "omega3", "500_600_kcal"]', "de",
    ),
]


@app.on_event("startup")
def startup_event():
    food_service._init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Demo recipes (2 free + 1 PRO). INSERT OR IGNORE keeps existing data intact.
    cursor.executemany(
        """
        INSERT OR IGNORE INTO recipes (
            id, name, description, difficulty, is_free_recipe,
            portion_count, preparation_time_minutes, calories_per_portion,
            protein_per_portion_g, carbs_per_portion_g, fat_per_portion_g,
            tags_json, locale
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        DEMO_RECIPES,
    )

    # Demo users: 1 = regular test user, 4 = isolated test user (Gemini policy)
    for user_id, uuid in ((1, "demo-user-1"), (4, "test-user-4")):
        cursor.execute(
            """
            INSERT OR IGNORE INTO users (
                id, uuid, first_name, gender, birth_date, height_cm,
                start_weight_kg, current_weight_kg, target_weight_kg,
                weight_change_per_week_kg, overall_goal,
                daily_calorie_goal, protein_goal_g, carbs_goal_g, fat_goal_g,
                language_code, premium_type
            ) VALUES (?, ?, 'Demo', 'male', '1969-04-17', 170.0,
                      75.0, 75.0, 75.0, 0.0, 'maintain',
                      1838, 90, 224, 59, 'ru', 'free')
            """,
            (user_id, uuid),
        )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# 1. WEB APP & HEALTH METADATA
# ---------------------------------------------------------------------------
def _find_web_app_file() -> str:
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "mobile", "web_preview.html"),
        os.path.join(os.path.dirname(__file__), "static", "web_preview.html"),
        os.path.join(os.getcwd(), "mobile", "web_preview.html"),
        os.path.join(os.getcwd(), "web_preview.html"),
        os.path.abspath("mobile/web_preview.html"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return candidates[0]

WEB_APP_PATH = _find_web_app_file()


@app.get("/", include_in_schema=False)
@app.get("/app", include_in_schema=False)
def serve_mobile_web_app():
    web_path = _find_web_app_file()
    if os.path.exists(web_path):
        return FileResponse(web_path, media_type="text/html")
    return JSONResponse({"message": "YAZIO-Next API running. Open /docs for Swagger UI."})


@app.get("/download/android-apk", include_in_schema=False)
@app.get("/download/yazio-next.apk", include_in_schema=False)
def download_android_apk():
    """Direct APK download link for Android testers."""
    return RedirectResponse(
        url="https://github.com/igorvatyuk-commits/yazio-next/releases/latest/download/yazio-next.apk",
        status_code=302,
    )


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "yazio-next-backend",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "sqlite_ready",
    }


# ---------------------------------------------------------------------------
# 2. ONBOARDING & PERSONALIZED GOAL ENGINE
# ---------------------------------------------------------------------------
class OnboardingRequest(BaseModel):
    gender: str = Field(..., example="male")
    birth_date: str = Field(..., example="1969-04-17")
    height_cm: float = Field(..., example=170.0)
    current_weight_kg: float = Field(..., example=77.1)
    target_weight_kg: float = Field(..., example=74.0)
    activity_degree: str = Field(default="moderately_active", example="moderately_active")
    diet_type: str = Field(default="classic", example="classic")
    weekly_rate_kg: float = Field(default=0.62, example=0.62)
    weekend_option: str = Field(default="sat_sun", example="sat_sun")


@app.post("/api/goals/calculate")
def calculate_goals(req: OnboardingRequest):
    try:
        b_date = date.fromisoformat(req.birth_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid birth_date format (YYYY-MM-DD required)")

    plan: PersonalizedPlanResult = build_personalized_plan(
        gender=req.gender,
        birth_date=b_date,
        height_cm=req.height_cm,
        current_weight_kg=req.current_weight_kg,
        target_weight_kg=req.target_weight_kg,
        activity_degree=req.activity_degree,
        diet_type=req.diet_type,
        weekly_rate_kg=req.weekly_rate_kg,
        weekend_option=req.weekend_option,
        reference_date=date.today(),
    )

    return {
        "bmr_kcal": plan.bmr_kcal,
        "tdee_kcal": plan.tdee_kcal,
        "daily_calorie_target": plan.daily_calorie_target,
        "macros": {
            "protein_g": plan.protein_g,
            "carbs_g": plan.carbs_g,
            "fats_g": plan.fats_g,
        },
        "meal_budgets": plan.meal_budgets,
        "weekend_schedule": {
            "weekday_calories": plan.weekday_calories,
            "weekend_calories": plan.weekend_calories,
            "weekend_days": plan.weekend_days,
        },
        "bmi": {
            "current": plan.bmi_current,
            "target": plan.bmi_target,
        },
        "estimated_goal_date": plan.estimated_goal_date.isoformat(),
        "weeks_to_goal": plan.weeks_to_goal,
        "scientific_citations": plan.citations,
    }


# ---------------------------------------------------------------------------
# 3. DIARY & CONSUMED MEALS (Zero-friction, free tomorrow pre-tracking)
# ---------------------------------------------------------------------------
class LogFoodItemRequest(BaseModel):
    user_id: int = 1
    log_date: str = Field(default_factory=lambda: date.today().isoformat())
    meal_section: str = Field(..., example="breakfast")  # breakfast, lunch, dinner, snack
    product_id: Optional[str] = None
    custom_name: str = Field(..., example="Banana")
    serving_label: str = Field(default="g", example="g")
    amount_grams: float = Field(..., example=150.0)
    calories_kcal: int = Field(..., example=134)
    protein_g: float = Field(..., example=1.6)
    carbs_g: float = Field(..., example=34.3)
    fat_g: float = Field(..., example=0.5)
    tracking_method: str = Field(default="manual")


@app.get("/api/diary/{user_id}")
def get_user_diary(user_id: int, log_date: Optional[str] = None):
    if not log_date:
        log_date = date.today().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()

    # User goals (defaults to 1838 kcal maintain or custom)
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    daily_goal = user["daily_calorie_goal"] if user else 1838
    protein_goal = user["protein_goal_g"] if user else 90
    carbs_goal = user["carbs_goal_g"] if user else 224
    fat_goal = user["fat_goal_g"] if user else 59

    meal_budgets = compute_meal_budgets(daily_goal)

    # Consumed items for this date
    cursor.execute(
        "SELECT * FROM consumed_items WHERE user_id = ? AND log_date = ? ORDER BY inserted_at ASC",
        (user_id, log_date),
    )
    rows = cursor.fetchall()

    meals = {"breakfast": [], "lunch": [], "dinner": [], "snack": []}
    eaten_cals = 0
    eaten_protein = 0.0
    eaten_carbs = 0.0
    eaten_fat = 0.0

    for r in rows:
        section = r["meal_section"]
        item = {
            "id": r["id"],
            "custom_name": r["custom_name"],
            "serving_label": r["serving_label"],
            "amount_grams": r["amount_grams"],
            "calories_kcal": r["calories_kcal"],
            "protein_g": r["protein_g"],
            "carbs_g": r["carbs_g"],
            "fat_g": r["fat_g"],
            "tracking_method": r["tracking_method"],
        }
        if section in meals:
            meals[section].append(item)
        eaten_cals += r["calories_kcal"]
        eaten_protein += r["protein_g"]
        eaten_carbs += r["carbs_g"]
        eaten_fat += r["fat_g"]

    # Water intake
    cursor.execute(
        "SELECT SUM(intake_ml) as total_ml FROM water_intake_logs WHERE user_id = ? AND log_date = ?",
        (user_id, log_date),
    )
    water_row = cursor.fetchone()
    water_ml = water_row["total_ml"] if (water_row and water_row["total_ml"]) else 0

    conn.close()

    remaining_cals = max(0, daily_goal - eaten_cals)

    return {
        "date": log_date,
        "is_tomorrow": log_date > date.today().isoformat(),
        "summary": {
            "daily_goal": daily_goal,
            "eaten_kcal": eaten_cals,
            "remaining_kcal": remaining_cals,
            "burned_kcal": 0,
        },
        "macros": {
            "protein": {"eaten": round(eaten_protein, 1), "goal": protein_goal},
            "carbs": {"eaten": round(eaten_carbs, 1), "goal": carbs_goal},
            "fat": {"eaten": round(eaten_fat, 1), "goal": fat_goal},
        },
        "meal_budgets": meal_budgets,
        "meals": meals,
        "water": {
            "consumed_ml": water_ml,
            "goal_ml": 2000,
            "glasses": water_ml // 250,
        },
    }


@app.post("/api/diary/log-food")
def log_food_item(req: LogFoodItemRequest):
    # Pre-logging for future days is a switchable feature (free by default)
    if req.log_date > date.today().isoformat():
        require_feature(req.user_id, "plan_tomorrow")
    else:
        require_feature(req.user_id, "diary_logging")

    conn = get_db_connection()
    cursor = conn.cursor()

    item_id = f"item_{int(datetime.utcnow().timestamp() * 1000)}"
    cursor.execute(
        """
        INSERT INTO consumed_items (
            id, user_id, log_date, meal_section, product_id,
            custom_name, serving_label, amount_grams, calories_kcal,
            protein_g, carbs_g, fat_g, tracking_method
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            item_id,
            req.user_id,
            req.log_date,
            req.meal_section,
            req.product_id,
            req.custom_name,
            req.serving_label,
            req.amount_grams,
            req.calories_kcal,
            req.protein_g,
            req.carbs_g,
            req.fat_g,
            req.tracking_method,
        ),
    )
    conn.commit()
    conn.close()

    return {"status": "success", "item_id": item_id}


@app.delete("/api/diary/item/{item_id}")
def delete_food_item(item_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM consumed_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "item_id": item_id}


class WaterLogRequest(BaseModel):
    user_id: int = 1
    log_date: str = Field(default_factory=lambda: date.today().isoformat())
    intake_ml: int = 250


@app.post("/api/diary/log-water")
def log_water(req: WaterLogRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO water_intake_logs (user_id, log_date, intake_ml) VALUES (?, ?, ?)",
        (req.user_id, req.log_date, req.intake_ml),
    )
    conn.commit()
    conn.close()
    return {"status": "success", "added_ml": req.intake_ml}


class WaterSetGlassesRequest(BaseModel):
    user_id: int = 1
    log_date: str = Field(default_factory=lambda: date.today().isoformat())
    glasses: int = 0


@app.put("/api/diary/water")
def set_water_glasses(req: WaterSetGlassesRequest):
    require_feature(req.user_id, "water_weight_tracking")
    total_ml = max(0, req.glasses) * 250
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM water_intake_logs WHERE user_id = ? AND log_date = ?",
        (req.user_id, req.log_date),
    )
    if total_ml > 0:
        cursor.execute(
            "INSERT INTO water_intake_logs (user_id, log_date, intake_ml) VALUES (?, ?, ?)",
            (req.user_id, req.log_date, total_ml),
        )
    conn.commit()
    conn.close()
    return {"status": "success", "consumed_ml": total_ml, "glasses": max(0, req.glasses)}


class WeightLogRequest(BaseModel):
    user_id: int = 1
    log_date: str = Field(default_factory=lambda: date.today().isoformat())
    kilograms: float = 75.0
    note: Optional[str] = None


@app.post("/api/diary/log-weight")
def log_weight(req: WeightLogRequest):
    require_feature(req.user_id, "water_weight_tracking")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO weight_logs (user_id, log_date, kilograms, note)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, log_date) DO UPDATE SET kilograms = excluded.kilograms, note = excluded.note
        """,
        (req.user_id, req.log_date, req.kilograms, req.note),
    )
    cursor.execute(
        "UPDATE users SET current_weight_kg = ? WHERE id = ?",
        (req.kilograms, req.user_id),
    )
    conn.commit()
    conn.close()
    return {"status": "success", "kilograms": req.kilograms, "log_date": req.log_date}


# ---------------------------------------------------------------------------
# 4. FOOD SEARCH & BARCODE SCANNER (Local DB + Open Food Facts cache)
# ---------------------------------------------------------------------------
@app.get("/api/food/search")
def search_food(
    query: str = Query(default=""),
    limit: int = 20,
    remote: bool = False,
):
    t0 = time.perf_counter()
    results = food_service.search_local(query=query, limit=limit, fetch_remote=remote)
    server_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    source = "openfoodfacts_live" if remote else "sqlite_cache"
    if query.strip():
        record_telemetry_event(
            button_key="search_online_de" if remote else "search_local",
            button_label_ru="🌐 Поиск в онлайн-базе DE (Open Food Facts)" if remote else "🔎 Поиск по локальной базе (SQLite)",
            target_value=f"{query.strip()} ({len(results)} шт.)",
            data_source=source,
            duration_ms=server_ms,
            status="success" if results else "not_found",
        )
    return {
        "query": query,
        "count": len(results),
        "items": results,
        "lookup_source": source,
        "server_ms": server_ms,
    }


@app.get("/api/food/barcode/{barcode}")
def scan_barcode(barcode: str, user_id: int = 1):
    require_feature(user_id, "barcode_scan")
    t0 = time.perf_counter()
    product = food_service.lookup_barcode(barcode)
    total_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    if not product:
        record_telemetry_event(
            button_key="barcode_lookup",
            button_label_ru="📷 Сканирование штрихкода (EAN)",
            target_value=barcode,
            data_source="openfoodfacts_live",
            duration_ms=total_ms,
            status="not_found",
            user_id=user_id,
        )
        raise HTTPException(status_code=404, detail=f"Barcode {barcode} not found in database or Open Food Facts")
    lookup_source = product.get("_lookup_source", "sqlite_cache")
    server_ms = product.get("_lookup_ms", total_ms)
    record_telemetry_event(
        button_key="barcode_lookup",
        button_label_ru="📷 Сканирование штрихкода (EAN)",
        target_value=f"{barcode} → {product.get('name', '')[:32]}",
        data_source=lookup_source,
        duration_ms=server_ms,
        status="success",
        user_id=user_id,
    )
    return {
        "status": "found",
        "product": product,
        "lookup_source": lookup_source,
        "server_ms": server_ms,
    }


class BindBarcodeRequest(BaseModel):
    barcode: str
    name: str
    producer: str = "Eigenmarke / Фермерский продукт"
    energy_kcal_100g: float = 143.0
    protein_g_100g: float = 13.0
    carbs_g_100g: float = 0.7
    sugar_g_100g: float = 0.4
    fat_g_100g: float = 9.5
    default_serving_label: str = "2 шт. (120g)"
    default_serving_grams: float = 120.0


@app.post("/api/food/bind-barcode")
def bind_custom_barcode(req: BindBarcodeRequest):
    """Saves an unknown barcode permanently into local SQLite so future scans take ~1ms."""
    code = req.barcode.strip()
    if not code:
        raise HTTPException(status_code=400, detail="Barcode is required")
    item = {
        "product_id": code,
        "barcode": code,
        "name": req.name.strip(),
        "producer": req.producer.strip(),
        "country_code": "DE",
        "energy_kcal_100g": round(req.energy_kcal_100g, 1),
        "protein_g_100g": round(req.protein_g_100g, 1),
        "carbs_g_100g": round(req.carbs_g_100g, 1),
        "sugar_g_100g": round(req.sugar_g_100g, 1),
        "fat_g_100g": round(req.fat_g_100g, 1),
        "default_serving_label": req.default_serving_label,
        "default_serving_grams": req.default_serving_grams,
        "source": "user_verified",
    }
    food_service._save_product(item)
    record_telemetry_event(
        button_key="barcode_bind_custom",
        button_label_ru="📌 Привязка нового штрихкода в БД",
        target_value=f"{code} → {item['name'][:28]}",
        data_source="sqlite_cache",
        duration_ms=1.5,
        status="success",
    )
    return {"status": "saved", "product": item}


# ---------------------------------------------------------------------------
# 5. FASTING TRACKER (persisted in SQLite `fasting_plans`, gated via config)
# ---------------------------------------------------------------------------
FASTING_PROTOCOLS = [
    {"id": "12_12", "label": "12:12", "fasting_hours": 12, "feature": "fasting_basic"},
    {"id": "14_10", "label": "14:10", "fasting_hours": 14, "feature": "fasting_basic"},
    {"id": "16_8", "label": "16:8", "fasting_hours": 16, "feature": "fasting_16_8"},
    {"id": "18_6", "label": "18:6", "fasting_hours": 18, "feature": "fasting_advanced"},
    {"id": "20_4", "label": "20:4", "fasting_hours": 20, "feature": "fasting_advanced"},
    {"id": "omad", "label": "OMAD 23:1", "fasting_hours": 23, "feature": "fasting_advanced"},
]


@app.get("/api/fasting/{user_id}")
def get_fasting_status(user_id: int):
    access = entitlements.snapshot(user_id)["features"]
    protocols = [
        {**p, "locked": not access[p["feature"]]["allowed"]}
        for p in FASTING_PROTOCOLS
    ]

    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM fasting_plans WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    conn.close()

    proto_id = row["protocol_type"] if row else "12_12"
    proto_meta = next((p for p in FASTING_PROTOCOLS if p["id"] == proto_id), FASTING_PROTOCOLS[0])
    is_active = bool(row["is_active"]) if row else True
    started_at = row["start_date"] if row else datetime.utcnow().isoformat()
    try:
        elapsed_sec = max(0, int((datetime.utcnow() - datetime.fromisoformat(started_at)).total_seconds()))
    except Exception:
        elapsed_sec = 0
    elapsed_hours = elapsed_sec / 3600.0 if is_active else 0.0

    return {
        "user_id": user_id,
        "protocol_id": proto_meta["id"],
        "protocol": proto_meta["label"],
        "is_active": is_active,
        "started_at": started_at,
        "elapsed_seconds": elapsed_sec if is_active else 0,
        "fasting_hours": proto_meta["fasting_hours"],
        "eating_hours": 24 - proto_meta["fasting_hours"],
        "start_time": row["start_eating_at"] if row else "21:00",
        "end_time": row["end_eating_at"] if row else "09:00",
        "available_protocols": protocols,
        "phases": [
            {"hour": 4, "name": "Blood sugar drops", "reached": elapsed_hours >= 4},
            {"hour": 8, "name": "Digestion complete", "reached": elapsed_hours >= 8},
            {"hour": 12, "name": "Fat burning begins", "reached": elapsed_hours >= 12},
            {"hour": 16, "name": "Autophagy cellular renewal", "reached": elapsed_hours >= 16},
        ],
    }


class StartFastingRequest(BaseModel):
    protocol_id: str = Field(..., json_schema_extra={"example": "16_8"})
    elapsed_hours_offset: float = 0.0


@app.post("/api/fasting/{user_id}/start")
def start_fasting(user_id: int, req: StartFastingRequest):
    protocol = next((p for p in FASTING_PROTOCOLS if p["id"] == req.protocol_id), None)
    if not protocol:
        raise HTTPException(status_code=400, detail=f"Unknown protocol '{req.protocol_id}'")
    require_feature(user_id, protocol["feature"])

    from datetime import timedelta
    start_dt = datetime.utcnow() - timedelta(hours=max(0.0, req.elapsed_hours_offset))
    conn = get_db_connection()
    conn.execute("UPDATE fasting_plans SET is_active = 0 WHERE user_id = ?", (user_id,))
    conn.execute(
        """
        INSERT INTO fasting_plans (user_id, protocol_type, start_date, start_eating_at, end_eating_at, is_active)
        VALUES (?, ?, ?, '21:00', '09:00', 1)
        """,
        (user_id, protocol["id"], start_dt.isoformat()),
    )
    conn.commit()
    conn.close()
    return {"status": "started", "user_id": user_id, "protocol": protocol, "started_at": start_dt.isoformat()}


@app.post("/api/fasting/{user_id}/stop")
def stop_fasting(user_id: int):
    conn = get_db_connection()
    conn.execute("UPDATE fasting_plans SET is_active = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"status": "stopped", "user_id": user_id}


# ---------------------------------------------------------------------------
# 6. RECIPES CATALOG & 1-TAP LOGGING
# ---------------------------------------------------------------------------
@app.get("/api/recipes")
def list_recipes(calorie_max: Optional[int] = None, user_id: int = 1):
    conn = get_db_connection()
    cursor = conn.cursor()
    if calorie_max:
        cursor.execute("SELECT * FROM recipes WHERE calories_per_portion <= ? ORDER BY calories_per_portion ASC", (calorie_max,))
    else:
        cursor.execute("SELECT * FROM recipes ORDER BY calories_per_portion ASC")
    rows = cursor.fetchall()
    conn.close()

    full_catalog_allowed = entitlements.check(user_id, "recipes_full", log_event=False).allowed

    items = []
    for r in rows:
        is_free = bool(r["is_free_recipe"])
        items.append({
            "id": r["id"],
            "name": r["name"],
            "description": r["description"],
            "difficulty": r["difficulty"],
            "is_free": is_free,
            "locked": (not is_free) and (not full_catalog_allowed),
            "prep_time_minutes": r["preparation_time_minutes"],
            "calories": r["calories_per_portion"],
            "protein_g": r["protein_per_portion_g"],
            "carbs_g": r["carbs_per_portion_g"],
            "fat_g": r["fat_per_portion_g"],
            "tags": json.loads(r["tags_json"]),
        })
    return {"count": len(items), "recipes": items}


# ---------------------------------------------------------------------------
# 6b. USER PROFILE & GOALS MANAGEMENT (Real SQLite persistence)
# ---------------------------------------------------------------------------
@app.get("/api/profile/{user_id}")
def get_user_profile(user_id: int):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    weights = conn.execute(
        "SELECT log_date, kilograms, note FROM weight_logs WHERE user_id = ? ORDER BY log_date DESC LIMIT 10",
        (user_id,),
    ).fetchall()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return {
        "user": dict(user),
        "weight_history": [dict(w) for w in weights],
    }


class UpdateProfileRequest(BaseModel):
    gender: str = "male"
    birth_date: str = "1969-04-17"
    height_cm: float = 170.0
    current_weight_kg: float = 75.0
    target_weight_kg: float = 74.0
    activity_degree: str = "moderately_active"
    diet_type: str = "classic"
    weekend_buffer_mode: str = "none"
    weekly_rate_kg: float = 0.5


@app.put("/api/profile/{user_id}")
def update_user_profile(user_id: int, req: UpdateProfileRequest):
    if req.diet_type not in ("classic", "maintain_default"):
        require_feature(user_id, "custom_macros")

    try:
        b_date = date.fromisoformat(req.birth_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="birth_date must be YYYY-MM-DD")

    plan = build_personalized_plan(
        gender=req.gender,
        birth_date=b_date,
        height_cm=req.height_cm,
        current_weight_kg=req.current_weight_kg,
        target_weight_kg=req.target_weight_kg,
        activity_degree=req.activity_degree,
        diet_type=req.diet_type,
        weekly_rate_kg=req.weekly_rate_kg,
        weekend_option=req.weekend_buffer_mode,
        reference_date=date.today(),
    )

    conn = get_db_connection()
    conn.execute(
        """
        UPDATE users SET
            gender = ?, birth_date = ?, height_cm = ?,
            current_weight_kg = ?, target_weight_kg = ?,
            activity_degree = ?, diet_type = ?, weekend_buffer_mode = ?,
            daily_calorie_goal = ?, protein_goal_g = ?, carbs_goal_g = ?, fat_goal_g = ?
        WHERE id = ?
        """,
        (
            req.gender,
            req.birth_date,
            req.height_cm,
            req.current_weight_kg,
            req.target_weight_kg,
            req.activity_degree,
            req.diet_type,
            req.weekend_buffer_mode,
            plan.daily_calorie_target,
            plan.protein_g,
            plan.carbs_g,
            plan.fats_g,
            user_id,
        ),
    )
    conn.commit()
    conn.close()
    return {
        "status": "updated",
        "daily_calorie_goal": plan.daily_calorie_target,
        "macros": {"protein_g": plan.protein_g, "carbs_g": plan.carbs_g, "fats_g": plan.fats_g},
        "meal_budgets": plan.meal_budgets,
        "estimated_goal_date": plan.estimated_goal_date.isoformat(),
    }


# ---------------------------------------------------------------------------
# 7. AI PHOTO & DOCTOR NUTRITION (Governed by Gemini Policy)
# ---------------------------------------------------------------------------
class AIPhotoAnalyzeRequest(BaseModel):
    user_id: int = 1
    image_base64: Optional[str] = None
    mime_type: str = "image/jpeg"
    dish_hint: Optional[str] = None


@app.post("/api/ai/scan-plate")
def scan_plate_with_gemini(req: AIPhotoAnalyzeRequest):
    # Gate: 3 free scans (shared 'ai_scans' quota), then PRO — configurable in paywall_config.json
    require_feature(req.user_id, "ai_photo_scan")
    t0 = time.perf_counter()

    # Perform analysis strictly using gemini-3.5-flash with guard_prompt
    result = ai_service.analyze_meal_vision_or_text(
        user_id=req.user_id,
        description=req.dish_hint or "Dish photo",
        image_base64=req.image_base64,
        mime_type=req.mime_type,
    )
    server_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    record_telemetry_event(
        button_key="ai_meal_scan",
        button_label_ru="📸 AI-распознавание еды (Gemini 3.5 Flash)",
        target_value=(req.dish_hint or "Фото тарелки")[:36],
        data_source="gemini_ai",
        duration_ms=server_ms,
        status="success",
        user_id=req.user_id,
    )

    # Count the scan only after a successful analysis (failed AI calls cost the user nothing)
    usage = entitlements.check(req.user_id, "ai_photo_scan", consume=True, log_event=False)
    result["access"] = usage.to_dict()
    result["server_ms"] = server_ms
    return result


class ClinicalReviewRequest(BaseModel):
    user_id: int = 1
    weekly_summary: str
    lab_markers: Optional[str] = None


@app.post("/api/ai/clinical-review")
def clinical_review(req: ClinicalReviewRequest):
    require_feature(req.user_id, "doctor_llm")
    return ai_service.run_clinical_nutrition_review(
        user_id=req.user_id,
        weekly_summary_text=req.weekly_summary,
        lab_markers_text=req.lab_markers,
    )


# ---------------------------------------------------------------------------
# 8. ENTITLEMENTS (what the app is allowed to show for this user)
# ---------------------------------------------------------------------------
@app.get("/api/entitlements/{user_id}")
def get_entitlements(user_id: int):
    """Called by the app on start: which features are open / locked / how many free uses left."""
    return entitlements.snapshot(user_id)


class AccessCheckRequest(BaseModel):
    feature_key: str = Field(..., example="food_rating")
    consume: bool = False


@app.post("/api/entitlements/{user_id}/check")
def check_entitlement(user_id: int, req: AccessCheckRequest):
    """Called when the user taps a feature. Logged for beta usage analytics."""
    try:
        return entitlements.check(user_id, req.feature_key, consume=req.consume).to_dict()
    except UnknownFeatureError:
        raise HTTPException(status_code=404, detail=f"Unknown feature '{req.feature_key}'")


# ---------------------------------------------------------------------------
# 9. ADMIN: PAYWALL CONTROL PANEL (protected by X-Admin-Token)
# ---------------------------------------------------------------------------
@app.get("/api/admin/paywall-config")
def admin_get_config(x_admin_token: Optional[str] = Header(default=None)):
    require_admin(x_admin_token)
    return entitlements.get_config()


class ModeUpdateRequest(BaseModel):
    mode: str = Field(..., example="production")


@app.put("/api/admin/paywall-config/mode")
def admin_set_mode(req: ModeUpdateRequest, x_admin_token: Optional[str] = Header(default=None)):
    require_admin(x_admin_token)
    if req.mode not in VALID_MODES:
        raise HTTPException(status_code=400, detail=f"mode must be one of {VALID_MODES}")
    cfg = entitlements.set_mode(req.mode)
    return {"status": "updated", "mode": cfg["mode"], "version": cfg["version"]}


class FeatureUpdateRequest(BaseModel):
    tier: Optional[str] = Field(default=None, example="pro")
    free_limit: Optional[int] = Field(default=None, example=3)


@app.put("/api/admin/paywall-config/features/{feature_key}")
def admin_update_feature(
    feature_key: str,
    req: FeatureUpdateRequest,
    x_admin_token: Optional[str] = Header(default=None),
):
    require_admin(x_admin_token)
    if req.tier is not None and req.tier not in VALID_TIERS:
        raise HTTPException(status_code=400, detail=f"tier must be one of {VALID_TIERS}")
    try:
        cfg = entitlements.update_feature(feature_key, tier=req.tier, free_limit=req.free_limit)
    except UnknownFeatureError:
        raise HTTPException(status_code=404, detail=f"Unknown feature '{feature_key}'")
    except InvalidConfigError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"status": "updated", "feature": cfg["features"][feature_key], "version": cfg["version"]}


@app.get("/api/admin/feature-usage")
def admin_feature_usage(x_admin_token: Optional[str] = Header(default=None)):
    """Beta analytics: which features testers use most and where they hit the paywall."""
    require_admin(x_admin_token)
    return {"features": entitlements.usage_report()}


class PremiumUpdateRequest(BaseModel):
    premium_type: str = Field(..., json_schema_extra={"example": "pro_annual"})


@app.put("/api/admin/users/{user_id}/premium")
def admin_set_premium(
    user_id: int,
    req: PremiumUpdateRequest,
    x_admin_token: Optional[str] = Header(default=None),
):
    """
    Testing tool: manually grant / revoke PRO for a user.
    In production the premium status is set by the RevenueCat webhook after a real purchase.
    """
    require_admin(x_admin_token)
    allowed_types = ("free", "pro_trial", "pro_annual", "pro_monthly")
    if req.premium_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"premium_type must be one of {allowed_types}")
    conn = get_db_connection()
    cur = conn.execute("UPDATE users SET premium_type = ? WHERE id = ?", (req.premium_type, user_id))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return {"status": "updated", "user_id": user_id, "premium_type": req.premium_type}


@app.post("/api/admin/users/{user_id}/reset-usage")
def admin_reset_usage(user_id: int, x_admin_token: Optional[str] = Header(default=None)):
    """Testing tool: reset free-use counters (e.g. 3 AI scans) for one tester."""
    require_admin(x_admin_token)
    conn = get_db_connection()
    conn.execute("DELETE FROM feature_usage_counters WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"status": "reset", "user_id": user_id}


# ---------------------------------------------------------------------------
# 10. TELEMETRY & PERFORMANCE DIAGNOSTICS (Button Clicks & Barcode/Search Speed)
# ---------------------------------------------------------------------------
class TelemetryEventRequest(BaseModel):
    user_id: int = 1
    button_key: str
    button_label_ru: str
    target_value: Optional[str] = None
    data_source: str = "ui_action"
    duration_ms: float = 0.0
    status: str = "success"


@app.post("/api/telemetry/event")
def log_client_telemetry(req: TelemetryEventRequest):
    """Logs any UI button click and client-side action timing."""
    record_telemetry_event(
        button_key=req.button_key,
        button_label_ru=req.button_label_ru,
        target_value=req.target_value,
        data_source=req.data_source,
        duration_ms=req.duration_ms,
        status=req.status,
        user_id=req.user_id,
    )
    return {"status": "logged"}


@app.get("/api/telemetry/dashboard")
def get_telemetry_dashboard():
    """
    Returns full testing analytics:
    1. Most clicked buttons by testers (popularity ranking + avg latency ms).
    2. Speed comparison by data source (SQLite local cache vs Open Food Facts API vs Gemini AI).
    3. Recent barcode scans and searches with exact execution times.
    """
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS telemetry_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 1,
            button_key TEXT NOT NULL,
            button_label_ru TEXT NOT NULL,
            target_value TEXT,
            data_source TEXT NOT NULL DEFAULT 'local',
            duration_ms REAL NOT NULL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'success',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    total_row = conn.execute("SELECT COUNT(*) AS cnt FROM telemetry_events").fetchone()
    total_events = int(total_row["cnt"]) if total_row else 0

    top_rows = conn.execute(
        """
        SELECT
            button_key,
            button_label_ru,
            COUNT(*) AS clicks,
            ROUND(AVG(duration_ms), 1) AS avg_ms,
            ROUND(MIN(duration_ms), 1) AS min_ms,
            ROUND(MAX(duration_ms), 1) AS max_ms
        FROM telemetry_events
        GROUP BY button_key, button_label_ru
        ORDER BY clicks DESC, avg_ms ASC
        """
    ).fetchall()

    top_buttons = []
    for r in top_rows:
        clicks = int(r["clicks"])
        top_buttons.append({
            "button_key": r["button_key"],
            "button_label_ru": r["button_label_ru"],
            "clicks": clicks,
            "share_pct": round((clicks / total_events) * 100.0, 1) if total_events > 0 else 0.0,
            "avg_ms": r["avg_ms"] or 0.0,
            "min_ms": r["min_ms"] or 0.0,
            "max_ms": r["max_ms"] or 0.0,
        })

    src_rows = conn.execute(
        """
        SELECT
            data_source,
            COUNT(*) AS count,
            ROUND(AVG(duration_ms), 1) AS avg_ms,
            ROUND(MIN(duration_ms), 1) AS min_ms,
            ROUND(MAX(duration_ms), 1) AS max_ms
        FROM telemetry_events
        WHERE duration_ms > 0
        GROUP BY data_source
        ORDER BY avg_ms ASC
        """
    ).fetchall()

    recent_rows = conn.execute(
        """
        SELECT
            id, button_key, button_label_ru, target_value,
            data_source, duration_ms, status, created_at
        FROM telemetry_events
        ORDER BY id DESC
        LIMIT 30
        """
    ).fetchall()
    conn.close()

    return {
        "total_events": total_events,
        "top_buttons": top_buttons,
        "source_comparison": [dict(r) for r in src_rows],
        "recent_events": [dict(r) for r in recent_rows],
    }


@app.delete("/api/telemetry/clear")
def clear_telemetry_events():
    conn = get_db_connection()
    conn.execute("DELETE FROM telemetry_events")
    conn.commit()
    conn.close()
    return {"status": "cleared"}
