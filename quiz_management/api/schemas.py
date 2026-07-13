from pydantic import BaseModel, Field


class QuestionSchema(BaseModel):
    question_title: str
    question_options: list[str] = Field(min_length=4, max_length=4)
    answer: str


class QuizSchema(BaseModel):
    title: str
    description: str
    questions: list[QuestionSchema] = Field(min_length=10, max_length=10)
