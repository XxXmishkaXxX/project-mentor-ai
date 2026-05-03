import pytest

from app.chat.db import ChatModel
from app.store.store import Store
from app.users.db import UserModel
from tests.constants import OTHER_EMAIL, OTHER_PASSWORD, OTHER_USERNAME
from tests.integration.conftest import create_user_in_db


@pytest.fixture
async def chat(store: Store, user: UserModel) -> ChatModel:
    return await store.chat_accessor.create_chat(user.id)


@pytest.fixture
async def other_user(store: Store) -> UserModel:
    return await create_user_in_db(
        store,
        username=OTHER_USERNAME,
        email=OTHER_EMAIL,
        password=OTHER_PASSWORD,
    )
