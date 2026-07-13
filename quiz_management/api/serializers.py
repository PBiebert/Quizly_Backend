from rest_framework import serializers

from quiz_management.models import Question, Quiz


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "question_title",
            "question_options",
            "answer",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
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


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

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
        if len(value) != 10:
            raise serializers.ValidationError(
                "Es müssen exakt 10 Fragen vorhanden sein."
            )
        return value

    def create(self, validated_data):
        questions_data = validated_data.pop("questions")
        quiz = Quiz.objects.create(**validated_data)
        Question.objects.bulk_create(
            Question(quiz=quiz, **question_data) for question_data in questions_data
        )
        return quiz
