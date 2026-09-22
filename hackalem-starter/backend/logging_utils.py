"""
Логирование каждого вызова OpenAI в logs/calls.jsonl.

Зачем это вообще нужно на хакатоне:
  - когда модель ведёт себя странно в 3 часа ночи, ты открываешь этот файл и
    видишь ТОЧНО, что было отправлено и что пришло в ответ — не гадаешь;
  - судьи иногда просят показать, как работает интеграция с API — файл с логом
    вызовов это готовое доказательство.

Формат: JSON Lines (один JSON-объект на строку) — можно открыть как обычный
текстовый файл или прочитать построчно скриптом.
"""
import json
import os
import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "calls.jsonl")


def log_call(request, response, error: str | None = None) -> None:
    os.makedirs(LOG_DIR, exist_ok=True)
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "request": request,
        "response": response,
        "error": error,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        # default=str — на случай если в объекте попадутся не-JSON-сериализуемые
        # типы (например, объекты pydantic/OpenAI SDK) — не упадём, а запишем как строку.
        f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
