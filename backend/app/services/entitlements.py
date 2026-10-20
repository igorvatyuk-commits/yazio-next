"""
Entitlement (feature access) service for YAZIO-Next.

Every paid or limited feature asks this service "may this user use feature X?"
instead of hardcoding `if user.is_free`. What is free / limited / PRO lives in
`app/config/paywall_config.json` and can be changed without an app release.

Modes:
- beta_all_open: everything is unlocked (closed beta), but every access is still
  logged so we can measure which features people actually use.
- production: tiers from the config are enforced.

Tiers:
- free:    always available.
- limited: `free_limit` uses (per `quota_key`), then PRO is required.
- pro:     only for PRO subscribers.
"""

import json
import os
import sqlite3
import tempfile
import threading
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "paywall_config.json"
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "yazio_next.db"

VALID_MODES = ("beta_all_open", "production")
VALID_TIERS = ("free", "limited", "pro")
PRO_PREMIUM_TYPES = ("pro_trial", "pro_annual", "pro_monthly")

_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS feature_usage_counters (
    user_id INTEGER NOT NULL,
    quota_key TEXT NOT NULL,
    used INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, quota_key)
);

CREATE TABLE IF NOT EXISTS feature_access_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    feature_key TEXT NOT NULL,
    allowed INTEGER NOT NULL,
    reason TEXT NOT NULL,
    mode TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_feature_events_feature
    ON feature_access_events(feature_key, reason);
"""


class UnknownFeatureError(KeyError):
    """Raised when a feature key is not defined in paywall_config.json."""


class InvalidConfigError(ValueError):
    """Raised when paywall_config.json contains invalid values."""


@dataclass
class AccessDecision:
    feature_key: str
    allowed: bool
    # beta_all_open | pro_subscriber | free_feature | within_free_limit
    # | free_limit_reached | pro_required
    reason: str
    tier: str
    mode: str
    free_limit: Optional[int] = None
    used: Optional[int] = None
    remaining: Optional[int] = None
    show_paywall: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EntitlementService:
    """Evaluates feature access from the remote paywall config and logs usage."""

    def __init__(self, db_path: Optional[str] = None, config_path: Optional[str] = None) -> None:
        self.db_path = Path(db_path or DEFAULT_DB_PATH)
        self.config_path = Path(
            config_path or os.environ.get("PAYWALL_CONFIG_PATH") or DEFAULT_CONFIG_PATH
        )
        self._lock = threading.Lock()
        self._config: Optional[Dict[str, Any]] = None
        self._config_mtime: Optional[float] = None
        self._ensure_tables()

    # ------------------------------------------------------------------
    # Database helpers
    # ------------------------------------------------------------------
    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables(self) -> None:
        with self._conn() as conn:
            conn.executescript(_TABLES_SQL)

    # ------------------------------------------------------------------
    # Config handling (hot reload on file change)
    # ------------------------------------------------------------------
    @staticmethod
    def _validate(cfg: Dict[str, Any]) -> None:
        if cfg.get("mode") not in VALID_MODES:
            raise InvalidConfigError(f"mode must be one of {VALID_MODES}, got {cfg.get('mode')!r}")
        features = cfg.get("features")
        if not isinstance(features, dict) or not features:
            raise InvalidConfigError("features must be a non-empty object")
        for key, feature in features.items():
            tier = feature.get("tier")
            if tier not in VALID_TIERS:
                raise InvalidConfigError(f"{key}: tier must be one of {VALID_TIERS}, got {tier!r}")
            if tier == "limited":
                limit = feature.get("free_limit")
                if not isinstance(limit, int) or limit < 0:
                    raise InvalidConfigError(f"{key}: limited tier requires integer free_limit >= 0")

    def get_config(self) -> Dict[str, Any]:
        with self._lock:
            mtime = self.config_path.stat().st_mtime
            if self._config is None or mtime != self._config_mtime:
                cfg = json.loads(self.config_path.read_text(encoding="utf-8"))
                self._validate(cfg)
                self._config = cfg
                self._config_mtime = mtime
            # Deep copy so callers cannot mutate the cached config
            return json.loads(json.dumps(self._config))

    def _write_config(self, cfg: Dict[str, Any]) -> Dict[str, Any]:
        self._validate(cfg)
        cfg["version"] = int(cfg.get("version", 0)) + 1
        cfg["updated_at"] = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        payload = json.dumps(cfg, ensure_ascii=False, indent=2) + "\n"

        # Atomic write: temp file in the same directory, then replace
        fd, tmp_path = tempfile.mkstemp(dir=str(self.config_path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(payload)
            os.replace(tmp_path, self.config_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        with self._lock:
            self._config = None
            self._config_mtime = None
        return self.get_config()

    def set_mode(self, mode: str) -> Dict[str, Any]:
        cfg = self.get_config()
        cfg["mode"] = mode
        return self._write_config(cfg)

    def update_feature(
        self,
        feature_key: str,
        tier: Optional[str] = None,
        free_limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        cfg = self.get_config()
        feature = cfg["features"].get(feature_key)
        if feature is None:
            raise UnknownFeatureError(feature_key)
        if tier is not None:
            feature["tier"] = tier
        if free_limit is not None:
            feature["free_limit"] = free_limit
        return self._write_config(cfg)

    # ------------------------------------------------------------------
    # Access evaluation
    # ------------------------------------------------------------------
    @staticmethod
    def _is_pro(conn: sqlite3.Connection, user_id: int) -> bool:
        try:
            row = conn.execute("SELECT premium_type FROM users WHERE id = ?", (user_id,)).fetchone()
        except sqlite3.OperationalError:
            return False
        return bool(row) and row["premium_type"] in PRO_PREMIUM_TYPES

    @staticmethod
    def _get_used(conn: sqlite3.Connection, user_id: int, quota_key: str) -> int:
        row = conn.execute(
            "SELECT used FROM feature_usage_counters WHERE user_id = ? AND quota_key = ?",
            (user_id, quota_key),
        ).fetchone()
        return int(row["used"]) if row else 0

    def check(
        self,
        user_id: int,
        feature_key: str,
        consume: bool = False,
        log_event: bool = True,
    ) -> AccessDecision:
        """
        Decide whether `user_id` may use `feature_key`.

        consume=True  -> counts one use against the feature's quota (for limited
                         features) when access is granted.
        log_event=True -> stores the decision for usage analytics.
        """
        cfg = self.get_config()
        feature = cfg["features"].get(feature_key)
        if feature is None:
            raise UnknownFeatureError(feature_key)

        mode = cfg["mode"]
        tier = feature["tier"]
        quota_key = feature.get("quota_key", feature_key)
        free_limit = feature.get("free_limit") if tier == "limited" else None

        with self._conn() as conn:
            used = self._get_used(conn, user_id, quota_key)

            if mode == "beta_all_open":
                allowed, reason = True, "beta_all_open"
            elif self._is_pro(conn, user_id):
                allowed, reason = True, "pro_subscriber"
            elif tier == "free":
                allowed, reason = True, "free_feature"
            elif tier == "limited":
                if used < free_limit:
                    allowed, reason = True, "within_free_limit"
                else:
                    allowed, reason = False, "free_limit_reached"
            else:
                allowed, reason = False, "pro_required"

            if allowed and consume:
                conn.execute(
                    """
                    INSERT INTO feature_usage_counters (user_id, quota_key, used, updated_at)
                    VALUES (?, ?, 1, CURRENT_TIMESTAMP)
                    ON CONFLICT(user_id, quota_key)
                    DO UPDATE SET used = used + 1, updated_at = CURRENT_TIMESTAMP
                    """,
                    (user_id, quota_key),
                )
                used += 1

            if log_event:
                conn.execute(
                    """
                    INSERT INTO feature_access_events (user_id, feature_key, allowed, reason, mode)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (user_id, feature_key, int(allowed), reason, mode),
                )
            conn.commit()

        remaining = max(0, free_limit - used) if free_limit is not None else None
        return AccessDecision(
            feature_key=feature_key,
            allowed=allowed,
            reason=reason,
            tier=tier,
            mode=mode,
            free_limit=free_limit,
            used=used if free_limit is not None else None,
            remaining=remaining,
            show_paywall=not allowed,
        )

    def snapshot(self, user_id: int) -> Dict[str, Any]:
        """Access state of every feature for one user (read-only, not logged)."""
        cfg = self.get_config()
        features: Dict[str, Any] = {}
        for key, feature in cfg["features"].items():
            decision = self.check(user_id, key, consume=False, log_event=False).to_dict()
            decision["name_ru"] = feature.get("name_ru", key)
            decision["name_de"] = feature.get("name_de", key)
            features[key] = decision
        return {
            "user_id": user_id,
            "mode": cfg["mode"],
            "config_version": cfg.get("version"),
            "features": features,
        }

    def usage_report(self) -> List[Dict[str, Any]]:
        """Aggregated feature usage for the beta analysis (most used first)."""
        cfg = self.get_config()
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT feature_key,
                       COUNT(*) AS total_events,
                       SUM(allowed) AS allowed_events,
                       SUM(1 - allowed) AS blocked_events,
                       COUNT(DISTINCT user_id) AS unique_users
                FROM feature_access_events
                GROUP BY feature_key
                ORDER BY total_events DESC
                """
            ).fetchall()
        report = []
        for r in rows:
            feature = cfg["features"].get(r["feature_key"], {})
            report.append({
                "feature_key": r["feature_key"],
                "name_ru": feature.get("name_ru", r["feature_key"]),
                "current_tier": feature.get("tier"),
                "total_events": r["total_events"],
                "allowed_events": r["allowed_events"],
                "blocked_events": r["blocked_events"],
                "unique_users": r["unique_users"],
            })
        return report
