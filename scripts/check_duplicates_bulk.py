import os
import re
from difflib import SequenceMatcher

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv("/mnt/ai-ssd/hermes/.env")
TOKEN_SEARCH = os.getenv("MOYSKLAD_TOKEN", "")
API_URL = "https://api.moysklad.ru/api/remap/1.2/entity/counterparty"
HEADERS = {"Authorization": f"Bearer {TOKEN_SEARCH}", "Accept-Encoding": "gzip"}

# --- Настройки ---
FUZZY_THRESHOLD = 0.80
MAX_EXTRA_WORDS = 0
PREFIX_LEN = 4

# Слова, которые есть у сотен компаний (не считаем их совпадением)
GENERIC_WORDS = {
    "кондитер",
    "кондитерская",
    "кондитерский",
    "десерт",
    "десерты",
    "dessert",
    "стандарт",
    "standard",
    "фабрика",
    "factory",
    "завод",
    "комбинат",
    "групп",
    "группа",
    "group",
    "торговый",
    "торг",
    "trade",
    "дом",
    "house",
    "продукт",
    "продукты",
    "product",
    "food",
    "фуд",
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
}

# --- Транслитерация (латиница <-> кириллица) ---
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


def _is_cyr(text: str) -> bool:
    return bool(re.search(r"[а-яё]", text.lower()))


def _cyr_to_lat(text: str) -> str:
    return "".join(_CYR_TO_LAT.get(ch, ch) for ch in text.lower())


def _lat_to_cyr(text: str) -> str:
    text, out, i = text.lower(), [], 0
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
    if _is_cyr(name):
        return name
    return " ".join(
        _lat_to_cyr(w.lower()).capitalize() if re.search(r"[a-z]", w, re.IGNORECASE) else w
        for w in name.split()
    )


def _phonetic_key(token: str) -> str:
    s = _cyr_to_lat(token)
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
    unified = re.sub(r"(.)\1+", r"\1", s)

    # Если слово короткое (меньше 6 букв), не выбрасываем гласные!
    if len(unified) < 6:
        return unified

    skeleton = re.sub(r"[aeiouy]", "", unified)
    return skeleton if len(skeleton) >= 3 else unified


def _tokens(name: str) -> list[str]:
    s = name.lower().replace("ё", "е").replace(".", "")
    words = re.findall(r"[^\W_]+", s)
    meaningful = [
        w
        for w in words
        if w not in {"ооо", "оао", "зао", "ао", "пао", "ип", "ltd", "llc", "inc", "corp"}
    ]
    return meaningful or words


def _significant_keys(name: str) -> list[str]:
    keys = [_phonetic_key(t) for t in _tokens(name)]
    return [k for k in keys if not any(_phonetic_key(w) == k for w in GENERIC_WORDS)] or keys


def is_duplicate(query_name: str, candidate_name: str) -> bool:
    q_keys = _significant_keys(query_name)
    c_keys = _significant_keys(candidate_name)
    if not q_keys or not c_keys:
        return False
    free = list(c_keys)
    for qk in q_keys:
        match_found = False
        for i, ck in enumerate(free):
            # Точное совпадение
            if (
                qk == ck
                or len(qk) >= 6
                and len(ck) >= 6
                and SequenceMatcher(None, qk, ck).ratio() >= FUZZY_THRESHOLD
            ):
                free.pop(i)
                match_found = True
                break
        if not match_found:
            return False
    return len(free) <= MAX_EXTRA_WORDS


# --- Парсер русского названия (из промта) ---
_LEGAL_RU = "ФГУП|ООО|ОАО|ЗАО|ПАО|ОДО|ТОВ|ФОП|ТОО|НКО|АНО|МУП|ГУП|ИП|ЧП|УП|АО"
_Q_OPEN, _Q_CLOSE = '«"“„', '»"”“'
_L = "А-Яа-яЁёA-Za-z"
_JUNK_FIRST_WORDS = {
    "стенд",
    "павильон",
    "зал",
    "контакты",
    "контакт",
    "адрес",
    "телефон",
    "тел",
    "сайт",
    "выставка",
    "экспонент",
    "каталог",
    "описание",
    "stand",
    "hall",
}
_ADDRESS_MARKERS = {"г", "ул", "д", "тел", "инн", "огрн", "адрес", "обл", "область", "район"}

_FORM_RE = re.compile(rf"(?<![{_L}])(?:{_LEGAL_RU})(?![{_L}])")
_QUOTED_RE = re.compile(rf"(?<![{_L}])(?:{_LEGAL_RU})\s*[{_Q_OPEN}]\s*(.{{2,80}}?)\s*[{_Q_CLOSE}]")
_LEAD_FORM_RE = re.compile(rf"^[\s,;–—-]*(?:{_LEGAL_RU})(?![{_L}])")
_CUT_RE = re.compile(r"[,;|:()]|\s[-–—]\s|\.{2,}|…")


def _clean(s: str) -> str:
    s = re.sub(rf"[{_Q_OPEN}{_Q_CLOSE}]", "", s)
    return re.sub(r"\s+", " ", s).strip(" .,;:-–—")


def _is_valid_name(s: str) -> bool:
    if not s:
        return False
    if len(re.findall(rf"[{_L}]", s)) < 3:
        return False
    if sum(ch.isdigit() for ch in s) / len(s) > 0.3:
        return False
    if re.search(r"[@|/:]|www|http", s.lower()):
        return False
    words = re.findall(r"[^\W_]+", s.lower())
    return bool(words) and len(words) <= 5 and words[0] not in _JUNK_FIRST_WORDS


def _name_after_form(tail: str) -> str | None:
    seg = _CUT_RE.split(tail[:80], 1)[0].strip()
    if not seg or seg[0] in _Q_OPEN:
        return None
    words = seg.split()
    for i, w in enumerate(words):
        if w.lower().strip(".") in _ADDRESS_MARKERS:
            words = words[:i]
            break
    if not words or len(words) > 4 or not all(w[0].isupper() for w in words):
        return None
    name = _clean(" ".join(words))
    return name if _is_valid_name(name) else None


def extract_russian_name(description: str) -> str | None:
    if not description or not isinstance(description, str):
        return None
    text = re.sub(r"[\r\n]+", " | ", description)
    text = re.sub(r"\s+", " ", text).strip()
    for m in _QUOTED_RE.finditer(text):
        name = _clean(m.group(1))
        if _is_valid_name(name):
            return name
    for m in _FORM_RE.finditer(text):
        name = _name_after_form(text[m.end() :])
        if name:
            return name
    first = _CUT_RE.split(text, 1)[0].strip()
    rest = text[len(first) :]
    if first and not _FORM_RE.match(first):
        if _LEAD_FORM_RE.match(rest) or first.isupper():
            name = _clean(first)
            if _is_valid_name(name):
                return name
    return None


# --- Поиск в API ---
def search_terms(name: str, prefix_len: int = 4, max_words: int = 2) -> list[str]:
    tokens = _tokens(name)
    words = [
        t for t in tokens if not any(_phonetic_key(w) == _phonetic_key(t) for w in GENERIC_WORDS)
    ] or tokens
    words = sorted(set(words), key=len, reverse=True)[:max_words]
    terms = []
    for w in words:
        other = _cyr_to_lat(w) if _is_cyr(w) else _lat_to_cyr(w)
        for variant in (w, other):
            term = variant[:prefix_len]
            if len(term) >= 3 and term not in terms:
                terms.append(term)
    return terms


def _fetch_names(substring: str) -> list[str]:
    try:
        resp = requests.get(
            API_URL,
            headers=HEADERS,
            params={"filter": f"name~{substring}", "limit": 100},
            timeout=30,
        )
        resp.raise_for_status()
        return [row.get("name", "") for row in resp.json().get("rows", [])]
    except Exception:
        return []


def find_duplicates(latin_name: str, description: str) -> list[str]:
    rus = extract_russian_name(description)
    names = [n for n in (latin_name, rus) if n]
    candidates = set()
    for n in names:
        for term in search_terms(n):
            candidates.update(_fetch_names(term))
    return sorted(c for c in candidates if any(is_duplicate(n, c) for n in names))


if __name__ == "__main__":
    file_path = "/mnt/ai-ssd/hermes/cache/пример1.xls"
    df = pd.read_excel(file_path)
    print(f"📄 Читаем {file_path}: {len(df)} строк\n")

    to_create = 0
    to_skip = 0

    for _, row in df.iterrows():
        raw_name = str(row.iloc[1]).strip()
        desc = str(row.iloc[6]) if len(row) > 6 else ""
        if not raw_name or raw_name.lower() == "nan":
            continue

        dupes = find_duplicates(raw_name, desc)
        rus = extract_russian_name(desc)
        display_name = rus if rus else transliterate_to_cyrillic(raw_name)

        if dupes:
            print(f"⏭️ {raw_name} -> {display_name}")
            print(f"   ❌ Дубли: {dupes}")
            to_skip += 1
        else:
            print(f"✅ {raw_name} -> {display_name}")
            print("   Дублей нет")
            to_create += 1

    print(f"\nИТОГО: Создать: {to_create} | Пропустить: {to_skip}")
