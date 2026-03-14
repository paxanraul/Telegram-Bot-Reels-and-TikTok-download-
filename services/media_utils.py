import subprocess


def extract_audio(video_path: str, audio_path: str, timeout: int | None = None) -> None:
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
        timeout=timeout,
    )


def normalize_video_for_telegram(
    input_path: str,
    output_path: str,
    timeout: int | None = None,
) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            # Render square pixels into the actual frame and strip rotation quirks.
            "-vf",
            "scale=trunc(iw*sar/2)*2:trunc(ih/2)*2,setsar=1,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-c:a",
            "copy",
            "-metadata:s:v:0",
            "rotate=0",
            "-movflags",
            "+faststart",
            output_path,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=timeout,
    )


def get_video_dimensions(video_path: str) -> tuple[int | None, int | None]:
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "csv=p=0:s=x",
                video_path,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        raw = result.stdout.strip()
        if not raw or "x" not in raw:
            return None, None
        width, height = raw.split("x", 1)
        return int(width), int(height)
    except Exception:
        return None, None
