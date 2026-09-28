from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


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