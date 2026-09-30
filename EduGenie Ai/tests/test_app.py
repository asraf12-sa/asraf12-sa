from fastapi.testclient import TestClient

from config import Settings
from gemini_client import GeminiService
from main import app


client = TestClient(app)


def test_default_gemini_model_is_supported():
    assert Settings().gemini_model == "gemini-2.5-flash"


def test_settings_reads_from_env_file(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-from-env")
    settings = Settings(GEMINI_API_KEY="test-key-from-env")
    assert settings.gemini_api_key == "test-key-from-env"


def test_gemini_retries_with_fallback_model(monkeypatch):
    calls = []

    class FakeResponse:
        text = "Recovered response"

    def fake_generate_with_model(self, model_name, prompt, system_instruction=None):
        calls.append(model_name)
        if model_name == "gemini-2.5-flash":
            raise RuntimeError("503 UNAVAILABLE")
        return FakeResponse()

    monkeypatch.setattr(
        "gemini_client.GeminiService._generate_with_model",
        fake_generate_with_model,
    )

    service = GeminiService.__new__(GeminiService)
    service.settings = Settings(gemini_model="gemini-2.5-flash")
    service.client = object()

    response = service.generate("hello")

    assert response == "Recovered response"
    assert calls == ["gemini-2.5-flash", "gemini-1.5-flash"]


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_home():

    response = client.get("/")

    assert response.status_code == 200

    assert "EduGenie" in response.text


def test_favicon():
    response = client.get("/favicon.ico")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/svg+xml"
    assert "<svg" in response.text


def test_invalid_question():

    response = client.post(
        "/qa",
        json={
            "question": ""
        }
    )

    assert response.status_code == 422


def test_invalid_quiz_request():

    response = client.post(
        "/quiz",
        json={
            "text": ""
        }
    )

    assert response.status_code == 422


def test_gemini_unavailable_returns_retryable_error(monkeypatch):
    class ProviderUnavailableError(Exception):
        status_code = 503

    def fail_quiz_generation(*args):
        raise ProviderUnavailableError("temporarily unavailable")

    monkeypatch.setattr("main.generate_quiz", fail_quiz_generation)

    response = TestClient(
        app,
        raise_server_exceptions=False,
    ).post(
        "/quiz",
        json={
            "text": "A passage about photosynthesis.",
            "level": "advanced",
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Gemini is temporarily unavailable. Please try again shortly."
    )
    assert response.headers["retry-after"] == "30"


def test_google_client_error_is_treated_as_retryable(monkeypatch):
    class GoogleClientError(Exception):
        status_code = 503

    def fail_quiz_generation(*args):
        raise GoogleClientError("UNAVAILABLE")

    monkeypatch.setattr("main.generate_quiz", fail_quiz_generation)

    response = TestClient(
        app,
        raise_server_exceptions=False,
    ).post(
        "/quiz",
        json={
            "text": "A passage about photosynthesis.",
            "level": "advanced",
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Gemini is temporarily unavailable. Please try again shortly."
    )
    assert response.headers["retry-after"] == "30"


def test_invalid_learning_duration():

    response = client.post(
        "/learn/recommendations",
        json={
            "topic": "Python",
            "level": "beginner",
            "weeks": 100
        }
    )

    assert response.status_code == 422