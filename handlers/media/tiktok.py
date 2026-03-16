import os
import uuid

from aiogram.types import Message, FSInputFile

from handlers.ui import clear_wait
from services.media_utils import (
    extract_audio,
    normalize_video_for_telegram,
    should_normalize_video,
)
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

        normalized_video_path = f"tiktok_fixed_{uuid.uuid4().hex}.mp4"
        audio_path = f"tiktok_{uuid.uuid4().hex}.mp3"
        send_video_path = video_path
        if should_normalize_video(video_path):
            try:
                normalize_video_for_telegram(video_path, normalized_video_path, timeout=180)
                send_video_path = normalized_video_path
            except Exception:
                send_video_path = video_path

        await message.reply_video(FSInputFile(send_video_path))
        try:
            extract_audio(send_video_path, audio_path)
            await message.reply_audio(FSInputFile(audio_path))
        except Exception:
            await message.reply(TEXTS["tiktok_audio_fail"][lang])
        try:
            await wait_msg.edit_text(TEXTS["ready"][lang])
        except Exception:
            pass

        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(normalized_video_path):
            os.remove(normalized_video_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)
    except Exception:
        await clear_wait(wait_msg)
        await message.reply(TEXTS["tiktok_download_fail"][lang])
