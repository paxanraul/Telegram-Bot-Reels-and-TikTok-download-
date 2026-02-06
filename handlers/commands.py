from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from config import ADMIN_ID
from handlers.ui import prompt_language, send_greeting
from storage.language_store import has_lang, get_lang
from storage.users_store import touch_user, user_ids

router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    touch_user(message.from_user.id)
    if not has_lang(message.from_user.id):
        await prompt_language(message)
        return
    await send_greeting(message, get_lang(message.from_user.id))


@router.message(Command("lang"))
async def change_language(message: Message) -> None:
    touch_user(message.from_user.id)
    await prompt_language(message)


@router.message(Command("broadcast"))
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
