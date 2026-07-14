from rest_framework import serializers

from quiz_management.models import Question, Quiz


class QuestionSerializer(serializers.ModelSerializer):
    """ModelSerializer for Question."""

    class Meta:
        model = Question
        fields = [
            "id",
            "question_title",
            "question_options",
            "answer",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        """Validates the question_options/answer pair.

        Raises:
            serializers.ValidationError: If question_options does not
                contain exactly 4 unique entries, or answer is not one of
                question_options.
        """

        options = data.get("question_options", [])
        if len(set(options)) != 4:
            raise serializers.ValidationError(
                "'question_options' must contain exactly 4 distinct options."
            )
        if data.get("answer") not in options:
            raise serializers.ValidationError(
                "'answer' must match one of the 'question_options'."
            )
        return data


class QuestionCreateSerializer(QuestionSerializer):
    """QuestionSerializer subclass with additional read-only timestamp fields.

    Adds created_at and updated_at (format: "%Y-%m-%dT%H:%M:%S.%fZ") to
    the fields and validation inherited from QuestionSerializer.
    """

    created_at = serializers.DateTimeField(
        read_only=True, format="%Y-%m-%dT%H:%M:%S.%fZ"
    )
    updated_at = serializers.DateTimeField(
        read_only=True, format="%Y-%m-%dT%H:%M:%S.%fZ"
    )

    class Meta(QuestionSerializer.Meta):
        fields = QuestionSerializer.Meta.fields + ["created_at", "updated_at"]


class QuizSerializer(serializers.ModelSerializer):
    """ModelSerializer for Quiz including nested questions."""

    questions = QuestionSerializer(many=True)
    created_at = serializers.DateTimeField(
        read_only=True, format="%Y-%m-%dT%H:%M:%S.%fZ"
    )
    updated_at = serializers.DateTimeField(
        read_only=True, format="%Y-%m-%dT%H:%M:%S.%fZ"
    )

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_questions(self, value):
        """Checks that exactly 10 questions were provided.

        Raises:
            serializers.ValidationError: If value does not contain exactly
                10 entries.
        """

        if len(value) != 10:
            raise serializers.ValidationError(
                "Exactly 10 questions are required."
            )
        return value

    def create(self, validated_data):
        """Creates a quiz and its associated question objects."""

        questions_data = validated_data.pop("questions")
        quiz = Quiz.objects.create(**validated_data)
        Question.objects.bulk_create(
            Question(quiz=quiz, **question_data) for question_data in questions_data
        )
        return quiz


class QuizCreateSerializer(QuizSerializer):
    """QuizSerializer subclass using QuestionCreateSerializer as the nested serializer."""

    questions = QuestionCreateSerializer(many=True)
