import json
import uuid

import pytest
from fastapi.testclient import TestClient

from app.ai.providers.base import AIProvider, AIProviderError
from app.api.deps import get_ai_provider
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)

VALID_QUIZ_JSON = json.dumps(
    {
        "questions": [
            {
                "question_type": "multiple_choice",
                "prompt": "What does SQL stand for?",
                "options": [
                    "Structured Query Language",
                    "Simple Query Language",
                    "Standard Query Logic",
                    "System Query Language",
                ],
                "correct_answer": "Structured Query Language",
                "explanation": "SQL stands for Structured Query Language.",
            },
            {
                "question_type": "true_false",
                "prompt": "A primary key can contain duplicate values.",
                "correct_answer": "false",
                "explanation": "Primary keys must be unique.",
            },
            {
                "question_type": "short_answer",
                "prompt": "Name the capital of France.",
                "correct_answer": "Paris",
                "explanation": "Paris is the capital of France.",
            },
        ]
    }
)


class FakeAIProvider(AIProvider):
    def __init__(self, response: str = VALID_QUIZ_JSON):
        self.response = response

    async def generate_reply(self, messages, response_format=None):
        return self.response


class FailingAIProvider(AIProvider):
    async def generate_reply(self, messages, response_format=None):
        raise AIProviderError("Could not reach the local AI model.")


def _register_and_login():
    email = f"{uuid.uuid4()}@example.com"
    password = "S3curePassw0rd!"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login_response.json()["access_token"]
    return {"email": email, "headers": {"Authorization": f"Bearer {token}"}}


@pytest.fixture
def authenticated_user():
    user = _register_and_login()
    yield user
    db = SessionLocal()
    db.query(User).filter(User.email == user["email"]).delete()
    db.commit()
    db.close()


@pytest.fixture
def fake_ai():
    provider = FakeAIProvider()
    app.dependency_overrides[get_ai_provider] = lambda: provider
    yield provider
    app.dependency_overrides.pop(get_ai_provider, None)


@pytest.fixture
def failing_ai():
    app.dependency_overrides[get_ai_provider] = lambda: FailingAIProvider()
    yield
    app.dependency_overrides.pop(get_ai_provider, None)


def _create_quiz(headers):
    response = client.post("/api/v1/quizzes", json={}, headers=headers)
    return response.json()


def _start_attempt(quiz_id, headers):
    response = client.post(f"/api/v1/quizzes/{quiz_id}/attempts", headers=headers)
    return response


def test_start_attempt_creates_in_progress_attempt_with_hidden_results(authenticated_user, fake_ai):
    quiz = _create_quiz(authenticated_user["headers"])
    response = _start_attempt(quiz["id"], authenticated_user["headers"])
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "in_progress"
    assert body["score"] is None
    assert body["total_questions"] == 3
    assert len(body["answers"]) == 3
    for answer in body["answers"]:
        assert answer["is_correct"] is None
        assert answer["correct_answer"] is None
        assert answer["explanation"] is None


def test_start_attempt_returns_404_for_missing_quiz(authenticated_user):
    response = _start_attempt(uuid.uuid4(), authenticated_user["headers"])
    assert response.status_code == 404


def test_start_attempt_rejects_quiz_that_failed_generation(authenticated_user, failing_ai):
    quiz = _create_quiz(authenticated_user["headers"])
    assert quiz["generation_status"] == "failed"
    response = _start_attempt(quiz["id"], authenticated_user["headers"])
    assert response.status_code == 400


def test_submit_answer_does_not_reveal_correctness_before_completion(authenticated_user, fake_ai):
    quiz = _create_quiz(authenticated_user["headers"])
    attempt = _start_attempt(quiz["id"], authenticated_user["headers"]).json()
    question_id = quiz["questions"][0]["id"]

    response = client.put(
        f"/api/v1/quiz-attempts/{attempt['id']}/answers/{question_id}",
        json={"submitted_answer": "Structured Query Language"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    answered = next(item for item in body["answers"] if item["question_id"] == question_id)
    assert answered["submitted_answer"] == "Structured Query Language"
    assert answered["is_correct"] is None


def test_submit_answer_upserts_existing_answer(authenticated_user, fake_ai):
    quiz = _create_quiz(authenticated_user["headers"])
    attempt = _start_attempt(quiz["id"], authenticated_user["headers"]).json()
    question_id = quiz["questions"][0]["id"]

    client.put(
        f"/api/v1/quiz-attempts/{attempt['id']}/answers/{question_id}",
        json={"submitted_answer": "Simple Query Language"},
        headers=authenticated_user["headers"],
    )
    response = client.put(
        f"/api/v1/quiz-attempts/{attempt['id']}/answers/{question_id}",
        json={"submitted_answer": "Structured Query Language"},
        headers=authenticated_user["headers"],
    )
    body = response.json()
    answered = next(item for item in body["answers"] if item["question_id"] == question_id)
    assert answered["submitted_answer"] == "Structured Query Language"
    assert len(body["answers"]) == 3


def test_submit_answer_rejects_question_from_another_quiz(authenticated_user, fake_ai):
    quiz = _create_quiz(authenticated_user["headers"])
    attempt = _start_attempt(quiz["id"], authenticated_user["headers"]).json()

    response = client.put(
        f"/api/v1/quiz-attempts/{attempt['id']}/answers/{uuid.uuid4()}",
        json={"submitted_answer": "anything"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 404


def test_submit_answer_rejected_after_attempt_completed(authenticated_user, fake_ai):
    quiz = _create_quiz(authenticated_user["headers"])
    attempt = _start_attempt(quiz["id"], authenticated_user["headers"]).json()
    question_id = quiz["questions"][0]["id"]

    client.post(f"/api/v1/quiz-attempts/{attempt['id']}/complete", headers=authenticated_user["headers"])
    response = client.put(
        f"/api/v1/quiz-attempts/{attempt['id']}/answers/{question_id}",
        json={"submitted_answer": "Structured Query Language"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 400


def test_complete_attempt_grades_answers_and_computes_score(authenticated_user, fake_ai):
    quiz = _create_quiz(authenticated_user["headers"])
    attempt = _start_attempt(quiz["id"], authenticated_user["headers"]).json()
    mc_question = quiz["questions"][0]["id"]
    tf_question = quiz["questions"][1]["id"]
    sa_question = quiz["questions"][2]["id"]

    client.put(
        f"/api/v1/quiz-attempts/{attempt['id']}/answers/{mc_question}",
        json={"submitted_answer": "Structured Query Language"},
        headers=authenticated_user["headers"],
    )
    client.put(
        f"/api/v1/quiz-attempts/{attempt['id']}/answers/{tf_question}",
        json={"submitted_answer": "true"},
        headers=authenticated_user["headers"],
    )
    client.put(
        f"/api/v1/quiz-attempts/{attempt['id']}/answers/{sa_question}",
        json={"submitted_answer": "  paris  "},
        headers=authenticated_user["headers"],
    )

    response = client.post(f"/api/v1/quiz-attempts/{attempt['id']}/complete", headers=authenticated_user["headers"])
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["score"] == 2
    assert body["total_questions"] == 3
    assert body["percentage_score"] == 67
    assert body["completed_at"] is not None

    results_by_question = {item["question_id"]: item for item in body["answers"]}
    assert results_by_question[mc_question]["is_correct"] is True
    assert results_by_question[tf_question]["is_correct"] is False
    assert results_by_question[tf_question]["correct_answer"] == "false"
    assert results_by_question[sa_question]["is_correct"] is True
    assert results_by_question[sa_question]["explanation"] == "Paris is the capital of France."


def test_complete_attempt_marks_unanswered_questions_incorrect(authenticated_user, fake_ai):
    quiz = _create_quiz(authenticated_user["headers"])
    attempt = _start_attempt(quiz["id"], authenticated_user["headers"]).json()

    response = client.post(f"/api/v1/quiz-attempts/{attempt['id']}/complete", headers=authenticated_user["headers"])
    body = response.json()
    assert body["score"] == 0
    assert all(item["is_correct"] is False for item in body["answers"])
    assert all(item["submitted_answer"] == "" for item in body["answers"])


def test_complete_attempt_is_idempotent(authenticated_user, fake_ai):
    quiz = _create_quiz(authenticated_user["headers"])
    attempt = _start_attempt(quiz["id"], authenticated_user["headers"]).json()
    mc_question = quiz["questions"][0]["id"]

    client.put(
        f"/api/v1/quiz-attempts/{attempt['id']}/answers/{mc_question}",
        json={"submitted_answer": "Structured Query Language"},
        headers=authenticated_user["headers"],
    )
    first = client.post(f"/api/v1/quiz-attempts/{attempt['id']}/complete", headers=authenticated_user["headers"])
    second = client.post(f"/api/v1/quiz-attempts/{attempt['id']}/complete", headers=authenticated_user["headers"])
    assert first.json()["score"] == second.json()["score"]
    assert first.json()["completed_at"] == second.json()["completed_at"]


def test_get_attempt_detail_requires_ownership(authenticated_user, fake_ai):
    other_user = _register_and_login()
    try:
        quiz = _create_quiz(other_user["headers"])
        attempt = _start_attempt(quiz["id"], other_user["headers"]).json()

        response = client.get(
            f"/api/v1/quiz-attempts/{attempt['id']}", headers=authenticated_user["headers"]
        )
        assert response.status_code == 404
    finally:
        db = SessionLocal()
        db.query(User).filter(User.email == other_user["email"]).delete()
        db.commit()
        db.close()


def test_list_attempts_returns_history_for_current_user(authenticated_user, fake_ai):
    quiz = _create_quiz(authenticated_user["headers"])
    _start_attempt(quiz["id"], authenticated_user["headers"])
    _start_attempt(quiz["id"], authenticated_user["headers"])

    response = client.get("/api/v1/quiz-attempts", headers=authenticated_user["headers"])
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["quiz_title"] == quiz["title"]


def test_list_attempts_filters_by_quiz_id(authenticated_user, fake_ai):
    quiz_one = _create_quiz(authenticated_user["headers"])
    quiz_two = _create_quiz(authenticated_user["headers"])
    _start_attempt(quiz_one["id"], authenticated_user["headers"])
    _start_attempt(quiz_two["id"], authenticated_user["headers"])

    response = client.get(
        "/api/v1/quiz-attempts", params={"quiz_id": quiz_one["id"]}, headers=authenticated_user["headers"]
    )
    body = response.json()
    assert len(body) == 1
    assert body[0]["quiz_id"] == quiz_one["id"]


def test_list_attempts_filters_by_subject_id(authenticated_user, fake_ai):
    subject_response = client.post(
        "/api/v1/subjects", json={"name": "Databases"}, headers=authenticated_user["headers"]
    )
    subject_id = subject_response.json()["id"]

    quiz_with_subject = client.post(
        "/api/v1/quizzes", json={"subject_id": subject_id}, headers=authenticated_user["headers"]
    ).json()
    quiz_without_subject = _create_quiz(authenticated_user["headers"])
    _start_attempt(quiz_with_subject["id"], authenticated_user["headers"])
    _start_attempt(quiz_without_subject["id"], authenticated_user["headers"])

    response = client.get(
        "/api/v1/quiz-attempts", params={"subject_id": subject_id}, headers=authenticated_user["headers"]
    )
    body = response.json()
    assert len(body) == 1
    assert body[0]["subject_id"] == subject_id


def test_quiz_attempts_require_authentication():
    response = client.get("/api/v1/quiz-attempts")
    assert response.status_code == 401