import os
import subprocess
import uuid

from aiogram.types import Message, FSInputFile

from handlers.ui import clear_wait
from services.media_utils import extract_audio
from services.shorts import download_shorts_video
from texts import TEXTS


async def handle_shorts(message: Message, url: str, lang: str) -> None:
    wait_msg = await message.reply("⏳")
    try:
        try:
            video_path = download_shorts_video(url, timeout=180)
        except subprocess.TimeoutExpired:
            print("[YouTube Shorts] Download timeout")
            await clear_wait(wait_msg)
            await message.reply(TEXTS["youtube_download_fail"][lang])
            return
        except Exception as e:
            print(f"[YouTube Shorts] Download error: {e}")
            await clear_wait(wait_msg)
            await message.reply(TEXTS["youtube_download_fail"][lang])
            return

        if video_path and os.path.exists(video_path):
            print(f"[YouTube Shorts] Video found: {video_path}")
            await message.reply_video(FSInputFile(video_path))
        else:
            print("[YouTube Shorts] Video not found after download")
            await clear_wait(wait_msg)
            await message.reply(TEXTS["youtube_download_fail"][lang])
            return

        audio_path = f"shorts_{uuid.uuid4().hex}.mp3"
        try:
            print("[YouTube Shorts] Start audio extract")
            extract_audio(video_path, audio_path, timeout=120)
            print(f"[YouTube Shorts] Audio ready: {audio_path}")
            await message.reply_audio(FSInputFile(audio_path))
        except Exception:
            print("[YouTube Shorts] Audio extract failed")
            await message.reply(TEXTS["youtube_audio_fail"][lang])

        try:
            await wait_msg.edit_text(TEXTS["ready"][lang])
        except Exception:
            pass

        if video_path and os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)
    except Exception:
        await clear_wait(wait_msg)
        await message.reply(TEXTS["youtube_download_fail"][lang])
