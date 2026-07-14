import whisper
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from quiz_management.api.gemini import generate_quiz
from quiz_management.api.permissions import IsQuizOwner
from quiz_management.api.serializers import QuizCreateSerializer, QuizSerializer
from quiz_management.api.youtube import delete_temp_audio, download_audio
from quiz_management.models import Quiz


class QuizListCreateView(generics.ListCreateAPIView):
    """Listet die Quizze des eingeloggten Users und erstellt neue Quizze aus einer Video-URL.

    GET liefert alle Quizze des Requesters über QuizSerializer.
    POST lädt das Audio der übergebenen URL herunter, transkribiert es via
    Whisper, lässt daraus über Gemini ein Quiz generieren und speichert es
    über QuizCreateSerializer.
    """

    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Gibt die Quiz-QuerySet gefiltert auf den eingeloggten User zurück."""

        return Quiz.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """
        Wählt den Serializer abhängig von der HTTP-Methode.

        Returns:
            QuizCreateSerializer bei POST (inkl. Timestamps bei den
            nested Questions), sonst QuizSerializer.
        """
        if self.request.method == "POST":
            return QuizCreateSerializer
        return QuizSerializer

    def post(self, request, *args, **kwargs):
        """
        Erstellt ein Quiz aus der im Request-Body übergebenen Video-URL.

        Ablauf: URL validieren, Audio herunterladen, per Whisper
        transkribieren, Transkript an Gemini übergeben um die Quiz-Daten
        zu generieren, temporäre Audiodatei löschen und das Ergebnis dem
        eingeloggten User zugeordnet speichern.
        """

        url = request.data.get("url")
        try:
            URLValidator()(url)
        except (ValidationError, TypeError):
            return Response(
                {"detail": "Ungültige URL oder Anfragedaten."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        audio_path = download_audio(url)
        model = whisper.load_model("turbo")
        transcription = model.transcribe(audio_path)
        delete_temp_audio(audio_path)

        quiz_data = generate_quiz(transcription["text"])
        quiz_data["video_url"] = url

        serializer = self.get_serializer(data=quiz_data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """
        Gibt alle Quizze des eingeloggten Users zurück.
        """

        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Ruft ein einzelnes Quiz ab, aktualisiert es teilweise oder löscht es."""

    http_method_names = ["get", "patch", "delete"]
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsQuizOwner]
    queryset = Quiz.objects.all()
