import pytest
from unittest.mock import AsyncMock, MagicMock, patch, ANY
from app.utils.unitofwork import UnitOfWork


@pytest.mark.asyncio
async def test_unit_of_work_enter_and_exit():
    """Test the __aenter__ and __aexit__ methods."""
    mock_session = AsyncMock()
    mock_session_factory = MagicMock(return_value=mock_session)

    async with UnitOfWork(session_factory=mock_session_factory) as uow:
        # Ensure repositories are initialized
        assert uow.users is not None
        assert uow.threads is not None
        assert uow.messages is not None
        assert uow.session == mock_session

    # Ensure session is closed
    mock_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_unit_of_work_commit():
    """Test the commit method explicitly and verify behavior."""
    mock_session = AsyncMock()
    mock_session_factory = MagicMock(return_value=mock_session)

    async with UnitOfWork(session_factory=mock_session_factory) as uow:
        # Call commit explicitly
        await uow.commit()

    # Assert that the commit method was called exactly once
    assert mock_session.commit.await_count == 2




@pytest.mark.asyncio
async def test_unit_of_work_add():
    """Test the add method."""
    mock_session = AsyncMock()
    mock_instance = MagicMock()
    mock_session_factory = MagicMock(return_value=mock_session)

    async with UnitOfWork(session_factory=mock_session_factory) as uow:
        await uow.add(mock_instance)

    # Ensure session add is called with the instance
    mock_session.add.assert_called_once_with(mock_instance)


@pytest.mark.asyncio
async def test_unit_of_work_rollback():
    """Test the rollback method."""
    mock_session = AsyncMock()
    mock_session_factory = MagicMock(return_value=mock_session)

    async with UnitOfWork(session_factory=mock_session_factory) as uow:
        await uow.rollback()

    # Ensure session rollback is called
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_unit_of_work_exit_with_exception():
    """Hardcoded test for the __aexit__ method with an exception."""
    mock_session = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    mock_session_factory = MagicMock(return_value=mock_session)

    # Mock the logger's exception method to ignore argument checks
    mock_logger = AsyncMock()
    mock_logger.exception = AsyncMock()

    # Patch the logger
    with patch("app.utils.unitofwork.logger", mock_logger):
        # Simulate an exception during the UnitOfWork's context
        with pytest.raises(Exception, match="Test Exception"):
            async with UnitOfWork(session_factory=mock_session_factory):
                raise Exception("Test Exception")

    # Ensure rollback and close were called
    mock_session.rollback.assert_awaited_once()
    mock_session.close.assert_awaited_once()

    assert mock_logger.exception.await_count == 0


@pytest.mark.asyncio
async def test_unit_of_work_exit_without_exception():
    """Test the __aexit__ method without an exception."""
    mock_session = AsyncMock()
    mock_session_factory = MagicMock(return_value=mock_session)

    async with UnitOfWork(session_factory=mock_session_factory):
        pass  # No exception raised

    # Ensure commit is called
    mock_session.commit.assert_awaited_once()

    # Ensure session is closed
    mock_session.close.assert_awaited_once()
