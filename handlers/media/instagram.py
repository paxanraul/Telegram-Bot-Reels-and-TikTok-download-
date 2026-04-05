import os
import shutil
import traceback
import uuid

from aiogram.types import Message, FSInputFile

from config import IG_USERNAME, IG_SESSIONFILE
from handlers.ui import clear_wait
from services.instagram import download_instagram_video
from services.media_utils import (
    extract_audio,
    get_video_dimensions,
    normalize_video_for_telegram,
    should_normalize_video,
)
from texts import TEXTS


async def handle_instagram(message: Message, url: str, lang: str) -> bool:
    wait_msg = await message.reply("⏳")
    target_dir = None
    normalized_video_path = None
    try:
        video_path, target_dir = download_instagram_video(url, IG_USERNAME, IG_SESSIONFILE)
        normalized_video_path = os.path.join(target_dir, f"fixed_{uuid.uuid4().hex}.mp4")
        send_video_path = video_path
        if should_normalize_video(video_path):
            try:
                normalize_video_for_telegram(video_path, normalized_video_path, timeout=180)
                send_video_path = normalized_video_path
            except Exception:
                send_video_path = video_path

        width, height = get_video_dimensions(send_video_path)
        await message.reply_video(
            FSInputFile(send_video_path),
            width=width,
            height=height,
            supports_streaming=True,
        )

        audio_path = os.path.join(target_dir, f"audio_{uuid.uuid4().hex}.mp3")
        try:
            extract_audio(send_video_path, audio_path)
            await message.reply_audio(FSInputFile(audio_path))
        except Exception:
            await message.reply(TEXTS["instagram_audio_fail"][lang])

        try:
            await wait_msg.edit_text(TEXTS["ready"][lang])
        except Exception:
            pass
        return True
    except Exception as e:
        print(f"[Instagram download error] {type(e).__name__}: {e}")
        print(traceback.format_exc())
        await clear_wait(wait_msg)
        await message.reply(TEXTS["instagram_download_fail"][lang])
        return False
    finally:
        if target_dir and os.path.exists(target_dir):
            shutil.rmtree(target_dir, ignore_errors=True)
