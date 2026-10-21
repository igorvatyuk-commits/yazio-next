"""
Review & Feedback Analysis Service for YAZIO-Next using TypeSafe AI (Jev System One model).

Provides lightning-fast, ultra-low-cost classification of user feedback:
- Cost: $0.042 / 1M input tokens, $0 output tokens
- Latency: ~300ms parallel decision pass
- Outputs: Probabilistic sentiment, bug classification, category routing, and urgency scoring.
"""

import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

TYPESAFE_API_URL = "https://api.typesafe.ai/v1/systemone"
DEFAULT_MODEL = "jev-latest"
FALLBACK_TYPESAFE_KEY = "apikey_224625f77dedba2c43ca8a17086bcaa4ed88_a5008c85729da33c3edb040c75269f3862f04fe23ed2e917a7f9717e9cca3c17"


def load_typesafe_api_key() -> Optional[str]:
    """Loads TYPESAFE_API_KEY from environment, backend/.env, or fallback."""
    key = os.environ.get("TYPESAFE_API_KEY")
    if key and key.strip():
        return key.strip()

    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("TYPESAFE_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            return val
        except Exception:
            pass
    return FALLBACK_TYPESAFE_KEY


class ReviewAnalysisResult(BaseModel):
    raw_text: str
    is_bug: bool
    bug_probability: float
    sentiment: str
    sentiment_confidence: float
    category: str
    category_confidence: float
    urgency_score: float
    urgency_level: str
    is_feature_request: bool
    feature_request_probability: float
    model_used: str
    input_tokens: int
    estimated_cost_usd: float


class ReviewAnalyzerService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or load_typesafe_api_key()

    def analyze_review(self, review_text: str) -> Dict[str, Any]:
        """
        Analyzes a single user review or tester feedback using TypeSafe AI Jev.
        """
        if not self.api_key:
            raise ValueError("TYPESAFE_API_KEY is not configured.")

        clean_text = review_text.strip()
        if not clean_text:
            raise ValueError("Review text cannot be empty.")

        payload = {
            "model": DEFAULT_MODEL,
            "state": clean_text,
            "questions": {
                "is_bug": {
                    "type": "noul",
                    "instructions": "Является ли этот отзыв сообщением об ошибке, зависании или сбое в работе приложения?"
                },
                "is_feature_request": {
                    "type": "noul",
                    "instructions": "Содержит ли этот отзыв предложение новой функции, улучшение или запрос на доработку?"
                },
                "sentiment": {
                    "type": "choice",
                    "instructions": "Какова общая тональность отзыва пользователя?",
                    "criteria": {
                        "positive": "Пользователь доволен, благодарит, хвалит работу приложения или скорость.",
                        "neutral": "Нейтральный вопрос, констатация факта или уточнение информации.",
                        "negative": "Недовольство, жалоба, критика, разочарование или раздражение."
                    }
                },
                "category": {
                    "type": "choice",
                    "instructions": "К какой функциональной категории относится данный отзыв?",
                    "criteria": {
                        "barcode_scanner": "Сканер штрихкодов, распознавание камерой, оптические ошибки, скорость поиска товара.",
                        "food_database": "База продуктов, калории, белки/жиры/углеводы, отсутствие товара в магазине.",
                        "ui_ux": "Интерфейс, удобство кнопок, темная тема, дизайн, навигация по экранам.",
                        "general": "Общее впечатление, благодарность, вопрос о подписке или общие вопросы."
                    }
                },
                "urgency": {
                    "type": "score",
                    "instructions": "Оцените степень критичности и срочности реагирования на данный отзыв.",
                    "criteria": [
                        "Низкая (пожелание, общая мысль или похвала)",
                        "Средняя (небольшое неудобство, но базовый сценарий работает)",
                        "Высокая (важная функция сбоит, частые повторные попытки)",
                        "Критическая (полный сбой, падение программы, блокировка работы)"
                    ]
                }
            }
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            TYPESAFE_API_URL,
            data=data_bytes,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "YAZIO-Next-Analyzer/1.0"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"TypeSafe AI HTTP {e.code}: {err_body}")
        except Exception as e:
            raise RuntimeError(f"TypeSafe AI request failed: {str(e)}")

        answers = resp_json.get("answers", {})
        usage = resp_json.get("usage", {})
        model_version = resp_json.get("model", DEFAULT_MODEL)

        # Parse answers
        is_bug_prob = answers.get("is_bug", {}).get("noul", 0.0)
        is_feature_prob = answers.get("is_feature_request", {}).get("noul", 0.0)
        
        sentiment_data = answers.get("sentiment", {})
        sentiment = sentiment_data.get("choice", "neutral")
        sentiment_conf = sentiment_data.get("confidence", 0.0)

        category_data = answers.get("category", {})
        category = category_data.get("choice", "general")
        category_conf = category_data.get("confidence", 0.0)

        urgency_data = answers.get("urgency", {})
        urgency_score = float(urgency_data.get("score", 0.0))
        legend = urgency_data.get("legend", {})
        rounded_idx = str(min(max(round(urgency_score), 0), 3))
        urgency_level = legend.get(rounded_idx, "Не определено")

        input_tokens = usage.get("input_tokens", 0)
        # Cost is $0.042 per 1,000,000 input tokens
        estimated_cost = (input_tokens / 1_000_000.0) * 0.042

        return {
            "raw_text": clean_text,
            "is_bug": is_bug_prob >= 0.5,
            "bug_probability": round(is_bug_prob, 3),
            "sentiment": sentiment,
            "sentiment_confidence": round(sentiment_conf, 3),
            "category": category,
            "category_confidence": round(category_conf, 3),
            "urgency_score": round(urgency_score, 2),
            "urgency_level": urgency_level,
            "is_feature_request": is_feature_prob >= 0.5,
            "feature_request_probability": round(is_feature_prob, 3),
            "model_used": model_version,
            "input_tokens": input_tokens,
            "estimated_cost_usd": round(estimated_cost, 7)
        }

    def batch_analyze(self, reviews: List[str]) -> List[Dict[str, Any]]:
        """Analyzes a batch of reviews sequentially or returns structured summary."""
        results = []
        for text in reviews:
            if text and text.strip():
                try:
                    res = self.analyze_review(text)
                    results.append(res)
                except Exception as e:
                    results.append({
                        "raw_text": text,
                        "error": str(e)
                    })
        return results
