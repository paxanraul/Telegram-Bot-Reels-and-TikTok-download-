import uuid

from tiktok_downloader import snaptik


def download_tiktok_video(url: str) -> str | None:
    snaps = snaptik(url)
    if not snaps:
        return None
    uid = uuid.uuid4().hex
    video_path = f"tiktok_{uid}.mp4"
    snaps[0].download(video_path)
    return video_path
