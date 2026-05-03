from unittest.mock import MagicMock

import pytest

from app.auth.manager import AuthManager


@pytest.fixture
def auth_manager(mock_store: MagicMock) -> AuthManager:
    return AuthManager(mock_store)
