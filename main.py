import asyncio
import json
import os
import shutil
import subprocess
import traceback
import uuid

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    FSInputFile,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from dotenv import load_dotenv

from tiktok_downloader import snaptik
import instaloader

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")
IG_SESSIONFILE = os.getenv("IG_SESSIONFILE")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_lang = {}
LANG_STORE = "user_lang.json"


def load_languages() -> None:
    if not os.path.exists(LANG_STORE):
        return
    try:
        with open(LANG_STORE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            for k, v in data.items():
                try:
                    user_lang[int(k)] = v
                except Exception:
                    continue
    except Exception:
        pass


def save_languages() -> None:
    try:
        data = {str(k): v for k, v in user_lang.items()}
        with open(LANG_STORE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
TEXTS = {
    "prompt_language": "🏳️ Choose a language / Выберите язык:",
    "greeting": {
        "English": "Hi, {name} !🙂 Send me a TikTok, Instagram (Reels) or YouTube (Shorts) link, and I'll send you the video without a watermark.",
        "Russian": "Привет, {   name} !🙂 Отправь мне ссылку на видео из TikTok, Instagram (Reels) или YouTube (Shorts) видео, и я отправлю тебе видео без водяного знака.",
    },
    "tiktok_download_fail": {
        "English": "😔 Failed to download the video from TikTok. Try another link or later.",
        "Russian": "😔 Не удалось скачать видео из TikTok. Попробуй другую ссылку или позже.",
    },
    "tiktok_audio_fail": {
        "English": "😔 Failed to extract audio from TikTok. Try another link or later.",
        "Russian": "😔 Не удалось извлечь аудио из TikTok. Попробуй другую ссылку или позже.",
    },
    "instagram_download_fail": {
        "English": "😔 Failed to download the video from Instagram. Try another link or later.",
        "Russian": "😔 Не удалось скачать видео из Instagram. Попробуй другую ссылку или позже.",
    },
    "instagram_audio_fail": {
        "English": "😔 Failed to extract audio from Instagram. Try another link or later.",
        "Russian": "😔 Не удалось извлечь аудио из Instagram. Попробуй другую ссылку или позже.",
    },
    "youtube_download_fail": {
        "English": "😔 Failed to download the video from YouTube Shorts. Try another link or later.",
        "Russian": "😔 Не удалось скачать видео из YouTube Shorts. Попробуй другую ссылку или позже.",
    },
    "youtube_audio_fail": {
        "English": "😔 Failed to extract audio from YouTube Shorts. Try another link or later.",
        "Russian": "😔 Не удалось извлечь аудио из YouTube Shorts. Попробуй другую ссылку или позже.",
    },
    "bad_link": {
        "English": "This doesn't look like a TikTok, Instagram Reels, or YouTube Shorts link.\nPlease send a correct link.",
        "Russian": "Ссылка не похожа на TikTok, Instagram Reels или YouTube Shorts.\nПришли правильную ссылку, пожалуйста.",
    },
    "ready": {
        "English": "Done✅",
        "Russian": "Готово✅",
    },
}


def language_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="English 🇬🇧"), KeyboardButton(text="Russian 🇷🇺")],
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


def get_lang(message: Message) -> str:
    return user_lang.get(message.from_user.id, "Russian")


def ensure_instagram_login(L: instaloader.Instaloader) -> bool:
    if not IG_USERNAME or not IG_SESSIONFILE:
        return False
    session_file = IG_SESSIONFILE
    try:
        if os.path.exists(session_file):
            L.load_session_from_file(IG_USERNAME, session_file)
            return True
        print("[Instagram login error] Sessionfile not found")
        return False
    except Exception as e:
        print(f"[Instagram login error] {type(e).__name__}: {e}")
        print(traceback.format_exc())
        return False


@dp.message(CommandStart())
async def start(message: Message):
    if message.from_user.id not in user_lang:
        await prompt_language(message)
        return
    await send_greeting(message, user_lang[message.from_user.id])


@dp.message(Command("lang"))
async def change_language(message: Message):
    await prompt_language(message)


@dp.message()
async def handle_link(message: Message):
    if message.text and message.text.strip().startswith("/"):
        return

    if message.text and message.text.strip() in {"English 🇬🇧", "Russian 🇷🇺"}:
        chosen = message.text.strip()
        if chosen == "English 🇬🇧":
            user_lang[message.from_user.id] = "English"
        else:
            user_lang[message.from_user.id] = "Russian"
        save_languages()
        await send_greeting(message, user_lang[message.from_user.id])
        return

    if message.from_user.id not in user_lang:
        await prompt_language(message)
        return

    url = message.text.strip()

    lang = get_lang(message)

    if 'tiktok.com' in url:
        wait_msg = await message.reply("⏳")
        try:
            snaps = snaptik(url)
            if not snaps:
                await message.reply(TEXTS["tiktok_download_fail"][lang])
                return

            uid = uuid.uuid4().hex
            video_path = f"tiktok_{uid}.mp4"
            audio_path = f"tiktok_{uid}.mp3"
            snaps[0].download(video_path)  # обычно [0] — это вариант без watermark

            await message.reply_video(FSInputFile(video_path))
            try:
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-i",
                        video_path,
                        "-vn",
                        "-acodec",
                        "libmp3lame",
                        "-q:a",
                        "2",
                        audio_path,
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
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
            await message.reply(TEXTS["tiktok_download_fail"][lang])

    elif 'instagram.com/reel' in url or 'instagram.com/p/' in url:
        wait_msg = await message.reply("⏳")
        try:
            # Извлекаем shortcode
            if '/reel/' in url:
                shortcode = url.split('/reel/')[1].split('/')[0]
            elif '/p/' in url:
                shortcode = url.split('/p/')[1].split('/')[0]
            else:
                await message.reply(TEXTS["instagram_download_fail"][lang])
                return

            L = instaloader.Instaloader(
                download_pictures=False,
                download_videos=True,   
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=False,
                compress_json=False,
            )
            # Reduce retries and timeouts to avoid long waits on blocked HQ requests
            L.context.max_connection_attempts = 2
            L.context.request_timeout = 10

            if not ensure_instagram_login(L):
                await message.reply(TEXTS["instagram_download_fail"][lang])
                return

            post = instaloader.Post.from_shortcode(L.context, shortcode)

            target_dir = 'ig_temp'
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir, ignore_errors=True)
            os.makedirs(target_dir, exist_ok=True)

            L.download_post(post, target=target_dir)

            video_path = None
            for file in os.listdir(target_dir):
                if file.lower().endswith('.mp4'):
                    video_path = os.path.join(target_dir, file)
                    break

            if video_path and os.path.exists(video_path):
                await message.reply_video(FSInputFile(video_path))
                audio_path = os.path.join(target_dir, f"audio_{uuid.uuid4().hex}.mp3")
                try:
                    subprocess.run(
                        [
                            "ffmpeg",
                            "-y",
                            "-i",
                            video_path,
                            "-vn",
                            "-acodec",
                            "libmp3lame",
                            "-q:a",
                            "2",
                            audio_path,
                        ],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    await message.reply_audio(FSInputFile(audio_path))
                except Exception:
                    await message.reply(TEXTS["instagram_audio_fail"][lang])
                try:
                    await wait_msg.edit_text(TEXTS["ready"][lang])
                except Exception:
                    pass
                shutil.rmtree(target_dir, ignore_errors=True)
            else:
                await message.reply(TEXTS["instagram_download_fail"][lang])

        except Exception as e:
            print(f"[Instagram download error] {type(e).__name__}: {e}")
            print(traceback.format_exc())
            await message.reply(TEXTS["instagram_download_fail"][lang])
            if os.path.exists('ig_temp'):
                shutil.rmtree('ig_temp', ignore_errors=True)

    elif 'youtube.com/shorts/' in url or 'm.youtube.com/shorts/' in url:
        wait_msg = await message.reply("⏳")
        try:
            uid = uuid.uuid4().hex
            video_path = f"shorts_{uid}.mp4"
            audio_path = f"shorts_{uid}.mp3"

            subprocess.run(
                [
                    "yt-dlp",
                    "-f",
                    "bv*+ba/b",
                    "-o",
                    video_path,
                    url,
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            if os.path.exists(video_path):
                await message.reply_video(FSInputFile(video_path))
            else:
                await message.reply(TEXTS["youtube_download_fail"][lang])
                return

            try:
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-i",
                        video_path,
                        "-vn",
                        "-acodec",
                        "libmp3lame",
                        "-q:a",
                        "2",
                        audio_path,
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                await message.reply_audio(FSInputFile(audio_path))
            except Exception:
                await message.reply(TEXTS["youtube_audio_fail"][lang])

            try:
                await wait_msg.edit_text(TEXTS["ready"][lang])
            except Exception:
                pass

            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(audio_path):
                os.remove(audio_path)

        except Exception:
            await message.reply(TEXTS["youtube_download_fail"][lang])

    else:
        await message.reply(TEXTS["bad_link"][lang])


async def main():
    load_languages()
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())
