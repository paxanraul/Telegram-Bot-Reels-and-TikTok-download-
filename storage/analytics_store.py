import json
import os
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ANALYTICS_STORE = os.path.join(BASE_DIR, "analytics.json")
RECENT_LIMIT = 200

analytics = {
    "total_events": 0,
    "platform_counts": {
        "tiktok": 0,
        "instagram": 0,
        "shorts": 0,
        "unsupported": 0,
    },
    "status_counts": {
        "success": 0,
        "failed": 0,
        "unsupported": 0,
    },
    "users": {},
    "recent_links": [],
}


def load_analytics() -> None:
    if not os.path.exists(ANALYTICS_STORE):
        return
    try:
        with open(ANALYTICS_STORE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            analytics.update(data)
    except Exception:
        pass


def save_analytics() -> None:
    try:
        with open(ANALYTICS_STORE, "w", encoding="utf-8") as f:
            json.dump(analytics, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def _ensure_user_bucket(user_id: int) -> dict:
    key = str(user_id)
    bucket = analytics["users"].get(key)
    if not isinstance(bucket, dict):
        bucket = {
            "requests": 0,
            "success": 0,
            "failed": 0,
            "unsupported": 0,
            "platforms": {
                "tiktok": 0,
                "instagram": 0,
                "shorts": 0,
                "unsupported": 0,
            },
        }
        analytics["users"][key] = bucket
    return bucket


def record_link_event(
    *,
    user_id: int,
    username: str | None,
    first_name: str | None,
    last_name: str | None,
    platform: str,
    url: str,
    status: str,
) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    analytics["total_events"] = int(analytics.get("total_events", 0)) + 1
    analytics["platform_counts"][platform] = int(analytics["platform_counts"].get(platform, 0)) + 1
    analytics["status_counts"][status] = int(analytics["status_counts"].get(status, 0)) + 1

    user_bucket = _ensure_user_bucket(user_id)
    user_bucket["requests"] = int(user_bucket.get("requests", 0)) + 1
    user_bucket[status] = int(user_bucket.get(status, 0)) + 1
    platforms = user_bucket.setdefault("platforms", {})
    platforms[platform] = int(platforms.get(platform, 0)) + 1

    if username is not None:
        user_bucket["username"] = username
    if first_name is not None:
        user_bucket["first_name"] = first_name
    if last_name is not None:
        user_bucket["last_name"] = last_name
    user_bucket["last_seen"] = timestamp
    user_bucket["last_url"] = url

    recent = analytics.setdefault("recent_links", [])
    recent.append(
        {
            "timestamp": timestamp,
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "platform": platform,
            "status": status,
            "url": url,
        }
    )
    if len(recent) > RECENT_LIMIT:
        del recent[:-RECENT_LIMIT]

    save_analytics()


def get_recent_links(limit: int = 10) -> list[dict]:
    recent = analytics.get("recent_links", [])
    return list(reversed(recent[-limit:]))


def get_top_users(limit: int = 10) -> list[tuple[str, dict]]:
    users = analytics.get("users", {})
    ranked = sorted(
        users.items(),
        key=lambda item: (int(item[1].get("requests", 0)), int(item[1].get("success", 0))),
        reverse=True,
    )
    return ranked[:limit]
