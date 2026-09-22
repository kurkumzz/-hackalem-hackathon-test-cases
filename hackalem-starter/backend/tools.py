"""
"Инструменты" — обычные python-функции, которые модель может попросить вызвать
(function calling). Модель сама не трогает базу данных и вообще ничего не
исполняет — она только говорит "вызови save_note с такими-то аргументами",
а код (agent.py) реально это делает и отдаёт результат обратно модели.

Сейчас здесь заглушка (заметки в SQLite) — она нужна, чтобы вся цепочка
"модель -> вызов функции -> результат -> ответ" реально работала и её можно
было проверить ДО того, как объявят кейс. Когда кейс объявят — либо допишешь
сюда новые функции (например, generate_content, translate_text,
find_similar_assets), либо заменишь эти на нужные под задачу. Схему
инструментов для OpenAI (JSON) при этом надо будет обновить в agent.py —
она должна совпадать с сигнатурой функции здесь.
"""
from . import db


def save_note(text: str, tag: str = "general") -> dict:
    """Сохранить текстовую заметку/идею в базу проекта."""
    note_id = db.add_item(item_type="note", data={"text": text, "tag": tag})
    return {"status": "ok", "id": note_id}


def search_notes(query: str) -> list[dict]:
    """Найти сохранённые заметки, содержащие подстроку query (без учёта регистра)."""
    items = db.list_items(item_type="note")
    query_lower = query.lower()
    return [item for item in items if query_lower in item["data"].get("text", "").lower()]
