import os
import whisper

os.environ["PATH"] += (
    r";C:\Users\emilm\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-essentials_build\bin"
)


def transcribe(audio_path: str) -> dict:
    """Transcribe an audio file using Whisper.

    Returns a dict with the transcript text and detected language."""
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return {
        "text": result["text"],
        "language": result.get("language", "de"),
    }
