from django.conf import settings
from django.db import models


class Quiz(models.Model):
    """Hauptmodell für ein Quiz basierend auf einer YouTube-Video"""

    STATUS_CHOICES = [
        ("processing", "Wird verarbeitet"),
        ("completed", "Fertig"),
        ("failed", "Fehler"),
    ]

    # Beziehungen
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quizzes",
        help_text="Der Benutzer, dem das Quiz gehört",
    )

    # Basis-Informationen
    title = models.CharField(max_length=255, help_text="Titel des Quiz")
    description = models.TextField(blank=True, default="", help_text="Beschreibung des Quiz")
    video_url = models.URLField(help_text="URL zum YouTube-Video")

    # Status & Tracking
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="processing", help_text="Verarbeitungsstatus des Quiz"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="Zeitstempel der Erstellung")
    updated_at = models.DateTimeField(auto_now=True, help_text="Zeitstempel der letzten Änderung")

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Quizzes"
        indexes = [
            models.Index(fields=["owner", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.owner.username})"


class Transcript(models.Model):
    """Speichert den Transkript des YouTube-Videos"""

    # Beziehung
    quiz = models.OneToOneField(Quiz, on_delete=models.CASCADE, related_name="transcript", help_text="Zugehöriges Quiz")

    # Transkript-Daten
    raw_text = models.TextField(help_text="Rohtext des Transkripts von Whisper")
    duration = models.IntegerField(null=True, blank=True, help_text="Länge des Videos in Sekunden")
    language = models.CharField(max_length=10, default="de", help_text="Erkannte Sprache (z.B. 'de', 'en')")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="Zeitstempel der Transkription")

    class Meta:
        verbose_name_plural = "Transcripts"

    def __str__(self):
        preview = self.raw_text[:50] + "..." if len(self.raw_text) > 50 else self.raw_text
        return f"Transcript für {self.quiz.title}: {preview}"


class Question(models.Model):
    """Speichert einzelne Fragen eines Quiz"""

    # Beziehung
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions", help_text="Zugehöriges Quiz")

    # Frage-Daten
    question_title = models.CharField(max_length=500, help_text="Der Fragetext")
    question_options = models.JSONField(
        help_text="Liste mit 4 Antwortmöglichkeiten als JSON Array"
        # Beispiel: ["Option A", "Option B", "Option C", "Option D"]
    )
    answer = models.CharField(max_length=255, help_text="Die richtige Antwort")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="Zeitstempel der Erstellung")
    updated_at = models.DateTimeField(auto_now=True, help_text="Zeitstempel der letzten Änderung")

    class Meta:
        ordering = ["quiz", "created_at"]
        verbose_name_plural = "Questions"
        indexes = [
            models.Index(fields=["quiz"]),
        ]

    def __str__(self):
        return f"Q{self.id}: {self.question_title[:50]}"


class ProcessingLog(models.Model):
    """Logging für die Verarbeitung eines Quiz (für Debugging & Error-Handling)"""

    STATUS_CHOICES = [
        ("download_started", "Download gestartet"),
        ("download_completed", "Download fertig"),
        ("transcription_started", "Transkription gestartet"),
        ("transcription_completed", "Transkription fertig"),
        ("generation_started", "Quiz-Generierung gestartet"),
        ("generation_completed", "Quiz-Generierung fertig"),
        ("error", "Fehler aufgetreten"),
        ("completed", "Vollständig verarbeitet"),
    ]

    # Beziehung
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="logs", help_text="Zugehöriges Quiz")

    # Log-Informationen
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, help_text="Status des Verarbeitungsschritts")
    message = models.TextField(blank=True, default="", help_text="Nachricht oder Error-Details")
    error_details = models.JSONField(null=True, blank=True, help_text="Detaillierte Error-Informationen falls Fehler")

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, help_text="Zeitstempel des Log-Eintrags")

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Processing Logs"
        indexes = [
            models.Index(fields=["quiz", "-created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.quiz.title} - {self.status} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
