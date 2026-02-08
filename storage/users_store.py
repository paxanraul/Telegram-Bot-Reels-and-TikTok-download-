import json
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

USER_IDS_STORE = os.path.join(BASE_DIR, "user_ids.json")
user_ids = set()


def load_user_ids() -> None:
    if not os.path.exists(USER_IDS_STORE):
        return
    try:
        with open(USER_IDS_STORE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            for item in data:
                try:
                    user_ids.add(int(item))
                except Exception:
                    continue
    except Exception:
        pass


def save_user_ids() -> None:
    try:
        with open(USER_IDS_STORE, "w", encoding="utf-8") as f:
            json.dump(sorted(user_ids), f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def touch_user(user_id: int) -> None:
    user_ids.add(user_id)
    save_user_ids()
