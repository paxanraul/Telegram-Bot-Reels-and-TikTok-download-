import json
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

LANG_STORE = os.path.join(BASE_DIR, "user_lang.json")
user_lang = {}


def load_languages() -> None:
    if not os.path.exists(LANG_STORE):
        return
    try:
        with open(LANG_STORE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            for k, v in data.items():
                try:
                    user_lang[int(k)] = v
                except Exception:
                    continue
    except Exception:
        pass


def save_languages() -> None:
    try:
        data = {str(k): v for k, v in user_lang.items()}
        with open(LANG_STORE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def has_lang(user_id: int) -> bool:
    return user_id in user_lang


def get_lang(user_id: int, default: str = "Русский") -> str:
    return user_lang.get(user_id, default)


def set_lang(user_id: int, lang: str) -> None:
    user_lang[user_id] = lang
    save_languages()
