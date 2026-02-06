from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)

from texts import TEXTS


def language_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="English 🇬🇧"), KeyboardButton(text="Русский 🇷🇺")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


async def prompt_language(message: Message) -> None:
    await message.reply(
        TEXTS["prompt_language"],
        reply_markup=language_keyboard(),
    )


async def send_greeting(message: Message, lang: str) -> None:
    text = TEXTS["greeting"][lang].format(name=message.from_user.first_name)
    await message.reply(text, reply_markup=ReplyKeyboardRemove())


async def clear_wait(wait_msg: Message) -> None:
    try:
        await wait_msg.delete()
    except Exception:
        pass
