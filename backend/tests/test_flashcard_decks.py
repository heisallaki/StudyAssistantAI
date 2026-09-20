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

VALID_FLASHCARDS_JSON = json.dumps(
    {
        "flashcards": [
            {"front": "What is a primary key?", "back": "A column that uniquely identifies each row."},
            {"front": "What does CPU stand for?", "back": "Central Processing Unit."},
            {"front": "What is normalization?", "back": "Organizing data to reduce redundancy."},
        ]
    }
)


class FakeAIProvider(AIProvider):
    def __init__(self, response: str = VALID_FLASHCARDS_JSON):
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


def _create_deck(headers, title="Databases"):
    response = client.post("/api/v1/decks", json={"title": title}, headers=headers)
    return response.json()


def test_create_deck(authenticated_user):
    response = client.post(
        "/api/v1/decks",
        json={"title": "Networking Basics", "description": "Core concepts"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Networking Basics"
    assert body["card_count"] == 0
    assert body["mastered_count"] == 0
    assert body["mastery_percentage"] == 0


def test_create_deck_with_invalid_subject_returns_404(authenticated_user):
    response = client.post(
        "/api/v1/decks",
        json={"title": "Orphan deck", "subject_id": str(uuid.uuid4())},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 404


def test_list_decks_returns_only_current_user_decks(authenticated_user):
    other_user = _register_and_login()
    try:
        _create_deck(authenticated_user["headers"], "Mine")
        _create_deck(other_user["headers"], "Theirs")

        response = client.get("/api/v1/decks", headers=authenticated_user["headers"])
        titles = [deck["title"] for deck in response.json()]
        assert titles == ["Mine"]
    finally:
        db = SessionLocal()
        db.query(User).filter(User.email == other_user["email"]).delete()
        db.commit()
        db.close()


def test_get_deck_returns_404_for_other_users_deck(authenticated_user):
    other_user = _register_and_login()
    try:
        deck = _create_deck(other_user["headers"])
        response = client.get(f"/api/v1/decks/{deck['id']}", headers=authenticated_user["headers"])
        assert response.status_code == 404
    finally:
        db = SessionLocal()
        db.query(User).filter(User.email == other_user["email"]).delete()
        db.commit()
        db.close()


def test_update_deck_title(authenticated_user):
    deck = _create_deck(authenticated_user["headers"])
    response = client.put(
        f"/api/v1/decks/{deck['id']}", json={"title": "Updated title"}, headers=authenticated_user["headers"]
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"


def test_delete_deck_cascades_flashcards(authenticated_user):
    deck = _create_deck(authenticated_user["headers"])
    client.post(
        f"/api/v1/decks/{deck['id']}/flashcards",
        json={"front": "Q", "back": "A"},
        headers=authenticated_user["headers"],
    )
    delete_response = client.delete(f"/api/v1/decks/{deck['id']}", headers=authenticated_user["headers"])
    assert delete_response.status_code == 204
    get_response = client.get(f"/api/v1/decks/{deck['id']}", headers=authenticated_user["headers"])
    assert get_response.status_code == 404


def test_add_flashcard_manual(authenticated_user):
    deck = _create_deck(authenticated_user["headers"])
    response = client.post(
        f"/api/v1/decks/{deck['id']}/flashcards",
        json={"front": "What is a foreign key?", "back": "A reference to another table's primary key."},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 201
    body = response.json()
    assert body["front"] == "What is a foreign key?"
    assert body["progress"]["status"] == "new"
    assert body["progress"]["times_reviewed"] == 0


def test_add_flashcard_to_missing_deck_returns_404(authenticated_user):
    response = client.post(
        f"/api/v1/decks/{uuid.uuid4()}/flashcards",
        json={"front": "Q", "back": "A"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 404


def test_update_flashcard(authenticated_user):
    deck = _create_deck(authenticated_user["headers"])
    card = client.post(
        f"/api/v1/decks/{deck['id']}/flashcards",
        json={"front": "Old front", "back": "Old back"},
        headers=authenticated_user["headers"],
    ).json()

    response = client.put(
        f"/api/v1/decks/{deck['id']}/flashcards/{card['id']}",
        json={"front": "New front"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 200
    body = response.json()
    assert body["front"] == "New front"
    assert body["back"] == "Old back"


def test_delete_flashcard(authenticated_user):
    deck = _create_deck(authenticated_user["headers"])
    card = client.post(
        f"/api/v1/decks/{deck['id']}/flashcards",
        json={"front": "Q", "back": "A"},
        headers=authenticated_user["headers"],
    ).json()

    response = client.delete(
        f"/api/v1/decks/{deck['id']}/flashcards/{card['id']}", headers=authenticated_user["headers"]
    )
    assert response.status_code == 204
    deck_after = client.get(f"/api/v1/decks/{deck['id']}", headers=authenticated_user["headers"]).json()
    assert deck_after["card_count"] == 0


def test_generate_flashcards_creates_cards_from_ai_response(authenticated_user, fake_ai):
    deck = _create_deck(authenticated_user["headers"])
    response = client.post(
        f"/api/v1/decks/{deck['id']}/flashcards/generate",
        json={"count": 3},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 201
    cards = response.json()
    assert len(cards) == 3
    assert cards[0]["front"] == "What is a primary key?"

    deck_after = client.get(f"/api/v1/decks/{deck['id']}", headers=authenticated_user["headers"]).json()
    assert deck_after["card_count"] == 3


def test_generate_flashcards_upstream_failure_returns_502(authenticated_user, failing_ai):
    deck = _create_deck(authenticated_user["headers"])
    response = client.post(
        f"/api/v1/decks/{deck['id']}/flashcards/generate",
        json={"count": 5},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 502


def test_generate_flashcards_invalid_ai_response_returns_502(authenticated_user):
    app.dependency_overrides[get_ai_provider] = lambda: FakeAIProvider(response="not valid json")
    try:
        deck = _create_deck(authenticated_user["headers"])
        response = client.post(
            f"/api/v1/decks/{deck['id']}/flashcards/generate",
            json={"count": 5},
            headers=authenticated_user["headers"],
        )
        assert response.status_code == 502
    finally:
        app.dependency_overrides.pop(get_ai_provider, None)


def test_review_queue_excludes_mastered_cards(authenticated_user):
    deck = _create_deck(authenticated_user["headers"])
    card = client.post(
        f"/api/v1/decks/{deck['id']}/flashcards",
        json={"front": "Q", "back": "A"},
        headers=authenticated_user["headers"],
    ).json()

    client.post(
        f"/api/v1/decks/{deck['id']}/flashcards/{card['id']}/review",
        json={"result": "good"},
        headers=authenticated_user["headers"],
    )
    client.post(
        f"/api/v1/decks/{deck['id']}/flashcards/{card['id']}/review",
        json={"result": "good"},
        headers=authenticated_user["headers"],
    )

    queue = client.get(f"/api/v1/decks/{deck['id']}/review-queue", headers=authenticated_user["headers"]).json()
    assert queue == []


def test_review_flashcard_good_twice_marks_mastered(authenticated_user):
    deck = _create_deck(authenticated_user["headers"])
    card = client.post(
        f"/api/v1/decks/{deck['id']}/flashcards",
        json={"front": "Q", "back": "A"},
        headers=authenticated_user["headers"],
    ).json()

    first = client.post(
        f"/api/v1/decks/{deck['id']}/flashcards/{card['id']}/review",
        json={"result": "good"},
        headers=authenticated_user["headers"],
    ).json()
    assert first["progress"]["status"] == "learning"

    second = client.post(
        f"/api/v1/decks/{deck['id']}/flashcards/{card['id']}/review",
        json={"result": "good"},
        headers=authenticated_user["headers"],
    ).json()
    assert second["progress"]["status"] == "mastered"
    assert second["progress"]["correct_streak"] == 2

    deck_after = client.get(f"/api/v1/decks/{deck['id']}", headers=authenticated_user["headers"]).json()
    assert deck_after["mastered_count"] == 1
    assert deck_after["mastery_percentage"] == 100


def test_review_flashcard_again_resets_streak(authenticated_user):
    deck = _create_deck(authenticated_user["headers"])
    card = client.post(
        f"/api/v1/decks/{deck['id']}/flashcards",
        json={"front": "Q", "back": "A"},
        headers=authenticated_user["headers"],
    ).json()

    client.post(
        f"/api/v1/decks/{deck['id']}/flashcards/{card['id']}/review",
        json={"result": "good"},
        headers=authenticated_user["headers"],
    )
    response = client.post(
        f"/api/v1/decks/{deck['id']}/flashcards/{card['id']}/review",
        json={"result": "again"},
        headers=authenticated_user["headers"],
    )
    body = response.json()
    assert body["progress"]["status"] == "learning"
    assert body["progress"]["correct_streak"] == 0
    assert body["progress"]["times_reviewed"] == 2


def test_review_nonexistent_flashcard_returns_404(authenticated_user):
    deck = _create_deck(authenticated_user["headers"])
    response = client.post(
        f"/api/v1/decks/{deck['id']}/flashcards/{uuid.uuid4()}/review",
        json={"result": "good"},
        headers=authenticated_user["headers"],
    )
    assert response.status_code == 404


def test_flashcards_require_authentication():
    response = client.get("/api/v1/decks")
    assert response.status_code == 401