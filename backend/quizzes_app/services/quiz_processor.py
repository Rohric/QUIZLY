"""Quiz creation and processing logic."""

import os
from .downloader import download_audio, extract_video_id
from .gemini import generate_quiz
from .transcriber import transcribe
from ..models import ProcessingLog, Question, Quiz, Transcript


def normalize_youtube_url(url: str) -> tuple[str, str]:
    """Extract video ID and return normalized URL.

    Returns (video_id, clean_url) tuple."""
    video_id = extract_video_id(url)
    clean_url = f"https://www.youtube.com/watch?v={video_id}"
    return video_id, clean_url


def create_processing_log(quiz: Quiz, status: str, message: str = "") -> ProcessingLog:
    """Create a processing log entry for a quiz.

    Returns the created ProcessingLog instance."""
    return ProcessingLog.objects.create(quiz=quiz, status=status, message=message)


def save_transcript(quiz: Quiz, transcript_data: dict) -> Transcript:
    """Save transcript data to database.

    Returns the created Transcript instance."""
    return Transcript.objects.create(
        quiz=quiz,
        raw_text=transcript_data["text"],
        language=transcript_data["language"],
    )


def save_questions(quiz: Quiz, quiz_data: dict) -> list:
    """Save quiz questions to database.

    Returns list of created Question instances."""
    questions = []
    for q in quiz_data["questions"]:
        question = Question.objects.create(
            quiz=quiz,
            question_title=q["question_title"],
            question_options=q["question_options"],
            answer=q["answer"],
        )
        questions.append(question)
    return questions


def download_and_transcribe(quiz: Quiz, clean_url: str) -> tuple[str, dict]:
    """Download audio and transcribe it.

    Returns (audio_path, transcript_data) tuple."""
    create_processing_log(quiz, "download_started")
    audio_path = download_audio(clean_url)
    create_processing_log(quiz, "download_completed")

    create_processing_log(quiz, "transcription_started")
    transcript_data = transcribe(audio_path)
    save_transcript(quiz, transcript_data)
    create_processing_log(quiz, "transcription_completed")
    return audio_path, transcript_data


def generate_and_save_quiz(quiz: Quiz, transcript_text: str) -> None:
    """Generate quiz from transcript and save questions.

    Raises ValueError if generation fails."""
    create_processing_log(quiz, "generation_started")
    quiz_data = generate_quiz(transcript_text)
    create_processing_log(quiz, "generation_completed")

    quiz.title = quiz_data["title"]
    quiz.description = quiz_data.get("description", "")
    quiz.status = "completed"
    quiz.save()

    save_questions(quiz, quiz_data)
    create_processing_log(quiz, "completed")


def process_quiz_creation(quiz: Quiz, clean_url: str) -> None:
    """Execute the full quiz creation pipeline.

    Raises ValueError if any step fails."""
    audio_path = None
    try:
        audio_path, transcript_data = download_and_transcribe(quiz, clean_url)
        generate_and_save_quiz(quiz, transcript_data["text"])
    except Exception as e:
        quiz.status = "failed"
        quiz.save()
        create_processing_log(quiz, "error", str(e))
        raise
    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)


def create_quiz_from_url(user, url: str) -> Quiz:
    """Create a new quiz from a YouTube URL.

    Returns the created Quiz instance."""
    video_id, clean_url = normalize_youtube_url(url)

    quiz = Quiz.objects.create(
        owner=user,
        title="Processing...",
        video_url=clean_url,
        status="processing",
    )

    process_quiz_creation(quiz, clean_url)
    quiz.refresh_from_db()
    return quiz
