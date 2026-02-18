from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message # Импорты из aiogram

from config import ADMIN_ID #import from .env
from handlers.ui import prompt_language, send_greeting # Выбор языка, приветствие
from storage.language_store import has_lang, get_lang # Данные выбора языка
from storage.users_store import touch_user, user_ids, user_meta # Данные пользовалеля

router = Router() # Для команд


@router.message(CommandStart()) # Команда /start
async def start(message: Message) -> None:
    touch_user(
        message.from_user.id,
        username=message.from_user.username, 
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    if not has_lang(message.from_user.id):
        await prompt_language(message)
        return
    await send_greeting(message, get_lang(message.from_user.id))


@router.message(Command("lang")) # Команда /lang
async def change_language(message: Message) -> None:
    touch_user(
        message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await prompt_language(message)


@router.message(Command("broadcast")) # Админский /broadcast для объявлений
async def broadcast(message: Message) -> None:
    if not ADMIN_ID or str(message.from_user.id) != str(ADMIN_ID):
        return
    text = message.text.partition(" ")[2].strip()
    if not text:
        await message.reply("Usage: /broadcast your message")
        return
    sent = 0
    for uid in list(user_ids):
        try:
            await message.bot.send_message(uid, text)
            sent += 1
        except Exception:
            pass
    await message.reply(f"Broadcast sent to {sent} users.")


@router.message(Command("stats")) #Админский /stats для статистики пользователей
async def stats(message: Message) -> None:
    if not ADMIN_ID or str(message.from_user.id) != str(ADMIN_ID):
        return
    ids = sorted(list(user_ids))
    lines = [f"Users: {len(ids)}"]
    for uid in ids:
        meta = user_meta.get(uid, {})
        username = meta.get("username")
        first_name = meta.get("first_name")
        last_name = meta.get("last_name")
        label = " ".join([name for name in [first_name, last_name] if name]) or "-"
        uname = f"@{username}" if username else "-"
        lines.append(f"{uid} | {uname} | {label}")
    await message.reply("\n".join(lines))
