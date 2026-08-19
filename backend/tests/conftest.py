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