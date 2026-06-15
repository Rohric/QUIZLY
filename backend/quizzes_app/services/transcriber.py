import whisper


def transcribe(audio_path: str) -> dict:
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return {
        "text": result["text"],
        "language": result.get("language", "de"),
    }
