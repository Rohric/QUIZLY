import json
import yt_dlp

URL = "https://www.youtube.com/watch?v=BaW_jenozKc"

# ℹ️ See help(yt_dlp.YoutubeDL) for a list of available options and public functions

tmp_filename = "audio"  # oder ein temporärer Pfad
ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": tmp_filename,
    "quiet": True,
    "noplaylist": True,
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(URL, download=False)

    # ℹ️ ydl.sanitize_info makes the info json-serializable
    print(json.dumps(ydl.sanitize_info(info)))
