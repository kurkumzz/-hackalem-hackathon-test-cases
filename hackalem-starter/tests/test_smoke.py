"""
Дымовой тест: проверяет, что приложение вообще поднимается и роуты отвечают —
БЕЗ обращения к настоящему OpenAI API (чтобы не тратить токены/не требовать ключ).

Запуск: python -m pytest tests/  (или просто: python tests/test_smoke.py)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_history_empty_for_new_session():
    response = client.get("/api/history/never-used-session-id")
    assert response.status_code == 200
    assert response.json() == []


def test_frontend_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "HackAlem" in response.text


if __name__ == "__main__":
    test_health()
    test_history_empty_for_new_session()
    test_frontend_served()
    print("Смоук-тесты прошли ✅")
