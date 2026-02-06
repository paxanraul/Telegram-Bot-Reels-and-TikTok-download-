import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers.commands import router as commands_router
from handlers.messages import router as messages_router
from storage.language_store import load_languages
from storage.users_store import load_user_ids


async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(commands_router)
    dp.include_router(messages_router)

    load_languages()
    load_user_ids()

    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
