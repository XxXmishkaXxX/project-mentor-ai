import pytest

from app.store.store import Store
from tests.constants import DEFAULT_EMAIL, DEFAULT_PASSWORD, DEFAULT_USERNAME
from tests.integration.conftest import create_user_in_db


@pytest.fixture
async def registered_user(store: Store):
    return await create_user_in_db(
        store,
        username=DEFAULT_USERNAME,
        email=DEFAULT_EMAIL,
        password=DEFAULT_PASSWORD,
    )
