import os
import whisper


def transcribe(audio_path: str) -> dict:
    """Transcribe an audio file using Whisper.

    Returns a dict with the transcript text and detected language."""
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return {
        "text": result["text"],
        "language": result.get("language", ""),
    }
