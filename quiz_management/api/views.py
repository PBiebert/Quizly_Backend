from rest_framework import generics, permissions
from rest_framework.permissions import AllowAny

# # /api/quizzes/


class QuizListCreateView(generics.ListCreateAPIView):
    # Prüfung ob user eingelogt ist
    permission_classes = [AllowAny]


# url holen
# ton runterladen
# ton in text umwandeln
# text an llm übergeben
# llm gibt titel, description und Anwortmöglichkeiten aus
# llm dagt welche antwort richtig ist
# daten an serilizer übergeben
# antwort warten und wenn valide response zurückgeben


# /api/quizzes/
# prüft ob user eingelogt ist
# filtert nach quiz welche zum user gehören
# gibt diese in den serilizer
# antwort warten und wenn valide response zurückgeben


# /api/quizzes/{id}/
# prüft ob user eingelogt ist
# filtert nach dem quiz {id}
