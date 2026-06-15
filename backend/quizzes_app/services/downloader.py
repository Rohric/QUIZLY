import os
import yt_dlp
from urllib.parse import urlparse, parse_qs


def extract_video_id(url: str) -> str:
    parsed = urlparse(url)
    video_id = parse_qs(parsed.query).get("v", [None])[0]
    if not video_id:
        raise ValueError("Keine gültige YouTube Video-ID gefunden.")
    return video_id


def download_audio(url: str) -> str:
    video_id = extract_video_id(url)
    clean_url = f"https://www.youtube.com/watch?v={video_id}"
    tmp_filename = "audio"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": tmp_filename,
        "quiet": True,
        "noplaylist": True,
        "ffmpeg_location": r"C:\Users\emilm\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-essentials_build\bin",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([clean_url])
    import glob

    print("Gefundene Dateien:", glob.glob("audio*"))
    return "audio.mp3"
