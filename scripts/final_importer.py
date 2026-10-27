import difflib
import logging
import os
import re
import sys
import time

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv("/mnt/ai-ssd/hermes/.env")
TOKEN = os.getenv("MOYSKLAD_TOKEN_HAPANKOV")
if not TOKEN:
    sys.exit("ОШИБКА: переменная окружения MOYSKLAD_TOKEN_HAPANKOV не задана в .env")

BASE_URL = "https://api.moysklad.ru/api/remap/1.2"
EXCEL_PATH = "/mnt/ai-ssd/hermes/cache/пример1.xls"
DB_NAMES_PATH = "/mnt/ai-ssd/hermes/cache/db_names.txt"
REPORT_PATH = "/mnt/ai-ssd/hermes/cache/import_report.csv"
DRY_RUN = False  # True - только проверка, False - создание
TAGS = ["глазури", "хапанков"]
STATE_ID = "21798e98-bca2-11e3-47b6-002590a28eca"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("importer")

HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept-Encoding": "gzip"}

ORG_FORMS = {"ооо", "ао", "зао", "пао", "оао", "ип", "ltd", "llc", "inc", "corp"}
GENERIC_WORDS = {
    "кондитер",
    "кондитерская",
    "десерт",
    "стандарт",
    "фабрика",
    "завод",
    "групп",
    "группа",
    "group",
    "торговый",
    "торг",
    "дом",
    "продукт",
    "компания",
    "ооо",
    "оао",
    "зао",
    "ао",
    "пао",
    "ип",
    "ltd",
    "llc",
    "inc",
    "corp",
    "cf",
    "th",
    "tm",
    "ie",
    "cdl",
    "сдл",
    "тд",
    "тк",
    "гк",
    "пк",
    "кф",
}
VOWELS = set("аеёиоуыэюя")

DIGRAPHS = [
    ("shch", "щ"),
    ("sch", "щ"),
    ("ch", "ч"),
    ("sh", "ш"),
    ("zh", "ж"),
    ("kh", "х"),
    ("yo", "ё"),
    ("yu", "ю"),
    ("ya", "я"),
    ("ts", "ц"),
]
SINGLE_LETTERS = {
    "a": "а",
    "b": "б",
    "v": "в",
    "w": "в",
    "g": "г",
    "d": "д",
    "z": "з",
    "i": "и",
    "j": "й",
    "k": "к",
    "l": "л",
    "m": "м",
    "n": "н",
    "o": "о",
    "p": "п",
    "r": "р",
    "s": "с",
    "t": "т",
    "u": "у",
    "f": "ф",
    "h": "х",
    "q": "к",
    "x": "кс",
}


def _translit_word(word: str) -> str:
    w = word.lower()
    for lat, cyr in DIGRAPHS:
        w = w.replace(lat, cyr)
    out = []
    chars = list(w)
    for idx, ch in enumerate(chars):
        prev_out = out[-1] if out else ""
        next_in = chars[idx + 1] if idx + 1 < len(chars) else ""
        is_last = idx == len(chars) - 1
        if ch == "c":
            out.append("с" if next_in in ("e", "i", "y") else "к")
        elif ch == "e":
            out.append("э" if not prev_out or (prev_out in VOWELS and not is_last) else "е")
        elif ch == "y":
            if is_last:
                out.extend(["и", "й"] if prev_out == "и" else ["ы", "й"])
            elif prev_out in VOWELS:
                out.append("й")
            else:
                out.append("ы")
        elif ch in SINGLE_LETTERS:
            out.append(SINGLE_LETTERS[ch])
        else:
            out.append(ch)
    return "".join(out)


def transliterate(text: str) -> str:
    if not text:
        return ""
    if re.search(r"[а-яё]", text, re.IGNORECASE):
        return text.strip()
    return " ".join(_translit_word(w) for w in text.split())


RE_RUSSIAN_NAME = re.compile(
    r"(?:ООО|ОАО|ЗАО|ПАО|АО|ИП)\s+(?:(?:ТД|ТК|ГК|ПК|ПКФ|ТС|ТМ|НПК|ООО)\s+)?(?:([\"«])([А-ЯЁA-Z0-9][А-ЯЁA-Z0-9\-\.\s]{2,60})(?:[\"»])|([А-ЯЁ0-9][А-ЯЁ0-9\-\s]{3,60}))",
    re.UNICODE,
)
RE_NAME_TAIL = re.compile(r"\s+(?:ИНН|ОГРН|ОГРНИП|ОКПО)\b|^\s+|\s+$|[\-—]+$")


def extract_russian_name(description: str) -> str | None:
    if not description or not re.search(r"[а-яё]", description, re.IGNORECASE):
        return None
    for m in RE_RUSSIAN_NAME.finditer(description):
        candidate = (m.group(2) or m.group(3) or "").strip()
        candidate = RE_NAME_TAIL.split(candidate)[0].strip(" \t-—,.;:")
        letters = [c for c in candidate if c.isalpha()]
        if len(letters) < 4:
            continue
        if m.group(1):
            return candidate
        if sum(1 for c in letters if c.isupper()) / len(letters) >= 0.8:
            return candidate
    return None


def normalize_words(name: str) -> list[str]:
    if not name:
        return []
    cleaned = re.sub(r"[\"«»()|/\\,;:.!?\[\]#№]", " ", name.lower().replace("ё", "е"))
    return list(
        dict.fromkeys(
            tok
            for tok in cleaned.split()
            if tok not in ORG_FORMS and tok not in GENERIC_WORDS and len(tok) >= 2
        )
    )


def _all_word_forms(name: str) -> list[str]:
    words = normalize_words(name)
    words += [w for w in normalize_words(transliterate(name)) if w not in words]
    return words


def phonetic(word: str) -> str:
    return "".join(c for c in word if c not in VOWELS)


def words_match(w1: str, w2: str) -> bool:
    if w1 == w2:
        return True
    t1, t2 = transliterate(w1), transliterate(w2)
    if t1 == t2:
        return True
    if min(len(w1), len(w2)) < 6:
        return False
    if phonetic(w1) == phonetic(w2) or phonetic(t1) == phonetic(t2):
        return True
    return (
        difflib.SequenceMatcher(None, w1, w2).ratio() >= 0.85
        or difflib.SequenceMatcher(None, t1, t2).ratio() >= 0.85
    )


def is_duplicate(query_name: str, candidate_name: str) -> bool:
    q_words = _all_word_forms(query_name)
    c_words = _all_word_forms(candidate_name)
    if not q_words or not c_words:
        return False
    return all(any(words_match(q, c) for c in c_words) for q in q_words)


def pick_search_word(name: str) -> str | None:
    words = _all_word_forms(name)
    return max(words, key=len) if words else None


def api_request(method: str, url: str, **kwargs):
    for attempt in range(1, 4):
        try:
            resp = requests.request(method, url, headers=HEADERS, timeout=30, **kwargs)
        except requests.RequestException as e:
            log.error("Сетевая ошибка: %s", e)
            time.sleep(2 * attempt)
            continue
        if resp.status_code in (429, 503):
            time.sleep(2**attempt)
            continue
        return resp
    return None


def search_counterparties(word: str) -> list[dict]:
    resp = api_request(
        "GET", f"{BASE_URL}/entity/counterparty", params={"filter": f"name~{word}", "limit": 100}
    )
    return resp.json().get("rows", []) if resp and resp.status_code == 200 else []


def create_counterparty(name: str, phone: str, email: str, website: str = "") -> dict | None:
    payload = {
        "name": name,
        "actualAddress": "Россия",
        "tags": TAGS,
        "state": {
            "meta": {
                "href": f"{BASE_URL}/entity/counterparty/metadata/states/{STATE_ID}",
                "type": "state",
            }
        },
    }
    if website:
        payload["website"] = website

    resp = api_request("POST", f"{BASE_URL}/entity/counterparty", json=payload)
    if resp and resp.status_code in (200, 201):
        entity = resp.json()
        # Создаем контактное лицо только если есть телефон или email
        if phone or email:
            cp = {"name": "Контактное лицо"}
            if phone:
                cp["phone"] = re.sub(r"\s", "", phone)
            if email:
                cp["email"] = email.strip()
            api_request(
                "POST", f"{BASE_URL}/entity/counterparty/{entity['id']}/contactpersons", json=cp
            )
        return entity
    return None


def create_note(counterparty_id: str, text: str):
    """Создает заметку (событие) в карточке контрагента."""
    if not text:
        return
    payload = {"description": text, "eventType": "note"}
    # В API МойСклад заметки создаются через событие (event)
    url = f"{BASE_URL}/entity/counterparty/{counterparty_id}/events"
    api_request("POST", url, json=payload)


def process_row(row: pd.Series) -> dict:
    raw_name = str(row.get(1, "") or "").strip()
    phone = str(row.get(3, "") or "").strip()
    email = str(row.get(4, "") or "").strip()
    website = str(row.get(5, "") or "").strip()
    description = str(row.get(6, "") or "").strip()
    if not raw_name:
        return {"excel_name": "", "result": "skipped_empty", "detail": "пустое название"}

    russian_name = extract_russian_name(description)
    search_name = russian_name if russian_name else transliterate(raw_name)
    word = pick_search_word(search_name)

    if not word:
        return {
            "excel_name": raw_name,
            "result": "skipped_no_word",
            "detail": "нет уникального слова",
        }

    time.sleep(0.25)
    candidates = search_counterparties(word)

    for cand in candidates:
        if is_duplicate(search_name, cand.get("name", "")):
            return {"excel_name": raw_name, "result": "duplicate", "detail": cand.get("name", "")}

    final_name = russian_name if russian_name else transliterate(raw_name)

    if DRY_RUN:
        return {
            "excel_name": raw_name,
            "result": "would_create",
            "detail": f"БЫ СОЗДАН: {final_name}",
        }

    time.sleep(0.25)
    entity = create_counterparty(final_name, phone, email, website)

    if entity:
        # Если есть описание - создаем заметку
        if description and len(description) > 5:
            time.sleep(0.2)  # небольшая пауза
            create_note(entity.get("id"), description)

        return {"excel_name": raw_name, "result": "created", "detail": entity.get("id", "")}
    return {"excel_name": raw_name, "result": "error", "detail": "ошибка создания"}


def main():
    if not os.path.exists(EXCEL_PATH):
        sys.exit(f"Файл {EXCEL_PATH} не найден")
    df = pd.read_excel(EXCEL_PATH, header=None, dtype=str).fillna("")
    log.info("Строк в Excel: %s", len(df))

    results = []
    created_count = 0
    for i in range(len(df)):
        res = process_row(df.iloc[i])
        results.append(res)
        if res["result"] == "created":
            created_count += 1
            if created_count >= 10:  # Останавливаемся после 10 созданных
                log.info("Достигнут лимит в 10 созданных компаний. Остановка.")
                break

    created = [r for r in results if r["result"] in ("created", "would_create")]
    skipped = [r for r in results if r["result"] == "duplicate"]
    errors = [r for r in results if r["result"] not in ("created", "duplicate", "would_create")]

    log.info("=" * 60)
    if DRY_RUN:
        log.info("РЕЖИМ ПРОВЕРКИ (DRY RUN):")
    log.info(
        "ИТОГО: создано/будет создано %s | пропущено дублей %s | ошибок/пропусков %s",
        len(created),
        len(skipped),
        len(errors),
    )
    for r in skipped:
        log.info("  ДУБЛЬ: %-35s -> %s", r["excel_name"], r["detail"])

    pd.DataFrame(results).to_csv(REPORT_PATH, index=False, encoding="utf-8-sig")
    log.info("Отчет сохранен: %s", REPORT_PATH)


if __name__ == "__main__":
    main()
