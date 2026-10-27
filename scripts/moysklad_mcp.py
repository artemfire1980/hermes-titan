import os

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Загружаем токен из .env Hermes
load_dotenv("/mnt/ai-ssd/hermes/.env")
TOKEN = os.environ.get("MOYSKLAD_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept-Encoding": "gzip"}
BASE_URL = "https://api.moysklad.ru/api/remap/1.2"

mcp = FastMCP("MoySklad_Local")


@mcp.tool()
def search_counterparty(query: str) -> str:
    """Умный поиск контрагента по названию (ищет по первому слову, фильтрует по остальным)."""
    words = query.lower().split()
    if not words:
        return "Пустой запрос"

    # Ищем по первому слову (API требует хотя бы 3 символа)
    search_word = words[0]
    if len(search_word) < 3:
        return "Слишком короткое слово для поиска"

    url = f"{BASE_URL}/entity/counterparty?filter=name~{search_word}&limit=50"
    r = requests.get(url, headers=HEADERS, timeout=15)

    if r.status_code != 200:
        return f"Ошибка API: {r.status_code}"

    rows = r.json().get("rows", [])
    if not rows:
        return "Ничего не найдено"

    # Фильтруем: если в запросе было больше 1 слова, проверяем их наличие
    results = []
    for row in rows:
        name = row["name"]
        if all(w in name.lower() for w in words):
            results.append(name)

    if not results:
        return "Точных совпадений нет (найдены случайные). Можно создавать."

    return "Найдены возможные дубли: " + ", ".join(results)


@mcp.tool()
def create_counterparty(
    name: str, phone: str, email: str, manager_name: str = "Хапанков В."
) -> str:
    """
    Создает контрагента с контактным лицом, тегами (глазури + менеджер) и статусом 'в разработке'.
    """
    # 1. Получаем ID статуса "в разработке"
    state_url = f"{BASE_URL}/entity/counterparty/metadata/states"
    r = requests.get(state_url, headers=HEADERS)
    state_id = None
    if r.status_code == 200:
        for s in r.json().get("rows", []):
            if "разработке" in s["name"].lower():
                state_id = s["id"]
                break

    # 2. Формируем тело запроса
    payload = {
        "name": name,
        "actualAddress": "Россия",
        "tags": ["глазури", manager_name.lower()],
        "contactpersons": [{"name": "Контактное лицо", "phone": phone, "email": email}],
    }

    if state_id:
        payload["state"] = {
            "meta": {
                "href": f"{BASE_URL}/entity/counterparty/metadata/states/{state_id}",
                "type": "state",
                "mediaType": "application/json",
            }
        }

    # 3. Отправляем POST запрос
    post_url = f"{BASE_URL}/entity/counterparty"
    r = requests.post(post_url, headers=HEADERS, json=payload)

    if r.status_code == 200:
        return f"✅ Контрагент '{name}' успешно создан! ID: {r.json().get('id')}"
    else:
        return f"❌ Ошибка создания: {r.status_code} - {r.text}"


if __name__ == "__main__":
    mcp.run()
