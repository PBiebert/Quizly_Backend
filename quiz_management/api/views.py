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
    """Lists the logged-in user's quizzes and creates new quizzes from a video URL.

    GET returns all quizzes belonging to the requester via QuizSerializer.
    POST downloads the audio for the given URL, transcribes it via
    Whisper, generates the quiz data from the transcript via Gemini, and
    saves it via QuizCreateSerializer.
    """

    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Returns the Quiz queryset filtered to the logged-in user."""

        return Quiz.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Selects the serializer based on the HTTP method.

        Returns:
            QuizCreateSerializer for POST (including timestamps on the
            nested questions), otherwise QuizSerializer.
        """
        if self.request.method == "POST":
            return QuizCreateSerializer
        return QuizSerializer

    def post(self, request, *args, **kwargs):
        """Creates a quiz from the video URL given in the request body.

        Flow: validate the URL, download the audio, transcribe it via
        Whisper, pass the transcript to Gemini to generate the quiz data,
        delete the temporary audio file, and save the result assigned to
        the logged-in user.
        """

        url = request.data.get("url")
        try:
            URLValidator()(url)
        except (ValidationError, TypeError):
            return Response(
                {"detail": "Invalid URL or request data."},
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
        """Returns all quizzes belonging to the logged-in user."""

        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieves a single quiz, partially updates it, or deletes it."""

    http_method_names = ["get", "patch", "delete"]
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsQuizOwner]
    queryset = Quiz.objects.all()
