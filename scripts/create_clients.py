import os
import re
import sys
from collections.abc import Iterable
from difflib import SequenceMatcher

import requests
from dotenv import load_dotenv

load_dotenv("/mnt/ai-ssd/hermes/.env")

TOKEN_SEARCH = os.getenv("MOYSKLAD_TOKEN", "")
TOKEN_CREATE = os.getenv("MOYSKLAD_TOKEN_HAPANKOV", "")

API_URL = "https://api.moysklad.ru/api/remap/1.2/entity/counterparty"
HEADERS_SEARCH = {"Authorization": f"Bearer {TOKEN_SEARCH}", "Accept-Encoding": "gzip"}
HEADERS_CREATE = {"Authorization": f"Bearer {TOKEN_CREATE}", "Accept-Encoding": "gzip"}

PREFIX_LEN = 4
FUZZY_THRESHOLD = 0.85
MAX_EXTRA_TOKENS = 1
PAGE_LIMIT = 1000
MAX_PAGES = 5

STATE_ID_DEVELOPMENT = "21798e98-bca2-11e3-47b6-002590a28eca"

LEGAL_FORMS = {
    "ооо",
    "оао",
    "зао",
    "пао",
    "ао",
    "ип",
    "чп",
    "тоо",
    "уп",
    "оо",
    "зат",
    "ltd",
    "llc",
    "llp",
    "inc",
    "corp",
    "co",
    "gmbh",
    "ag",
    "sa",
    "sarl",
    "srl",
    "spa",
    "bv",
    "nv",
    "oy",
    "ab",
    "as",
    "jsc",
    "ojsc",
    "pjsc",
    "cjsc",
    "ie",
    "eg",
    "sp",
    "zoo",
    "plc",
    "limited",
    "company",
}

# --- Транслитерация для поиска и создания ---
_CYR_TO_LAT = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "e",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "sch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
}

_LAT_TO_CYR = [
    ("shch", "щ"),
    ("sch", "щ"),
    ("sh", "ш"),
    ("ch", "ч"),
    ("zh", "ж"),
    ("kh", "х"),
    ("ts", "ц"),
    ("yu", "ю"),
    ("ya", "я"),
    ("yo", "е"),
    ("ye", "е"),
    ("ou", "у"),
    ("oo", "у"),
    ("ph", "ф"),
    ("ck", "к"),
    ("ee", "и"),
    ("a", "а"),
    ("b", "б"),
    ("c", "к"),
    ("d", "д"),
    ("e", "е"),
    ("f", "ф"),
    ("g", "г"),
    ("h", "х"),
    ("i", "и"),
    ("j", "дж"),
    ("k", "к"),
    ("l", "л"),
    ("m", "м"),
    ("n", "н"),
    ("o", "о"),
    ("p", "п"),
    ("q", "к"),
    ("r", "р"),
    ("s", "с"),
    ("t", "т"),
    ("u", "у"),
    ("v", "в"),
    ("w", "в"),
    ("x", "кс"),
    ("y", "и"),
    ("z", "з"),
]


def _is_cyrillic(text: str) -> bool:
    return bool(re.search(r"[а-яё]", text))


def _cyr_to_lat(text: str) -> str:
    return "".join(_CYR_TO_LAT.get(ch, ch) for ch in text)


def _lat_to_cyr(text: str) -> str:
    out, i = [], 0
    while i < len(text):
        for lat, cyr in _LAT_TO_CYR:
            if text.startswith(lat, i):
                out.append(cyr)
                i += len(lat)
                break
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def transliterate_to_cyrillic(name: str) -> str:
    """Переводит название в кириллицу (для соблюдения закона)."""
    # Если уже на кириллице - оставляем как есть
    if _is_cyrillic(name):
        return name

    # Иначе переводим по словам
    words = name.split()
    result = []
    for w in words:
        # Если слово содержит латиницу, транслитерируем
        if re.search(r"[a-z]", w, re.IGNORECASE):
            result.append(_lat_to_cyr(w.lower()).capitalize())
        else:
            result.append(w)
    return " ".join(result)


def _tokens(name: str) -> list[str]:
    s = name.lower().replace("ё", "е").replace(".", "")
    words = re.findall(r"[^\W_]+", s)
    meaningful = [w for w in words if w not in LEGAL_FORMS]
    return meaningful or words


def _phonetic_key(token: str) -> str:
    s = _cyr_to_lat(token.lower())
    for src, dst in (
        ("shch", "$"),
        ("sch", "$"),
        ("sh", "$"),
        ("ch", "#"),
        ("zh", "j"),
        ("kh", "h"),
        ("ts", "%"),
        ("tz", "%"),
        ("ph", "f"),
        ("ck", "k"),
        ("c", "k"),
        ("q", "k"),
        ("x", "ks"),
        ("w", "v"),
    ):
        s = s.replace(src, dst)
    skeleton = re.sub(r"[aeiouy]", "", s)
    skeleton = re.sub(r"(.)\1+", r"\1", skeleton)
    return skeleton or s


def _tokens_match(key_a: str, key_b: str) -> bool:
    if key_a == key_b:
        return True
    if min(len(key_a), len(key_b)) >= 4:
        return SequenceMatcher(None, key_a, key_b).ratio() >= FUZZY_THRESHOLD
    return False


def _is_same_company(query: str, candidate: str) -> bool:
    q_keys = [_phonetic_key(t) for t in _tokens(query)]
    c_keys = [_phonetic_key(t) for t in _tokens(candidate)]
    if not q_keys or not c_keys:
        return False
    used: set[int] = set()
    for qk in q_keys:
        for idx, ck in enumerate(c_keys):
            if idx not in used and _tokens_match(qk, ck):
                used.add(idx)
                break
        else:
            return False
    return (len(c_keys) - len(q_keys)) <= MAX_EXTRA_TOKENS


def _search_variants(token: str) -> set[str]:
    variants = {token}
    variants.add(_cyr_to_lat(token) if _is_cyrillic(token) else _lat_to_cyr(token))
    for v in variants:
        if len(v) > PREFIX_LEN:
            variants.add(v[:PREFIX_LEN])
    return {v for v in variants if len(v) >= 3}


def _fetch_names(substring: str) -> Iterable[str]:
    offset = 0
    for _ in range(MAX_PAGES):
        params = {"filter": f"name~{substring}", "limit": PAGE_LIMIT, "offset": offset}
        try:
            resp = requests.get(API_URL, headers=HEADERS_SEARCH, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            rows = data.get("rows", [])
            for row in rows:
                yield row.get("name", "")
            offset += len(rows)
            if not rows or offset >= data.get("meta", {}).get("size", 0):
                return
        except Exception:
            return


def search_counterparty(name: str) -> list[str]:
    # 1. Ищем по оригиналу (латиница)
    tokens_orig = _tokens(name)
    # 2. Ищем по транслиту (кириллица)
    name_cyr = transliterate_to_cyrillic(name)
    tokens_cyr = _tokens(name_cyr)

    candidates: set[str] = set()
    for token in tokens_orig + tokens_cyr:
        for variant in _search_variants(token):
            candidates.update(_fetch_names(variant))

    # Сравниваем кандидатов и с оригиналом, и с кириллическим названием
    results = []
    for c in candidates:
        if c and (_is_same_company(name, c) or _is_same_company(name_cyr, c)):
            results.append(c)
    return sorted(set(results))


def create_counterparty(name, phone, email, manager_name="хапанков"):
    # Транслитерируем имя в кириллицу для закона
    cyr_name = transliterate_to_cyrillic(name)

    payload = {
        "name": cyr_name,  # Используем кириллицу!
        "actualAddress": "Россия",
        "tags": ["глазури", manager_name],
        "contactpersons": [{"name": "Контактное лицо", "phone": phone, "email": email}],
        "state": {
            "meta": {
                "href": f"https://api.moysklad.ru/api/remap/1.2/entity/counterparty/metadata/states/{STATE_ID_DEVELOPMENT}",
                "type": "state",
                "mediaType": "application/json",
            }
        },
    }
    r = requests.post(API_URL, headers=HEADERS_CREATE, json=payload)
    if r.status_code == 200:
        return True, r.json().get("id"), cyr_name
    return False, f"{r.status_code} - {r.text}", cyr_name


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python3 create_clients.py [search|create] [аргументы]")
        sys.exit(0)

    action = sys.argv[1]
    if action == "search":
        name = " ".join(sys.argv[2:])
        res = search_counterparty(name)
        if res:
            print(f"⚠️ Найдены совпадения ({len(res)}):")
            for r in res:
                print(f"  - {r}")
        else:
            print("✅ Дублей нет — можно создавать.")
    elif action == "create":
        ok, msg, cyr = create_counterparty(sys.argv[2], sys.argv[3], sys.argv[4])
        if ok:
            print(f"✅ Успешно создан! ID: {msg}")
            print(f"📝 Название в базе: {cyr}")
        else:
            print(f"❌ Ошибка: {msg}")
