from rest_framework import serializers

from quiz_management.models import Question, Quiz


class QuestionSerializer(serializers.ModelSerializer):
    """ModelSerializer für Question."""

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
        """Validiert das question_options und answer-Paar.

        Raises:
            serializers.ValidationError: Wenn question_options nicht genau
                4 eindeutige Einträge enthält oder answer nicht in
                question_options vorkommt.
        """

        options = data.get("question_options", [])
        if len(set(options)) != 4:
            raise serializers.ValidationError(
                "'question_options' müssen genau 4 unterschiedliche Optionen enthalten."
            )
        if data.get("answer") not in options:
            raise serializers.ValidationError(
                "'answer' muss einer der 'question_options' entsprechen."
            )
        return data


class QuestionCreateSerializer(QuestionSerializer):
    """
    QuestionSerializer-Subklasse mit zusätzlichen read-only Timestamp-Feldern.

    Ergänzt created_at und updated_at (Format: "%Y-%m-%dT%H:%M:%S.%fZ") zu
    den von QuestionSerializer geerbten Feldern und der Validierung.
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
    """ModelSerializer für Quiz inkl. nested Questions."""

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
        """
        Prüft, dass genau 10 Questions übergeben wurden.

        Raises:
            serializers.ValidationError: Wenn value nicht genau 10 Einträge
                enthält.
        """

        if len(value) != 10:
            raise serializers.ValidationError(
                "Es müssen exakt 10 Fragen vorhanden sein."
            )
        return value

    def create(self, validated_data):
        """Erstellt ein Quiz und die zugehörigen Question-Objekte."""

        questions_data = validated_data.pop("questions")
        quiz = Quiz.objects.create(**validated_data)
        Question.objects.bulk_create(
            Question(quiz=quiz, **question_data) for question_data in questions_data
        )
        return quiz


class QuizCreateSerializer(QuizSerializer):
    """QuizSerializer-Subklasse mit QuestionCreateSerializer als nested Serializer."""

    questions = QuestionCreateSerializer(many=True)
