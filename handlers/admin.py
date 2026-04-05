from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import is_admin
from storage.analytics_store import analytics, get_recent_links, get_top_users
from storage.language_store import user_lang
from storage.users_store import user_ids, user_meta

router = Router()


def admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Overview", callback_data="admin:overview"),
                InlineKeyboardButton(text="Users", callback_data="admin:users"),
            ],
            [
                InlineKeyboardButton(text="Recent Links", callback_data="admin:links"),
                InlineKeyboardButton(text="Top Users", callback_data="admin:top"),
            ],
            [
                InlineKeyboardButton(text="Platforms", callback_data="admin:platforms"),
                InlineKeyboardButton(text="Refresh", callback_data="admin:overview"),
            ],
            [
                InlineKeyboardButton(text="Close", callback_data="admin:close"),
            ],
        ]
    )


def _user_label(user_id: int, meta: dict | None = None) -> str:
    meta = meta or user_meta.get(user_id, {})
    username = meta.get("username")
    first_name = meta.get("first_name")
    last_name = meta.get("last_name")
    full_name = " ".join(value for value in [first_name, last_name] if value) or "-"
    if username:
        return f"{full_name} (@{username})"
    return f"{full_name} (id:{user_id})"


def _truncate(text: str, limit: int = 90) -> str:
    if len(text) <= limit:
        return text
    return f"{text[:limit - 3]}..."


def build_overview_text() -> str:
    ru_count = sum(1 for lang in user_lang.values() if lang == "Русский")
    en_count = sum(1 for lang in user_lang.values() if lang == "English")
    status = analytics.get("status_counts", {})
    platforms = analytics.get("platform_counts", {})
    return (
        "Admin panel\n\n"
        f"Users: {len(user_ids)}\n"
        f"Languages: RU {ru_count}, EN {en_count}\n"
        f"Tracked requests: {analytics.get('total_events', 0)}\n"
        f"Success: {status.get('success', 0)}\n"
        f"Failed: {status.get('failed', 0)}\n"
        f"Unsupported: {status.get('unsupported', 0)}\n\n"
        f"TikTok: {platforms.get('tiktok', 0)}\n"
        f"Instagram: {platforms.get('instagram', 0)}\n"
        f"Shorts: {platforms.get('shorts', 0)}\n"
        f"Unsupported links: {platforms.get('unsupported', 0)}"
    )


def build_users_text(limit: int = 20) -> str:
    ids = sorted(list(user_ids))
    lines = [f"Users list: {len(ids)}"]
    for uid in ids[:limit]:
        lines.append(f"{uid} | {_user_label(uid)}")
    if len(ids) > limit:
        lines.append(f"... and {len(ids) - limit} more")
    return "\n".join(lines)


def build_recent_links_text(limit: int = 10) -> str:
    links = get_recent_links(limit)
    if not links:
        return "Recent links: empty"
    lines = ["Recent links:"]
    for item in links:
        label = _user_label(int(item["user_id"]), item)
        lines.append(
            f"{item['timestamp']} | {item['platform']} | {item['status']}\n"
            f"{label}\n{_truncate(item['url'])}"
        )
    return "\n\n".join(lines)


def build_top_users_text(limit: int = 10) -> str:
    ranked = get_top_users(limit)
    if not ranked:
        return "Top users: empty"
    lines = ["Top users by requests:"]
    for user_id, data in ranked:
        lines.append(
            f"{user_id} | {_user_label(int(user_id), data)} | "
            f"requests={data.get('requests', 0)} success={data.get('success', 0)} failed={data.get('failed', 0)}"
        )
    return "\n".join(lines)


def build_platforms_text() -> str:
    platforms = analytics.get("platform_counts", {})
    status = analytics.get("status_counts", {})
    return (
        "Platform stats\n\n"
        f"TikTok: {platforms.get('tiktok', 0)}\n"
        f"Instagram: {platforms.get('instagram', 0)}\n"
        f"Shorts: {platforms.get('shorts', 0)}\n"
        f"Unsupported: {platforms.get('unsupported', 0)}\n\n"
        f"Success total: {status.get('success', 0)}\n"
        f"Failed total: {status.get('failed', 0)}\n"
        f"Unsupported total: {status.get('unsupported', 0)}"
    )


def get_admin_text(section: str) -> str:
    if section == "users":
        return build_users_text()
    if section == "links":
        return build_recent_links_text()
    if section == "top":
        return build_top_users_text()
    if section == "platforms":
        return build_platforms_text()
    return build_overview_text()


@router.message(Command("admin"))
async def admin_panel(message: Message) -> None:
    if not is_admin(message.from_user.id):
        return
    await message.reply(build_overview_text(), reply_markup=admin_keyboard())


@router.callback_query(F.data.startswith("admin:"))
async def admin_callbacks(callback: CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    action = callback.data.split(":", 1)[1]
    if action == "close":
        if callback.message:
            try:
                await callback.message.delete()
            except Exception:
                pass
        await callback.answer()
        return

    if callback.message:
        try:
            await callback.message.edit_text(
                get_admin_text(action),
                reply_markup=admin_keyboard(),
            )
        except Exception:
            pass
    await callback.answer()
