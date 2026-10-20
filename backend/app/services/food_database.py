"""
Database & Food Catalog Service for YAZIO-Next (DE/EU Open Food Facts + US USDA + Local SQLite).

Initializes the production schema (`schema.sql`), seeds verified German (REWE, EDEKA, ALDI, Lidl, dm)
and US (USDA) staple products for offline speed, and provides live barcode & text search via Open Food Facts.
"""

import json
import re
import sqlite3
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional


def _safe_float(val: Any, default: float = 0.0) -> float:
    """Safely extract a float from numbers or strings like '30 g' or '12,5'."""
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace(",", ".")
    if not s:
        return default
    match = re.search(r"[-+]?\d*\.?\d+", s)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return default
    return default

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "models" / "schema.sql"
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "yazio_next.db"


VERIFIED_SEED_PRODUCTS: List[Dict[str, Any]] = [
    {
        "product_id": "4388840215836",
        "barcode": "4388840215836",
        "name": "REWE Beste Wahl Skyr Natur (Скир)",
        "producer": "REWE",
        "country_code": "DE",
        "energy_kcal_100g": 64.0,
        "protein_g_100g": 11.0,
        "carbs_g_100g": 4.0,
        "sugar_g_100g": 4.0,
        "fat_g_100g": 0.2,
        "default_serving_label": "Becher / Стаканчик (150g)",
        "default_serving_grams": 150.0,
        "source": "openfoodfacts",
    },
    {
        "product_id": "4311501491829",
        "barcode": "4311501491829",
        "name": "EDEKA Bio Haferflocken Zartblatt (Овсянка)",
        "producer": "EDEKA",
        "country_code": "DE",
        "energy_kcal_100g": 372.0,
        "protein_g_100g": 13.5,
        "carbs_g_100g": 58.7,
        "sugar_g_100g": 0.7,
        "fat_g_100g": 7.0,
        "default_serving_label": "Portion / Порция (50g)",
        "default_serving_grams": 50.0,
        "source": "openfoodfacts",
    },
    {
        "product_id": "20636080",
        "barcode": "20636080",
        "name": "Milbona High Protein Pudding Chocolate (Протеиновый пудинг)",
        "producer": "Lidl / Milbona",
        "country_code": "DE",
        "energy_kcal_100g": 76.0,
        "protein_g_100g": 10.0,
        "carbs_g_100g": 5.2,
        "sugar_g_100g": 4.0,
        "fat_g_100g": 1.5,
        "default_serving_label": "Becher / Стаканчик (200g)",
        "default_serving_grams": 200.0,
        "source": "openfoodfacts",
    },
    {
        "product_id": "4008400404127",
        "barcode": "4008400404127",
        "name": "Milbona Skyr Natur (Скир Lidl)",
        "producer": "Lidl / Milbona",
        "country_code": "DE",
        "energy_kcal_100g": 65.0,
        "protein_g_100g": 11.0,
        "carbs_g_100g": 4.0,
        "sugar_g_100g": 4.0,
        "fat_g_100g": 0.2,
        "default_serving_label": "Portion / Порция (200g)",
        "default_serving_grams": 200.0,
        "source": "openfoodfacts",
    },
    {
        "product_id": "4058172924811",
        "barcode": "4058172924811",
        "name": "dmBio Protein Riegel Kakao & Cashew (Протеиновый батончик)",
        "producer": "dm-drogerie markt",
        "country_code": "DE",
        "energy_kcal_100g": 412.0,
        "protein_g_100g": 25.0,
        "carbs_g_100g": 34.0,
        "sugar_g_100g": 21.0,
        "fat_g_100g": 18.0,
        "default_serving_label": "Riegel / Батончик (45g)",
        "default_serving_grams": 45.0,
        "source": "openfoodfacts",
    },
    {
        "product_id": "staple_banana",
        "barcode": "0000000004011",
        "name": "Banane / Банан (Banana, fresh)",
        "producer": "Naturprodukt",
        "country_code": "DE",
        "energy_kcal_100g": 89.0,
        "protein_g_100g": 1.1,
        "carbs_g_100g": 22.8,
        "sugar_g_100g": 12.2,
        "fat_g_100g": 0.3,
        "default_serving_label": "Ganze Banane / Целый банан (150g)",
        "default_serving_grams": 150.0,
        "source": "usda",
    },
    {
        "product_id": "staple_apple",
        "barcode": None,
        "name": "Apfel / Яблоко (Apple, fresh)",
        "producer": "Naturprodukt",
        "country_code": "DE",
        "energy_kcal_100g": 52.0,
        "protein_g_100g": 0.3,
        "carbs_g_100g": 13.8,
        "sugar_g_100g": 10.4,
        "fat_g_100g": 0.2,
        "default_serving_label": "Mittelgroß / Среднее яблоко (180g)",
        "default_serving_grams": 180.0,
        "source": "usda",
    },
    {
        "product_id": "staple_eggs_scrambled",
        "barcode": None,
        "name": "Rührei / Яичница (Scrambled Eggs, 2 Eier)",
        "producer": "Hausgemacht",
        "country_code": "DE",
        "energy_kcal_100g": 148.0,
        "protein_g_100g": 12.6,
        "carbs_g_100g": 1.1,
        "sugar_g_100g": 0.8,
        "fat_g_100g": 10.0,
        "default_serving_label": "2 Eier / 2 яйца (120g)",
        "default_serving_grams": 120.0,
        "source": "usda",
    },
    {
        "product_id": "usda_chicken_breast_grilled",
        "barcode": None,
        "name": "Hähnchenbrustfilet / Куриная грудка (Chicken Breast)",
        "producer": "USDA / Naturprodukt",
        "country_code": "DE",
        "energy_kcal_100g": 165.0,
        "protein_g_100g": 31.0,
        "carbs_g_100g": 0.0,
        "sugar_g_100g": 0.0,
        "fat_g_100g": 3.6,
        "default_serving_label": "Filet / Филе (150g)",
        "default_serving_grams": 150.0,
        "source": "usda",
    },
    {
        "product_id": "usda_avocado_raw",
        "barcode": None,
        "name": "Avocado / Авокадо (Frisch)",
        "producer": "USDA / Naturprodukt",
        "country_code": "DE",
        "energy_kcal_100g": 160.0,
        "protein_g_100g": 2.0,
        "carbs_g_100g": 8.5,
        "sugar_g_100g": 0.7,
        "fat_g_100g": 14.7,
        "default_serving_label": "Halbe Avocado / Половинка (70g)",
        "default_serving_grams": 70.0,
        "source": "usda",
    },
    {
        "product_id": "staple_magerquark",
        "barcode": "4311501641934",
        "name": "Magerquark / Обезжиренный творог (0.2% Fett)",
        "producer": "EDEKA / REWE / ALDI",
        "country_code": "DE",
        "energy_kcal_100g": 67.0,
        "protein_g_100g": 12.0,
        "carbs_g_100g": 4.0,
        "sugar_g_100g": 4.0,
        "fat_g_100g": 0.2,
        "default_serving_label": "Portion / Порция (250g)",
        "default_serving_grams": 250.0,
        "source": "openfoodfacts",
    },
    {
        "product_id": "staple_salmon",
        "barcode": None,
        "name": "Lachsfilet / Филе лосося (Salmon, Atlantic)",
        "producer": "Naturprodukt",
        "country_code": "DE",
        "energy_kcal_100g": 208.0,
        "protein_g_100g": 20.4,
        "carbs_g_100g": 0.0,
        "sugar_g_100g": 0.0,
        "fat_g_100g": 13.4,
        "default_serving_label": "Filet / Филе (125g)",
        "default_serving_grams": 125.0,
        "source": "usda",
    },
    {
        "product_id": "staple_rice_cooked",
        "barcode": None,
        "name": "Reis gekocht / Отварной рис (Basmati / Jasmin)",
        "producer": "Grundnahrungsmittel",
        "country_code": "DE",
        "energy_kcal_100g": 130.0,
        "protein_g_100g": 2.7,
        "carbs_g_100g": 28.2,
        "sugar_g_100g": 0.1,
        "fat_g_100g": 0.3,
        "default_serving_label": "Portion / Порция (150g)",
        "default_serving_grams": 150.0,
        "source": "usda",
    },
    {
        "product_id": "staple_vollkornbrot",
        "barcode": None,
        "name": "Vollkornbrot / Цельнозерновой хлеб (German Wholegrain Bread)",
        "producer": "Bäckerei",
        "country_code": "DE",
        "energy_kcal_100g": 214.0,
        "protein_g_100g": 7.5,
        "carbs_g_100g": 38.0,
        "sugar_g_100g": 3.2,
        "fat_g_100g": 1.8,
        "default_serving_label": "Scheibe / Ломтик (60g)",
        "default_serving_grams": 60.0,
        "source": "openfoodfacts",
    },
    {
        "product_id": "staple_coffee_milk",
        "barcode": None,
        "name": "Kaffee mit Milch / Кофе с молоком (Cappuccino / Latte)",
        "producer": "Getränk",
        "country_code": "DE",
        "energy_kcal_100g": 24.0,
        "protein_g_100g": 1.6,
        "carbs_g_100g": 2.4,
        "sugar_g_100g": 2.4,
        "fat_g_100g": 0.8,
        "default_serving_label": "Tasse / Чашка (200ml)",
        "default_serving_grams": 200.0,
        "source": "openfoodfacts",
    },
]


class FoodDatabaseService:
    """Manages local SQLite storage and live Open Food Facts barcode & text lookups."""

    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        with self._get_conn() as conn:
            conn.executescript(schema_sql)
            for item in VERIFIED_SEED_PRODUCTS:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO products (
                        product_id, barcode, name, producer, country_code,
                        energy_kcal_100g, protein_g_100g, carbs_g_100g, sugar_g_100g,
                        fat_g_100g, default_serving_label, default_serving_grams, source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item["product_id"],
                        item["barcode"],
                        item["name"],
                        item["producer"],
                        item["country_code"],
                        item["energy_kcal_100g"],
                        item["protein_g_100g"],
                        item["carbs_g_100g"],
                        item["sugar_g_100g"],
                        item["fat_g_100g"],
                        item["default_serving_label"],
                        item["default_serving_grams"],
                        item["source"],
                    ),
                )
            conn.commit()

    def _save_product(self, item: Dict[str, Any]) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO products (
                    product_id, barcode, name, producer, country_code,
                    energy_kcal_100g, protein_g_100g, carbs_g_100g, sugar_g_100g,
                    fat_g_100g, default_serving_label, default_serving_grams, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["product_id"],
                    item["barcode"],
                    item["name"],
                    item["producer"],
                    item["country_code"],
                    item["energy_kcal_100g"],
                    item["protein_g_100g"],
                    item["carbs_g_100g"],
                    item["sugar_g_100g"],
                    item["fat_g_100g"],
                    item["default_serving_label"],
                    item["default_serving_grams"],
                    item["source"],
                ),
            )
            conn.commit()

    def search_local(self, query: str, limit: int = 20, fetch_remote: bool = False) -> List[Dict[str, Any]]:
        """
        Unicode-aware case-insensitive search (supports Cyrillic, German Umlauts, English).
        Optionally fetches live from Open Food Facts Germany/World when local matches are sparse.
        """
        q = (query or "").strip().lower()
        with self._get_conn() as conn:
            all_rows = conn.execute(
                "SELECT * FROM products ORDER BY is_verified DESC, name ASC"
            ).fetchall()

        if not q:
            return [dict(r) for r in all_rows[:limit]]

        matches: List[Dict[str, Any]] = []
        for r in all_rows:
            name_low = (r["name"] or "").lower()
            prod_low = (r["producer"] or "").lower()
            bcode = (r["barcode"] or "").lower()
            if q in name_low or q in prod_low or q == bcode:
                matches.append(dict(r))
                if len(matches) >= limit:
                    break

        if fetch_remote and len(matches) < 3 and len(q) >= 3:
            remote_items = self.search_openfoodfacts(query, limit=8)
            existing_ids = {m["product_id"] for m in matches}
            for item in remote_items:
                if item["product_id"] not in existing_ids:
                    matches.append(item)
                    existing_ids.add(item["product_id"])

        return matches[:limit]

    def search_openfoodfacts(self, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        """Live search against Open Food Facts (DE/World) with automatic SQLite caching."""
        params = urllib.parse.urlencode({
            "search_terms": query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": limit,
            "fields": "code,product_name,product_name_de,generic_name_de,brands,nutriments,serving_size,serving_quantity",
        })
        url = f"https://de.openfoodfacts.org/cgi/search.pl?{params}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "YazioNextApp/1.0 (Germany; contact@yazionext.de)"},
        )
        results: List[Dict[str, Any]] = []
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                for p in payload.get("products", []):
                    code = str(p.get("code") or "").strip()
                    name = (
                        p.get("product_name_de")
                        or p.get("product_name")
                        or p.get("generic_name_de")
                        or ""
                    ).strip()
                    nutr = p.get("nutriments", {})
                    kcal = _safe_float(nutr.get("energy-kcal_100g"), 0.0)
                    if kcal <= 0:
                        kj = _safe_float(nutr.get("energy-kj_100g") or nutr.get("energy_100g"), 0.0)
                        if kj > 0:
                            kcal = kj / 4.184
                    if not code or not name or kcal <= 0:
                        continue
                    srv_grams = _safe_float(p.get("serving_quantity"), 100.0)
                    if srv_grams <= 0:
                        srv_grams = 100.0
                    item = {
                        "product_id": code,
                        "barcode": code,
                        "name": name,
                        "producer": (p.get("brands") or "").split(",")[0].strip(),
                        "country_code": "DE",
                        "energy_kcal_100g": round(kcal, 1),
                        "protein_g_100g": round(_safe_float(nutr.get("proteins_100g"), 0.0), 1),
                        "carbs_g_100g": round(_safe_float(nutr.get("carbohydrates_100g"), 0.0), 1),
                        "sugar_g_100g": round(_safe_float(nutr.get("sugars_100g"), 0.0), 1),
                        "fat_g_100g": round(_safe_float(nutr.get("fat_100g"), 0.0), 1),
                        "default_serving_label": p.get("serving_size") or "Portion (100g)",
                        "default_serving_grams": srv_grams,
                        "source": "openfoodfacts",
                    }
                    self._save_product(item)
                    results.append(item)
        except Exception:
            pass
        return results

    def lookup_barcode(self, barcode: str, fetch_remote: bool = True) -> Optional[Dict[str, Any]]:
        """
        1. Checks local SQLite cache first (instant 1-3ms offline lookup).
        2. If not cached and `fetch_remote=True`, queries Open Food Facts API v2 (DE/EU/Global)
           using lightweight `fields` filter (~3x faster) and caches the result locally in SQLite.
        """
        t0 = time.perf_counter()
        barcode = (barcode or "").strip()
        if not barcode:
            return None

        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM products WHERE barcode = ? OR product_id = ?",
                (barcode, barcode),
            ).fetchone()
            if row:
                result = dict(row)
                result["_lookup_source"] = "sqlite_cache"
                result["_lookup_ms"] = round((time.perf_counter() - t0) * 1000.0, 2)
                return result

        if not fetch_remote:
            return None

        fields = "code,product_name,product_name_de,generic_name_de,brands,nutriments,serving_size,serving_quantity"
        url = f"https://world.openfoodfacts.org/api/v2/product/{urllib.parse.quote(barcode)}.json?fields={fields}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "YazioNextApp/1.0 (Germany; contact@yazionext.de)"},
        )
        try:
            with urllib.request.urlopen(req, timeout=6) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                if payload.get("status") != 1:
                    return None
                p = payload.get("product", {})
                nutr = p.get("nutriments", {})
                kcal = _safe_float(nutr.get("energy-kcal_100g"), 0.0)
                if kcal <= 0:
                    kj = _safe_float(nutr.get("energy-kj_100g") or nutr.get("energy_100g"), 0.0)
                    if kj > 0:
                        kcal = kj / 4.184
                srv_grams = _safe_float(p.get("serving_quantity"), 100.0)
                if srv_grams <= 0:
                    srv_grams = 100.0
                item = {
                    "product_id": barcode,
                    "barcode": barcode,
                    "name": (
                        p.get("product_name_de")
                        or p.get("product_name")
                        or p.get("generic_name_de")
                        or "Unbekanntes Produkt"
                    ),
                    "producer": p.get("brands", ""),
                    "country_code": "DE",
                    "energy_kcal_100g": round(kcal, 1),
                    "protein_g_100g": round(_safe_float(nutr.get("proteins_100g"), 0.0), 1),
                    "carbs_g_100g": round(_safe_float(nutr.get("carbohydrates_100g"), 0.0), 1),
                    "sugar_g_100g": round(_safe_float(nutr.get("sugars_100g"), 0.0), 1),
                    "fat_g_100g": round(_safe_float(nutr.get("fat_100g"), 0.0), 1),
                    "default_serving_label": p.get("serving_size") or "100g",
                    "default_serving_grams": srv_grams,
                    "source": "openfoodfacts",
                }
                self._save_product(item)
                item["_lookup_source"] = "openfoodfacts_live"
                item["_lookup_ms"] = round((time.perf_counter() - t0) * 1000.0, 2)
                return item
        except Exception:
            return None
