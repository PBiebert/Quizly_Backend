from django.conf import settings
from django.db import models


class Quiz(models.Model):
    """A quiz generated from a YouTube video, with its associated questions."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="quizzes", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=150)
    video_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    """A multiple-choice question with exactly 4 options, belonging to a quiz."""

    quiz = models.ForeignKey(Quiz, related_name="questions", on_delete=models.CASCADE)
    question_title = models.CharField(max_length=255)
    question_options = models.JSONField()
    answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_title
