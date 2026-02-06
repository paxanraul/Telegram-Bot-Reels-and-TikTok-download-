import os
import uuid

from aiogram.types import Message, FSInputFile

from handlers.ui import clear_wait
from services.media_utils import extract_audio
from services.tiktok import download_tiktok_video
from texts import TEXTS


async def handle_tiktok(message: Message, url: str, lang: str) -> None:
    wait_msg = await message.reply("⏳")
    try:
        video_path = download_tiktok_video(url)
        if not video_path:
            await clear_wait(wait_msg)
            await message.reply(TEXTS["tiktok_download_fail"][lang])
            return

        audio_path = f"tiktok_{uuid.uuid4().hex}.mp3"
        await message.reply_video(FSInputFile(video_path))
        try:
            extract_audio(video_path, audio_path)
            await message.reply_audio(FSInputFile(audio_path))
        except Exception:
            await message.reply(TEXTS["tiktok_audio_fail"][lang])
        try:
            await wait_msg.edit_text(TEXTS["ready"][lang])
        except Exception:
            pass

        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)
    except Exception:
        await clear_wait(wait_msg)
        await message.reply(TEXTS["tiktok_download_fail"][lang])
