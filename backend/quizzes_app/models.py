from django.conf import settings
from django.db import models


class Quiz(models.Model):
    """Main model for a quiz based on a YouTube video."""

    STATUS_CHOICES = [
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quizzes",
        help_text="The user who owns this quiz.",
    )

    title = models.CharField(max_length=255, help_text="Title of the quiz.")
    description = models.TextField(blank=True, default="", help_text="Description of the quiz.")
    video_url = models.URLField(help_text="URL of the YouTube video.")

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="processing", help_text="Processing status of the quiz."
    )

    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp of creation.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp of last update.")

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Quizzes"
        indexes = [
            models.Index(fields=["owner", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.owner.username})"


class Transcript(models.Model):
    """Stores the transcript of a YouTube video."""

    quiz = models.OneToOneField(Quiz, on_delete=models.CASCADE, related_name="transcript", help_text="Associated quiz.")

    raw_text = models.TextField(help_text="Raw transcript text from Whisper.")
    duration = models.IntegerField(null=True, blank=True, help_text="Video duration in seconds.")
    language = models.CharField(max_length=10, default="", help_text="Detected language (e.g. 'de', 'en').")

    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp of transcription.")

    class Meta:
        verbose_name_plural = "Transcripts"

    def __str__(self):
        preview = self.raw_text[:50] + "..." if len(self.raw_text) > 50 else self.raw_text
        return f"Transcript for {self.quiz.title}: {preview}"


class Question(models.Model):
    """Stores a single question belonging to a quiz."""

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions", help_text="Associated quiz.")

    question_title = models.CharField(max_length=500, help_text="The question text.")
    question_options = models.JSONField(help_text="List of 4 answer options as a JSON array.")
    answer = models.CharField(max_length=255, help_text="The correct answer.")

    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp of creation.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp of last update.")

    class Meta:
        ordering = ["quiz", "created_at"]
        verbose_name_plural = "Questions"
        indexes = [
            models.Index(fields=["quiz"]),
        ]

    def __str__(self):
        return f"Q{self.id}: {self.question_title[:50]}"


class ProcessingLog(models.Model):
    """Logs each processing step of a quiz for debugging and error tracking."""

    STATUS_CHOICES = [
        ("download_started", "Download started"),
        ("download_completed", "Download completed"),
        ("transcription_started", "Transcription started"),
        ("transcription_completed", "Transcription completed"),
        ("generation_started", "Quiz generation started"),
        ("generation_completed", "Quiz generation completed"),
        ("error", "Error occurred"),
        ("completed", "Fully processed"),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="logs", help_text="Associated quiz.")

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, help_text="Status of the processing step.")
    message = models.TextField(blank=True, default="", help_text="Message or error details.")
    error_details = models.JSONField(
        null=True, blank=True, help_text="Detailed error information if an error occurred."
    )

    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp of the log entry.")

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Processing Logs"
        indexes = [
            models.Index(fields=["quiz", "-created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.quiz.title} - {self.status} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
