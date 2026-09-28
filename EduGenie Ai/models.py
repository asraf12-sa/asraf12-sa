from pydantic import BaseModel, Field, field_validator


# =========================================================
# Request models
# =========================================================

class TextRequest(BaseModel):

    text: str = Field(
        min_length=3,
        max_length=20000
    )

    @field_validator("text")
    @classmethod
    def clean_text(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Text cannot be empty"
            )

        return value


class QARequest(BaseModel):

    question: str = Field(
        min_length=3,
        max_length=5000
    )

    @field_validator("question")
    @classmethod
    def clean_question(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Question cannot be empty"
            )

        return value


class ExplainRequest(BaseModel):

    topic: str = Field(
        min_length=2,
        max_length=3000
    )

    level: str = Field(
        default="beginner",
        max_length=50
    )


class QuizRequest(TextRequest):

    level: str = Field(
        default="beginner",
        max_length=50
    )


class SummaryRequest(TextRequest):
    pass


class LearnRequest(BaseModel):

    topic: str = Field(
        min_length=2,
        max_length=1000
    )

    level: str = Field(
        default="beginner",
        max_length=50
    )

    weeks: int = Field(
        default=6,
        ge=1,
        le=52
    )


# =========================================================
# Quiz models
# =========================================================

class QuizQuestion(BaseModel):

    question: str

    options: list[str] = Field(
        min_length=4,
        max_length=4
    )

    correct_answer: str

    explanation: str = ""


# =========================================================
# Response models
# =========================================================

class QAResponse(BaseModel):

    answer: str


class ExplainResponse(BaseModel):

    explanation: str


class QuizResponse(BaseModel):

    questions: list[QuizQuestion]


class SummaryResponse(BaseModel):

    summary: str


class LearnResponse(BaseModel):

    plan: str