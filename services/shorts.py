import os
import subprocess
import uuid


def download_shorts_video(url: str, timeout: int = 180) -> str | None:
    uid = uuid.uuid4().hex
    output_template = f"shorts_{uid}.%(ext)s"

    print(f"[YouTube Shorts] Start download: {url}")
    subprocess.run(
        [
            "yt-dlp",
            "-f",
            "bv*+ba/b",
            "--merge-output-format",
            "mp4",
            "-o",
            output_template,
            url,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=timeout,
    )
    print("[YouTube Shorts] Download finished")

    for file in os.listdir("."):
        if file.startswith(f"shorts_{uid}.") and file.lower().endswith((".mp4", ".mkv", ".webm")):
            return file
    return None
