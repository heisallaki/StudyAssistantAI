import json

from pydantic import BaseModel, Field, field_validator

VALID_QUESTION_TYPES = {"multiple_choice", "true_false", "short_answer"}


class GeneratedQuestion(BaseModel):
    question_type: str
    prompt: str
    options: list[str] = Field(default_factory=list)
    correct_answer: str
    explanation: str = ""

    @field_validator("question_type")
    @classmethod
    def validate_question_type(cls, value: str) -> str:
        if value not in VALID_QUESTION_TYPES:
            raise ValueError(f"invalid question_type: {value}")
        return value


class GeneratedQuiz(BaseModel):
    questions: list[GeneratedQuestion]


def _is_question_valid(question: GeneratedQuestion) -> bool:
    if question.question_type == "multiple_choice":
        return len(question.options) >= 2 and question.correct_answer in question.options
    if question.question_type == "true_false":
        return question.correct_answer.strip().lower() in {"true", "false"}
    return bool(question.correct_answer.strip())


def parse_generated_quiz(raw_text: str) -> list[GeneratedQuestion]:
    data = json.loads(raw_text)
    parsed = GeneratedQuiz.model_validate(data)
    return [question for question in parsed.questions if _is_question_valid(question)]