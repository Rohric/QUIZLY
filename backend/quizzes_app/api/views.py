from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Quiz
from ..services.quiz_processor import create_quiz_from_url
from .serializers import QuizSerializer, QuizCreateSerializer


class QuizListCreateView(APIView):
    """API view to list all quizzes of the authenticated user or create a new one."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return all quizzes owned by the current user."""
        quizzes = Quiz.objects.filter(owner=request.user)
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Download, transcribe, and generate a quiz from a YouTube URL."""
        url = request.data.get("url")
        if not url:
            return Response({"detail": "URL is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quiz = create_quiz_from_url(request.user, url)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = QuizCreateSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class QuizDetailView(APIView):
    """API view to retrieve, update, or delete a single quiz."""

    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """Fetch a quiz by ID and verify ownership.

        Returns a (quiz, None) tuple on success or (None, error Response) if not found or forbidden."""
        try:
            quiz = Quiz.objects.get(pk=pk)
        except Quiz.DoesNotExist:
            return None, Response({"detail": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
        if quiz.owner != user:
            return None, Response({"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN)
        return quiz, None

    def get(self, request, pk):
        """Return a single quiz by ID."""
        quiz, error = self.get_object(pk, request.user)
        if error:
            return error
        serializer = QuizSerializer(quiz)
        return Response(serializer.data)

    def patch(self, request, pk):
        """Partially update a quiz (title or description)."""
        quiz, error = self.get_object(pk, request.user)
        if error:
            return error
        serializer = QuizSerializer(quiz, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete a quiz permanently."""
        quiz, error = self.get_object(pk, request.user)
        if error:
            return error
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
