import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.repositories.users import UserRepository
from app.models import User


class MockSession:
    """Mock SQLAlchemy session."""
    async def execute(self, *args, **kwargs):
        return MagicMock()


@pytest.mark.asyncio
async def test_get_by_email():
    # Setup
    mock_session = MockSession()
    mock_user = User(id=1, email="test@example.com", full_name="Test User")

    # Mock SQLAlchemy Result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user

    # Patch SQLAlchemy Repository retrieve method
    with patch("app.repositories.users.SQLAlchemyRepository.retrieve", AsyncMock(return_value=mock_result)) as mock_retrieve:
        # Initialize Repository
        repo = UserRepository(session=mock_session)

        # Execute Method
        result = await repo.get_by_email(email="test@example.com")

        # Assertions
        assert result == mock_user
        mock_retrieve.assert_called_once_with(return_result=True, email="test@example.com")
