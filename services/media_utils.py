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
            # Force square pixels so Telegram does not stretch videos
            "-vf",
            "scale=trunc(iw*sar/2)*2:trunc(ih/2)*2,setsar=1",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-c:a",
            "copy",
            "-movflags",
            "+faststart",
            output_path,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=timeout,
    )
