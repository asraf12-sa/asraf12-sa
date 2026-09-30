import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from explanation_module import explain_topic
from learning_path import get_learning_recommendations
from models import (
    ExplainRequest,
    LearnRequest,
    QuizRequest,
    QuizResponse,
    QARequest,
    SummaryRequest,
)
from qna import answer_question
from quiz_module import generate_quiz
from summary_module import summarize_text

app = FastAPI()
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templetes")
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static" / "css"),
    name="static",
)


@app.exception_handler(Exception)
async def handle_unexpected_error(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unhandled error while processing %s %s",
        request.method,
        request.url.path,
        exc_info=exc,
    )

    status_code = getattr(exc, "status_code", None)
    if status_code is None:
        status_code = getattr(exc, "code", None)

    error_message = str(exc).lower()
    retryable = status_code in {429, 500, 503} or any(
        marker in error_message
        for marker in (
            "temporarily unavailable",
            "unavailable",
            "rate limit",
            "overloaded",
            "quota",
            "high demand",
            "too many requests",
        )
    )

    if retryable:
        return JSONResponse(
            status_code=503,
            headers={"Retry-After": "30"},
            content={
                "detail": (
                    "Gemini is temporarily unavailable. Please try again shortly."
                )
            },
        )

    return JSONResponse(
        status_code=500,
        content={
            "detail": (
                "The AI request failed. Check the server console for details "
                "about the API key, model, quota, or network connection."
            )
        },
    )


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(
        BASE_DIR / "static" / "css" / "favicon.svg",
        media_type="image/svg+xml",
    )


@app.post("/qa")
def qa(payload: QARequest):
    return {"answer": answer_question(payload.question)}


@app.post("/explain")
def explain(payload: ExplainRequest):
    return {
        "explanation": explain_topic(
            payload.topic,
            payload.level,
        )
    }


@app.post("/quiz", response_model=QuizResponse)
def quiz(payload: QuizRequest):
    return {
        "questions": generate_quiz(
            payload.text,
            payload.level,
        )
    }


@app.post("/summarize")
def summarize(payload: SummaryRequest):
    return {"summary": summarize_text(payload.text)}


@app.post("/learn/recommendations")
def learning_recommendations(payload: LearnRequest):
    return {
        "plan": get_learning_recommendations(
            payload.topic,
            payload.level,
            payload.weeks,
        )
    }