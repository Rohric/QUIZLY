import os
import yt_dlp
from urllib.parse import urlparse, parse_qs


def extract_video_id(url: str) -> str:
    """Extract the video ID from a YouTube URL.

    Returns the video ID as a string."""
    parsed = urlparse(url)
    video_id = parse_qs(parsed.query).get("v", [None])[0]
    if not video_id:
        raise ValueError("No valid YouTube video ID found.")
    return video_id


def download_audio(url: str) -> str:
    """Download the audio track of a YouTube video.

    Returns the local file path of the downloaded MP3."""
    video_id = extract_video_id(url)
    clean_url = f"https://www.youtube.com/watch?v={video_id}"
    tmp_filename = "audio"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": tmp_filename,
        "quiet": True,
        "noplaylist": True,
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([clean_url])
    import glob

    print("Found files:", glob.glob("audio*"))
    return "audio.mp3"
