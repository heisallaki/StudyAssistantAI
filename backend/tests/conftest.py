import os
from urllib.parse import urlsplit, urlunsplit

from app.core.config import get_settings


def _resolve_test_database_url() -> str:
    explicit = os.environ.get("TEST_DATABASE_URL")
    if explicit:
        return explicit

    base_url = get_settings().DATABASE_URL
    if not base_url:
        raise RuntimeError(
            "DATABASE_URL is not set. Set DATABASE_URL in backend/.env (used to derive a "
            "_test database) or set TEST_DATABASE_URL explicitly to run the test suite."
        )

    parts = urlsplit(base_url)
    if not parts.path or parts.path == "/":
        raise RuntimeError(
            f"DATABASE_URL has no database name to derive a test database from: {base_url}"
        )

    test_path = parts.path.rstrip("/") + "_test"
    return urlunsplit((parts.scheme, parts.netloc, test_path, parts.query, parts.fragment))


_test_database_url = _resolve_test_database_url()
_test_database_name = _test_database_url.rsplit("/", 1)[-1].split("?", 1)[0]

if "test" not in _test_database_name.lower():
    raise RuntimeError(
        "Refusing to run the test suite: the resolved test database name "
        f"('{_test_database_name}') does not contain 'test'. This check exists to prevent "
        "the test suite's table teardown from ever running against a real database. Set "
        "TEST_DATABASE_URL explicitly to a database whose name contains 'test'."
    )

os.environ["DATABASE_URL"] = _test_database_url
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
get_settings.cache_clear()

import pytest

from app.db.base import Base
from app.db.session import engine

from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.document import Document
from app.models.conversation import Conversation
from app.models.message import Message


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)