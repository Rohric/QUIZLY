from rest_framework import serializers

from ..models import Question, Quiz


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for reading question data."""

    class Meta:
        model = Question
        fields = ["id", "question_title", "question_options", "answer"]


class QuestionCreateSerializer(serializers.ModelSerializer):
    """Serializer for question data including timestamps, used after quiz creation."""

    class Meta:
        model = Question
        fields = ["id", "question_title", "question_options", "answer", "created_at", "updated_at"]


class QuizSerializer(serializers.ModelSerializer):
    """Serializer for reading quiz data including nested questions."""

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "created_at", "updated_at", "video_url", "questions"]


class QuizCreateSerializer(serializers.ModelSerializer):
    """Serializer for the quiz creation response including full question details."""

    questions = QuestionCreateSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "created_at", "updated_at", "video_url", "questions"]
