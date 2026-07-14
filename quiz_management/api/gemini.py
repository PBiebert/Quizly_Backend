import json

from google import genai
from pydantic import BaseModel, Field

from quiz_management.api.prompts import build_quiz_prompt


class QuestionSchema(BaseModel):
    """Pydantic-Schema für eine einzelne Frage im Gemini-Response-JSON.

    question_options muss genau 4 Einträge enthalten.
    """

    question_title: str
    question_options: list[str] = Field(min_length=4, max_length=4)
    answer: str


class QuizSchema(BaseModel):
    """Pydantic-Schema für das Gemini-Response-JSON eines Quiz.

    Wird als response_format-Schema an die Gemini API übergeben, um die
    Struktur der generierten Quiz-Daten zu erzwingen. questions muss genau
    10 Einträge enthalten.
    """

    title: str
    description: str
    questions: list[QuestionSchema] = Field(min_length=10, max_length=10)


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
