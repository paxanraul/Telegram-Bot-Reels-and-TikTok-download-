import os
import shutil
import traceback
import uuid

import instaloader


def ensure_instagram_login(L: instaloader.Instaloader, username: str | None, sessionfile: str | None) -> bool:
    if not username or not sessionfile:
        return False
    try:
        if os.path.exists(sessionfile):
            L.load_session_from_file(username, sessionfile)
            return True
        print("[Instagram login error] Sessionfile not found")
        return False
    except Exception as e:
        print(f"[Instagram login error] {type(e).__name__}: {e}")
        print(traceback.format_exc())
        return False


def download_instagram_video(url: str, username: str | None, sessionfile: str | None) -> tuple[str, str]:
    if "/reel/" in url:
        shortcode = url.split("/reel/")[1].split("/")[0]
    elif "/p/" in url:
        shortcode = url.split("/p/")[1].split("/")[0]
    else:
        raise ValueError("invalid_shortcode")

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

    if not ensure_instagram_login(L, username, sessionfile):
        raise RuntimeError("login_failed")

    post = instaloader.Post.from_shortcode(L.context, shortcode)

    target_dir = f"ig_temp_{uuid.uuid4().hex}"
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir, ignore_errors=True)
    os.makedirs(target_dir, exist_ok=True)

    L.download_post(post, target=target_dir)

    video_path = None
    for file in os.listdir(target_dir):
        if file.lower().endswith(".mp4"):
            video_path = os.path.join(target_dir, file)
            break

    if not video_path or not os.path.exists(video_path):
        raise FileNotFoundError("instagram_video_not_found")

    return video_path, target_dir
