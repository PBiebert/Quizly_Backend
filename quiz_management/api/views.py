import whisper
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from quiz_management.api.gemini import generate_quiz
from quiz_management.api.serializers import QuizSerializer
from quiz_management.api.youtube import delete_temp_audio, download_audio
from quiz_management.models import Quiz

# # /api/quizzes/


class QuizListCreateView(generics.ListCreateAPIView):
    # Prüfung ob user eingelogt ist
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # filtert nach quiz welche zum eingeloggten user gehören
        return Quiz.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        # url holen
        url = request.data.get("url")
        # ton runterladen
        audio_path = download_audio(url)
        # ton in text umwandeln -> model später ändern nur für die entwicklung !
        model = whisper.load_model("turbo")
        transcription = model.transcribe(audio_path)
        # audio löschen, wird nicht mehr benötigt
        delete_temp_audio(audio_path)

        # transkript an gemini übergeben, quiz-json erzeugen lassen
        quiz_data = generate_quiz(transcription["text"])
        # video_url ergänzen, kommt nicht von gemini, sondern aus dem request
        quiz_data["video_url"] = url

        # daten an serializer übergeben und struktur validieren
        serializer = self.get_serializer(data=quiz_data)
        serializer.is_valid(raise_exception=True)
        # quiz dem eingeloggten user zuordnen und speichern
        serializer.save(user=request.user)

        # gespeichertes quiz zurückgeben
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# /api/quizzes/
# prüft ob user eingelogt ist
# filtert nach quiz welche zum user gehören
# gibt diese in den serilizer
# antwort warten und wenn valide response zurückgeben


# /api/quizzes/{id}/
# prüft ob user eingelogt ist
# filtert nach dem quiz {id}
