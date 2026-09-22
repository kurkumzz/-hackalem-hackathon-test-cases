"""
Настройки проекта. Всё, что может поменяться между твоей машиной и машиной
тиммейта (ключи, модель) — читаем из .env, а не хардкодим в коде.

Как это работает:
  1. load_dotenv() подхватывает файл .env из корня проекта (если он есть).
  2. os.getenv("ИМЯ", "значение_по_умолчанию") читает переменную окружения.

Перед первым запуском: скопируй .env.example в .env и впиши туда свой
OPENAI_API_KEY (выдадут на хакатоне вместе с токенами от OpenAI).
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    # Основная модель. На хакатоне уточни у организаторов, какие модели
    # доступны по выданным токенам, и поменяй значение в .env — код трогать не надо.
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-5")
    # Запасная модель — если основная недоступна/упала, wrapper попробует эту.
    OPENAI_FALLBACK_MODEL: str = os.getenv("OPENAI_FALLBACK_MODEL", "gpt-4.1")
    # Сколько раз повторять попытку запроса к OpenAI при ошибке, прежде чем сдаться.
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))


settings = Settings()

if not settings.OPENAI_API_KEY:
    # Не бросаем исключение — даём проекту подняться (например, чтобы посмотреть
    # фронтенд или прогнать тесты), но громко предупреждаем в консоли.
    print("⚠️  OPENAI_API_KEY не задан. Скопируй .env.example в .env и впиши свой ключ.")
