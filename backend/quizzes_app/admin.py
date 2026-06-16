from django.contrib import admin
from .models import Quiz, Question, ProcessingLog, Transcript


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "title", "status", "created_at", "updated_at")
    search_fields = ("title", "owner__username")
    list_filter = ("status", "created_at")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "quiz", "question_title", "answer", "created_at")
    search_fields = ("question_title", "answer", "quiz__title")
    list_filter = ("quiz",)


@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    list_display = ("id", "quiz", "language", "duration", "created_at")
    search_fields = ("quiz__title",)
    list_filter = ("language",)


@admin.register(ProcessingLog)
class ProcessingLogAdmin(admin.ModelAdmin):
    list_display = ("id", "quiz", "status", "message", "created_at")
    search_fields = ("quiz__title", "message")
    list_filter = ("status",)
