from django.contrib import admin

from .models import Question, Quiz


class QuizAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "video_url", "created_at", "updated_at")


class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "question_title", "quiz", "answer", "created_at", "updated_at")


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
