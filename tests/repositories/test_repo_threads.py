import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from app.repositories.threads import ThreadRepository, MessageRepository
from app.models import Thread


class MockSession:
    """Mock SQLAlchemy session."""
    async def execute(self, *args, **kwargs):
        return MagicMock()


@pytest.mark.asyncio
async def test_get_thread_with_messages():
    # Setup
    mock_session = MockSession()
    thread_id = uuid4()
    mock_thread = Thread(id=thread_id, title="Test Thread", messages=[])

    # Mock Result
    mock_result = MagicMock()
    mock_result.unique.return_value.scalar_one.return_value = mock_thread

    # Mock Patching
    with patch.object(mock_session, "execute", AsyncMock(return_value=mock_result)), \
         patch("app.repositories.threads.ThreadRepository.fetch_data", AsyncMock(return_value=mock_thread)):
        # Initialize Repository
        repo = ThreadRepository(session=mock_session)

        # Execute Method
        result = await repo.get_thread_with_messages(id=thread_id)

        # Assertions
        assert result == mock_thread
        mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_message_repository_list():
    # Setup
    mock_session = MockSession()
    mock_paginate = AsyncMock(return_value={"items": [], "total": 0, "page": 1, "per_page": 10})

    # Initialize Repository
    mock_message_repo = MessageRepository(session=mock_session)

    # Mock Patching
    with patch("app.repositories.mixins.paginate", mock_paginate), \
         patch("sqlalchemy.sql.selectable.Select", MagicMock()):
        # Execute Method
        result = await mock_message_repo.list(page=1, per_page=10, thread_id="test-thread-id")

        # Assertions
        assert result == {"items": [], "total": 0, "page": 1, "per_page": 10}

