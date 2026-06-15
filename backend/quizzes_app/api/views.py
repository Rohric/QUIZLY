import os

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import ProcessingLog, Question, Quiz, Transcript
from ..services.downloader import download_audio
from ..services.gemini import generate_quiz
from ..services.transcriber import transcribe
from .serializers import QuizSerializer


class QuizListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        url = request.data.get("url")
        if not url:
            return Response({"detail": "URL ist erforderlich."}, status=status.HTTP_400_BAD_REQUEST)

        quiz = Quiz.objects.create(owner=request.user, title="Wird verarbeitet...", video_url=url, status="processing")
        ProcessingLog.objects.create(quiz=quiz, status="download_started")

        try:
            audio_path = download_audio(url)
            ProcessingLog.objects.create(quiz=quiz, status="download_completed")

            ProcessingLog.objects.create(quiz=quiz, status="transcription_started")
            transcript_data = transcribe(audio_path)
            Transcript.objects.create(quiz=quiz, raw_text=transcript_data["text"], language=transcript_data["language"])
            ProcessingLog.objects.create(quiz=quiz, status="transcription_completed")

            ProcessingLog.objects.create(quiz=quiz, status="generation_started")
            quiz_data = generate_quiz(transcript_data["text"])
            ProcessingLog.objects.create(quiz=quiz, status="generation_completed")

            quiz.title = quiz_data["title"]
            quiz.description = quiz_data.get("description", "")
            quiz.status = "completed"
            quiz.save()

            for q in quiz_data["questions"]:
                Question.objects.create(
                    quiz=quiz,
                    question_title=q["question_title"],
                    question_options=q["question_options"],
                    answer=q["answer"],
                )

            ProcessingLog.objects.create(quiz=quiz, status="completed")

            if os.path.exists(audio_path):
                os.remove(audio_path)

            serializer = QuizSerializer(quiz)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            import traceback

            traceback.print_exc()
            quiz.status = "failed"
            quiz.save()
            ProcessingLog.objects.create(quiz=quiz, status="error", message=str(e))
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
