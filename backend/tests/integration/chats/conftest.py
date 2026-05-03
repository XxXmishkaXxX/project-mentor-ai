import pytest

from app.chat.domain.models import Chat
from app.store.store import Store
from app.users.domain.models import User
from tests.constants import OTHER_EMAIL, OTHER_PASSWORD, OTHER_USERNAME
from tests.integration.conftest import create_user_in_db


@pytest.fixture
async def chat(store: Store, user: User) -> Chat:
    return await store.chat_accessor.create_chat(user.id)


@pytest.fixture
async def other_user(store: Store) -> User:
    return await create_user_in_db(
        store,
        username=OTHER_USERNAME,
        email=OTHER_EMAIL,
        password=OTHER_PASSWORD,
    )
