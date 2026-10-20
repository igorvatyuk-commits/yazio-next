"""
Tests for the entitlement (paywall switch) service and its API endpoints.
Each test runs on a temporary copy of the database and paywall config.
"""

import json
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.services.entitlements import (  # noqa: E402
    EntitlementService,
    InvalidConfigError,
    UnknownFeatureError,
)

REAL_CONFIG = BACKEND_DIR / "app" / "config" / "paywall_config.json"


@pytest.fixture
def service(tmp_path):
    config_path = tmp_path / "paywall_config.json"
    shutil.copy(REAL_CONFIG, config_path)
    db_path = tmp_path / "test.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, premium_type TEXT NOT NULL)")
        conn.execute("INSERT INTO users (id, premium_type) VALUES (1, 'free'), (2, 'pro_annual')")
    return EntitlementService(db_path=str(db_path), config_path=str(config_path))


def test_beta_mode_opens_everything(service):
    service.set_mode("beta_all_open")
    for key in ("doctor_llm", "fasting_advanced", "food_rating", "recipes_full"):
        decision = service.check(1, key)
        assert decision.allowed is True
        assert decision.reason == "beta_all_open"


def test_beta_mode_still_counts_usage(service):
    service.set_mode("beta_all_open")
    for _ in range(5):
        service.check(1, "ai_photo_scan", consume=True)
    report = {r["feature_key"]: r for r in service.usage_report()}
    assert report["ai_photo_scan"]["total_events"] == 5
    assert report["ai_photo_scan"]["blocked_events"] == 0


def test_production_free_feature_allowed(service):
    service.set_mode("production")
    decision = service.check(1, "barcode_scan")
    assert decision.allowed is True
    assert decision.reason == "free_feature"


def test_production_pro_feature_blocked_for_free_user(service):
    service.set_mode("production")
    decision = service.check(1, "doctor_llm")
    assert decision.allowed is False
    assert decision.reason == "pro_required"
    assert decision.show_paywall is True


def test_production_pro_subscriber_gets_everything(service):
    service.set_mode("production")
    decision = service.check(2, "doctor_llm")
    assert decision.allowed is True
    assert decision.reason == "pro_subscriber"


def test_limited_feature_three_free_then_paywall(service):
    service.set_mode("production")
    for expected_remaining in (2, 1, 0):
        decision = service.check(1, "ai_photo_scan", consume=True)
        assert decision.allowed is True
        assert decision.remaining == expected_remaining
    blocked = service.check(1, "ai_photo_scan", consume=True)
    assert blocked.allowed is False
    assert blocked.reason == "free_limit_reached"


def test_photo_and_voice_share_ai_quota(service):
    service.set_mode("production")
    service.check(1, "ai_photo_scan", consume=True)
    service.check(1, "ai_photo_scan", consume=True)
    voice = service.check(1, "ai_voice_text", consume=True)
    assert voice.allowed is True and voice.remaining == 0
    assert service.check(1, "ai_photo_scan").allowed is False


def test_moving_feature_to_pro_applies_without_restart(service):
    service.set_mode("production")
    assert service.check(1, "fasting_16_8").allowed is True
    service.update_feature("fasting_16_8", tier="pro")
    assert service.check(1, "fasting_16_8").allowed is False


def test_config_version_increments_on_change(service):
    before = service.get_config()["version"]
    service.update_feature("food_rating", tier="free")
    assert service.get_config()["version"] == before + 1


def test_invalid_values_are_rejected(service):
    with pytest.raises(InvalidConfigError):
        service.set_mode("everything_free_forever")
    with pytest.raises(InvalidConfigError):
        service.update_feature("food_rating", tier="gold")
    with pytest.raises(UnknownFeatureError):
        service.update_feature("teleportation", tier="pro")


def test_snapshot_does_not_log_events(service):
    service.snapshot(1)
    assert service.usage_report() == []


def test_config_file_stays_valid_json(service):
    service.update_feature("grocery_list", tier="free")
    data = json.loads(service.config_path.read_text(encoding="utf-8"))
    assert data["features"]["grocery_list"]["tier"] == "free"
    assert "name_ru" in data["features"]["grocery_list"]


# ----------------------------------------------------------------------
# API level: gated endpoints return HTTP 402 with paywall details
# ----------------------------------------------------------------------
@pytest.fixture
def api_client(tmp_path, monkeypatch):
    config_path = tmp_path / "paywall_config.json"
    shutil.copy(REAL_CONFIG, config_path)
    monkeypatch.setenv("PAYWALL_CONFIG_PATH", str(config_path))

    from fastapi.testclient import TestClient
    import app.main as main_module

    # Work on a temporary copy of the database so beta analytics stay clean
    db_copy = tmp_path / "api_test.db"
    shutil.copy(main_module.DB_PATH, db_copy)
    with sqlite3.connect(db_copy) as conn:
        conn.execute("DELETE FROM feature_usage_counters")
        conn.execute("DELETE FROM feature_access_events")
    monkeypatch.setattr(main_module, "DB_PATH", str(db_copy))

    test_service = EntitlementService(db_path=str(db_copy), config_path=str(config_path))
    monkeypatch.setattr(main_module, "entitlements", test_service)

    with TestClient(main_module.app) as client:
        yield client, test_service


def test_api_ai_scan_paywall_after_three(api_client):
    client, service = api_client
    service.set_mode("production")
    body = {"user_id": 1, "image_base64": "dGVzdA==", "dish_hint": "Avocado Toast"}
    for _ in range(3):
        assert client.post("/api/ai/scan-plate", json=body).status_code == 200
    blocked = client.post("/api/ai/scan-plate", json=body)
    assert blocked.status_code == 402
    assert blocked.json()["detail"]["reason"] == "free_limit_reached"


def test_api_fasting_advanced_locked_in_production(api_client):
    client, service = api_client
    service.set_mode("production")
    assert client.post("/api/fasting/1/start", json={"protocol_id": "16_8"}).status_code == 200
    assert client.post("/api/fasting/1/start", json={"protocol_id": "18_6"}).status_code == 402
    service.set_mode("beta_all_open")
    assert client.post("/api/fasting/1/start", json={"protocol_id": "18_6"}).status_code == 200


def test_api_admin_requires_token(api_client):
    client, _ = api_client
    assert client.get("/api/admin/paywall-config").status_code == 401
    ok = client.get("/api/admin/paywall-config", headers={"X-Admin-Token": "dev-local-token"})
    assert ok.status_code == 200


def test_api_admin_switches_feature(api_client):
    client, service = api_client
    headers = {"X-Admin-Token": "dev-local-token"}
    client.put("/api/admin/paywall-config/mode", json={"mode": "production"}, headers=headers)
    assert client.post("/api/ai/clinical-review", json={"user_id": 1, "weekly_summary": "x"}).status_code == 402
    client.put("/api/admin/paywall-config/features/doctor_llm", json={"tier": "free"}, headers=headers)
    assert client.post("/api/ai/clinical-review", json={"user_id": 1, "weekly_summary": "x"}).status_code == 200


def test_api_recipes_locked_flag(api_client):
    client, service = api_client
    service.set_mode("production")
    recipes = {r["id"]: r for r in client.get("/api/recipes?user_id=1").json()["recipes"]}
    assert recipes["rec_salmon_bowl"]["locked"] is True
    assert recipes["rec_quark_bowl"]["locked"] is False
