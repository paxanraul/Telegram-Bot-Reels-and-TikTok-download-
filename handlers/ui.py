from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from texts import TEXTS


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en"),
                InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang_ru"),
            ],
        ],
    )


async def prompt_language(message: Message) -> None:
    await message.reply(
        TEXTS["prompt_language"],
        reply_markup=language_keyboard(),
    )


async def send_greeting(message: Message, lang: str) -> None:
    text = TEXTS["greeting"][lang].format(name=message.from_user.first_name)
    await message.reply(text)


async def clear_wait(wait_msg: Message) -> None:
    try:
        await wait_msg.delete()
    except Exception:
        pass
