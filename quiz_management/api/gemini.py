import json

from google import genai

from quiz_management.api.prompts import build_quiz_prompt
from quiz_management.api.schemas import QuizSchema


def generate_quiz(transcript: str) -> dict:
    """Generiert ein Quiz-JSON aus einem Transkript über die Gemini API.

    args:
        transcript (str): Der transkribierte Text (z. B. von Whisper).

    returns:
        dict: Die Quiz-Daten (title, description, questions).
    """
    client = genai.Client()

    interaction = client.interactions.create(
        model="gemini-3.1-flash-lite",
        input=build_quiz_prompt(transcript),
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": QuizSchema.model_json_schema(),
        },
    )

    return json.loads(interaction.output_text)
