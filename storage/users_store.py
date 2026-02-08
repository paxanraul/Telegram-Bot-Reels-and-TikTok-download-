import json
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

USER_IDS_STORE = os.path.join(BASE_DIR, "user_ids.json")
USER_META_STORE = os.path.join(BASE_DIR, "users_meta.json")
user_ids = set()
user_meta = {}


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
    try:
        if os.path.exists(USER_META_STORE):
            with open(USER_META_STORE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                for k, v in data.items():
                    try:
                        user_meta[int(k)] = v
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
    try:
        data = {str(k): v for k, v in user_meta.items()}
        with open(USER_META_STORE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def touch_user(user_id: int, username: str | None = None, first_name: str | None = None, last_name: str | None = None) -> None:
    user_ids.add(user_id)
    meta = user_meta.get(user_id, {})
    if username is not None:
        meta["username"] = username
    if first_name is not None:
        meta["first_name"] = first_name
    if last_name is not None:
        meta["last_name"] = last_name
    if meta:
        user_meta[user_id] = meta
    save_user_ids()
