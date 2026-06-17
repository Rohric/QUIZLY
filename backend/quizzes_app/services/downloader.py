import re
from urllib.parse import parse_qs, urlparse

import yt_dlp

YOUTUBE_DOMAINS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "www.youtu.be"}

YOUTUBE_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{11}$")


def extract_video_id(url: str) -> str:
    """Extract the video ID from a YouTube URL.

    Returns the video ID as a string."""
    parsed = urlparse(url.strip())

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Invalid URL: must start with http:// or https://")

    if parsed.netloc not in YOUTUBE_DOMAINS:
        raise ValueError("Invalid URL: not a YouTube link.")

    if parsed.netloc in ("youtu.be", "www.youtu.be"):
        video_id = parsed.path.lstrip("/").split("/")[0]

    elif parsed.path.startswith(("/shorts/", "/embed/", "/v/")):
        video_id = parsed.path.split("/")[2]

    else:
        video_id = parse_qs(parsed.query).get("v", [None])[0]

    if not video_id or not YOUTUBE_ID_RE.match(video_id):
        raise ValueError("No valid YouTube video ID found.")

    return video_id


def download_audio(clean_url: str) -> str:
    """Download the audio track of a YouTube video.

    Returns the local file path of the downloaded MP3."""
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
