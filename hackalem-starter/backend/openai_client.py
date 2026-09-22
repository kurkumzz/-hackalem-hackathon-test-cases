"""
Тонкая обёртка над OpenAI SDK. Всё общение с OpenAI API идёт ТОЛЬКО через эти
две функции — так что если на хакатоне придётся что-то поменять (модель,
ретраи, формат вызова), правишь в одном месте, а не по всему проекту.

chat_completion()       — обычный чат + (опционально) function calling.
structured_completion() — просишь модель вернуть данные строго по schema
                           (pydantic-модель) и сразу получаешь готовый python-объект,
                           без ручного json.loads() и надежды, что модель не ошиблась
                           с форматом.
"""
import time
from openai import OpenAI
from .config import settings
from .logging_utils import log_call

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class OpenAIError(Exception):
    pass


def chat_completion(messages: list[dict], tools: list[dict] | None = None, model: str | None = None):
    """
    Обёртка над client.chat.completions.create с повторными попытками и
    фолбэком на запасную модель.

    Порядок попыток: сначала основная модель MAX_RETRIES раз (с увеличивающейся
    паузой между попытками — 1с, 2с, 4с...), потом то же самое с запасной моделью.
    Если и это не сработало — кидаем OpenAIError с последней ошибкой внутри.
    """
    primary = model or settings.OPENAI_MODEL
    candidates = [primary]
    if settings.OPENAI_FALLBACK_MODEL and settings.OPENAI_FALLBACK_MODEL != primary:
        candidates.append(settings.OPENAI_FALLBACK_MODEL)

    last_error: Exception | None = None

    for candidate_model in candidates:
        for attempt in range(settings.MAX_RETRIES):
            request_payload = {"model": candidate_model, "messages": messages}
            if tools:
                request_payload["tools"] = tools
                request_payload["tool_choice"] = "auto"
            try:
                response = client.chat.completions.create(**request_payload)
                log_call(request=request_payload, response=response.model_dump(), error=None)
                return response
            except Exception as e:  # намеренно широкий except — хакатон, а не банк
                last_error = e
                log_call(request=request_payload, response=None, error=str(e))
                time.sleep(2 ** attempt)

    raise OpenAIError(f"Не удалось получить ответ от OpenAI после всех попыток: {last_error}")


def structured_completion(messages: list[dict], response_model, model: str | None = None):
    """
    response_model — класс pydantic.BaseModel, описывающий, что должна вернуть модель.

    Пример:
        class Idea(BaseModel):
            title: str
            description: str

        idea = structured_completion(
            messages=[{"role": "user", "content": "Придумай идею для трека Креативные индустрии"}],
            response_model=Idea,
        )
        print(idea.title)  # уже готовый python-объект, не строка с JSON
    """
    target_model = model or settings.OPENAI_MODEL
    request_payload = {"model": target_model, "messages": messages, "response_format": response_model}
    try:
        completion = client.beta.chat.completions.parse(**request_payload)
    except Exception as e:
        log_call(
            request={"model": target_model, "messages": messages, "response_format": response_model.__name__},
            response=None,
            error=str(e),
        )
        raise OpenAIError(f"Не удалось получить структурированный ответ: {e}")

    log_call(
        request={"model": target_model, "messages": messages, "response_format": response_model.__name__},
        response=completion.model_dump(),
        error=None,
    )
    return completion.choices[0].message.parsed
