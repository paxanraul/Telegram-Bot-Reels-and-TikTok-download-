import os
import shutil
import traceback
import uuid

from aiogram.types import Message, FSInputFile

from config import IG_USERNAME, IG_SESSIONFILE
from handlers.ui import clear_wait
from services.instagram import download_instagram_video
from services.media_utils import extract_audio
from texts import TEXTS


async def handle_instagram(message: Message, url: str, lang: str) -> None:
    wait_msg = await message.reply("⏳")
    target_dir = None
    try:
        video_path, target_dir = download_instagram_video(url, IG_USERNAME, IG_SESSIONFILE)
        await message.reply_video(FSInputFile(video_path))

        audio_path = os.path.join(target_dir, f"audio_{uuid.uuid4().hex}.mp3")
        try:
            extract_audio(video_path, audio_path)
            await message.reply_audio(FSInputFile(audio_path))
        except Exception:
            await message.reply(TEXTS["instagram_audio_fail"][lang])

        try:
            await wait_msg.edit_text(TEXTS["ready"][lang])
        except Exception:
            pass
    except Exception as e:
        print(f"[Instagram download error] {type(e).__name__}: {e}")
        print(traceback.format_exc())
        await clear_wait(wait_msg)
        await message.reply(TEXTS["instagram_download_fail"][lang])
    finally:
        if target_dir and os.path.exists(target_dir):
            shutil.rmtree(target_dir, ignore_errors=True)
