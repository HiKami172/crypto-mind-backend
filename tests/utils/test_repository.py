import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

from app.utils.repository import SQLAlchemyRepository
from app.exceptions.request_exceptions import NotFoundException

Base = declarative_base()


class MockModel(Base):
    __tablename__ = "mock_table"
    id = Column(Integer, primary_key=True)
    name = Column(String)


@pytest.fixture
def mock_session():
    """Fixture to create a mocked AsyncSession."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def repository(mock_session):
    """Fixture to create a repository instance with a mocked session."""
    class MockRepository(SQLAlchemyRepository):
        model = MockModel

    return MockRepository(session=mock_session)


@pytest.mark.asyncio
async def test_create(repository, mock_session):
    """Test the create method."""
    mock_instance = MockModel(id=1, name="Test")
    repository.model = MagicMock(return_value=mock_instance)

    result = await repository.create(id=1, name="Test")

    assert result == mock_instance
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_list(repository, mock_session):
    """Test the list method."""
    mock_result = AsyncMock()
    mock_result.scalars.return_value = [MockModel(id=i, name=f"Name {i}") for i in range(3)]
    mock_session.execute.return_value = mock_result

    repository.fetch_data = AsyncMock(return_value=[MockModel(id=i) for i in range(3)])
    result = await repository.list(limit=3)

    assert len(result) == 3
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_retrieve(repository, mock_session):
    """Test the retrieve method."""
    mock_result = AsyncMock()
    mock_result.scalar_one.return_value = MockModel(id=1, name="Test")
    mock_session.execute.return_value = mock_result

    repository.fetch_data = AsyncMock(return_value=MockModel(id=1))
    result = await repository.retrieve(id=1)

    assert result.id == 1


@pytest.mark.asyncio
async def test_update(repository, mock_session):
    """Test the update method."""
    mock_result = AsyncMock()
    mock_result.scalar_one.return_value = MockModel(id=1, name="Updated")
    mock_session.execute.return_value = mock_result

    repository.fetch_data = AsyncMock(return_value=MockModel(id=1, name="Updated"))
    result = await repository.update(data={"name": "Updated"}, id=1)

    assert result.name == "Updated"
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_or_create(repository, mock_session):
    """Test the get_or_create method."""
    # Mock retrieve to simulate a successful retrieval
    repository.retrieve = AsyncMock(return_value=MockModel(id=1, name="Test"))
    repository.create = AsyncMock()  # Create should not be called in this scenario

    # Act
    result = await repository.get_or_create(id=1, name="Test")

    # Assert
    repository.retrieve.assert_awaited_once_with(return_result=False, id=1, name="Test")
    repository.create.assert_not_called()
    assert result.id == 1
    assert result.name == "Test"








