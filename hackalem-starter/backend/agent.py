"""
Agent loop: модель отвечает либо готовым текстом, либо просьбой вызвать один
или несколько инструментов. Если это вызов инструмента — исполняем его руками
(в tools.py) и отдаём результат модели обратно, чтобы она сформировала
финальный ответ. Цикл повторяется, пока модель не выдаст обычный текстовый
ответ — либо пока не кончится лимит шагов MAX_STEPS (защита от бесконечного
цикла вызовов).

## Что менять, когда объявят кейс
1. SYSTEM_PROMPT — опиши задачу словами: кто пользователь, что нужно решить.
2. TOOLS_SCHEMA / TOOLS_IMPL — добавь функции под реальную задачу (в tools.py).
Остальной код (сам цикл) трогать обычно не нужно.
"""
import json
from . import db, tools
from .openai_client import chat_completion

SYSTEM_PROMPT = (
    "Ты — AI-ассистент хакатон-проекта HackAlem AI (трек «Креативные индустрии»). "
    "ЗАГЛУШКА: замени этот системный промпт на описание реальной задачи, когда "
    "объявят кейс. Отвечай по-русски, кратко и по делу."
)

# JSON-схемы инструментов в формате, который понимает OpenAI function calling.
# ВАЖНО: имена и параметры здесь должны совпадать с функциями из tools.py.
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "save_note",
            "description": "Сохранить заметку/идею в базу проекта",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Текст заметки"},
                    "tag": {"type": "string", "description": "Метка/категория, необязательно"},
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_notes",
            "description": "Найти сохранённые заметки по подстроке",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Что искать"},
                },
                "required": ["query"],
            },
        },
    },
]

TOOLS_IMPL = {
    "save_note": tools.save_note,
    "search_notes": tools.search_notes,
}

MAX_STEPS = 5


def run_agent(user_message: str, session_id: str = "default") -> str:
    history = db.get_history(session_id)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, *history, {"role": "user", "content": user_message}]

    db.save_message(session_id, "user", user_message)

    for _ in range(MAX_STEPS):
        response = chat_completion(messages=messages, tools=TOOLS_SCHEMA)
        msg = response.choices[0].message

        if msg.tool_calls:
            # Модель просит вызвать один или несколько инструментов.
            # Сначала кладём в историю само это "намерение" модели (обязательно
            # для OpenAI API — иначе следующий запрос будет некорректным).
            messages.append(
                {
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                        }
                        for tc in msg.tool_calls
                    ],
                }
            )
            # Затем реально исполняем каждый вызов и кладём результат в историю.
            for tc in msg.tool_calls:
                fn = TOOLS_IMPL.get(tc.function.name)
                args = json.loads(tc.function.arguments or "{}")
                result = fn(**args) if fn else {"error": f"неизвестный инструмент {tc.function.name}"}
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result, ensure_ascii=False, default=str),
                    }
                )
            continue  # спрашиваем модель ещё раз — теперь у неё есть результат инструмента

        # Обычный текстовый ответ, без вызова инструментов — это финал.
        reply = msg.content or ""
        db.save_message(session_id, "assistant", reply)
        return reply

    fallback = "Не удалось получить ответ за отведённое число шагов агента (возможно, зациклился на вызовах инструментов)."
    db.save_message(session_id, "assistant", fallback)
    return fallback
