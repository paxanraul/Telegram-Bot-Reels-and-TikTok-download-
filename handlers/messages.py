from aiogram import Router
from aiogram.types import Message

from handlers.media.instagram import handle_instagram
from handlers.media.shorts import handle_shorts
from handlers.media.tiktok import handle_tiktok
from handlers.ui import prompt_language, send_greeting
from storage.language_store import get_lang, has_lang, set_lang
from storage.users_store import touch_user
from texts import TEXTS

router = Router()


@router.message()
async def handle_link(message: Message) -> None:
    touch_user(
        message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )

    if message.text and message.text.strip().startswith("/"):
        return

    if message.text and message.text.strip() in {"English 🇬🇧", "Русский 🇷🇺"}:
        chosen = message.text.strip()
        if chosen == "English 🇬🇧":
            set_lang(message.from_user.id, "English")
        else:
            set_lang(message.from_user.id, "Русский")
        await send_greeting(message, get_lang(message.from_user.id))
        return

    if not has_lang(message.from_user.id):
        await prompt_language(message)
        return

    url = message.text.strip()
    lang = get_lang(message.from_user.id)

    if "tiktok.com" in url:
        await handle_tiktok(message, url, lang)
    elif "instagram.com/reel" in url or "instagram.com/p/" in url:
        await handle_instagram(message, url, lang)
    elif "youtube.com/shorts/" in url or "m.youtube.com/shorts/" in url:
        await handle_shorts(message, url, lang)
    else:
        await message.reply(TEXTS["bad_link"][lang])
