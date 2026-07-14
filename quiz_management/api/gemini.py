import json

from google import genai
from pydantic import BaseModel, Field

from quiz_management.api.prompts import build_quiz_prompt


class QuestionSchema(BaseModel):
    """Pydantic schema for a single question in the Gemini response JSON.

    question_options must contain exactly 4 entries.
    """

    question_title: str
    question_options: list[str] = Field(min_length=4, max_length=4)
    answer: str


class QuizSchema(BaseModel):
    """Pydantic schema for the Gemini response JSON of a quiz.

    Passed as the response_format schema to the Gemini API to enforce the
    structure of the generated quiz data. questions must contain exactly
    10 entries.
    """

    title: str
    description: str
    questions: list[QuestionSchema] = Field(min_length=10, max_length=10)


def generate_quiz(transcript: str) -> dict:
    """Generates a quiz JSON from a transcript via the Gemini API.

    args:
        transcript (str): The transcribed text (e.g. from Whisper).

    returns:
        dict: The quiz data (title, description, questions).
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
