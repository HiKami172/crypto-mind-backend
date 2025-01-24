import pytest
from unittest.mock import AsyncMock, ANY
from uuid import uuid4
from app.services.threads import ThreadService
from app.schemas.threads import ThreadCreateRequest, ThreadMessagesByIdResponse

@pytest.mark.asyncio
async def test_create_thread():
    mock_unit_of_work = AsyncMock()
    mock_unit_of_work.add = AsyncMock()
    mock_unit_of_work.commit = AsyncMock()

    data = ThreadCreateRequest(title="Test Thread")
    user_id = 1

    new_thread = await ThreadService.create(mock_unit_of_work, data, user_id)

    assert new_thread is not None
    assert new_thread.title == "Test Thread"
    assert new_thread.user_id == user_id
    mock_unit_of_work.add.assert_called_once()
    mock_unit_of_work.commit.assert_called_once()

@pytest.mark.asyncio
async def test_retrieve_thread():
    mock_unit_of_work = AsyncMock()
    thread_id = uuid4()
    mock_unit_of_work.threads.get_thread_with_messages = AsyncMock(return_value={"id": str(thread_id), "messages": []})

    result = await ThreadService.retrieve(mock_unit_of_work, thread_id)

    assert result is not None
    assert result["id"] == str(thread_id)
    mock_unit_of_work.threads.get_thread_with_messages.assert_called_once_with(pk=thread_id)

@pytest.mark.asyncio
async def test_list_threads():
    mock_unit_of_work = AsyncMock()
    mock_unit_of_work.threads.list = AsyncMock(return_value={"items": [], "total": 0})

    page = 1
    per_page = 10

    result = await ThreadService.list(mock_unit_of_work, page, per_page)

    assert result["items"] == []
    assert result["total"] == 0
    mock_unit_of_work.threads.list.assert_called_once_with(page=page, per_page=per_page)

@pytest.mark.asyncio
async def test_list_messages():
    mock_unit_of_work = AsyncMock()
    mock_unit_of_work.messages.list = AsyncMock(return_value={"items": [], "total": 0})

    page = 1
    per_page = 10

    result = await ThreadService.list_messages(mock_unit_of_work, page, per_page)

    assert result["items"] == []
    assert result["total"] == 0
    mock_unit_of_work.messages.list.assert_called_once_with(page=page, per_page=per_page)

@pytest.mark.asyncio
async def test_add_message():
    mock_unit_of_work = AsyncMock()
    mock_unit_of_work.messages.create = AsyncMock()

    thread_id = uuid4()
    message = {"content": "Test message", "role": "user"}

    await ThreadService.add_message(mock_unit_of_work, thread_id, message)

    mock_unit_of_work.messages.create.assert_called_once_with(
        id=ANY, thread_id=thread_id, content=message["content"], role=message["role"]
    )

@pytest.mark.asyncio
async def test_get_messages():
    mock_unit_of_work = AsyncMock()
    thread_id = str(uuid4())
    user_id = 1

    # Add the required fields to the mock thread data
    mock_thread = {
        "id": thread_id,
        "title": "Test Thread",
        "created_at": "2025-01-01T00:00:00",
        "updated_at": "2025-01-01T00:00:00",
        "messages": [],
    }
    mock_unit_of_work.threads.get_thread_with_messages = AsyncMock(return_value=mock_thread)

    result = await ThreadService.get_messages(mock_unit_of_work, user_id, thread_id)

    assert result == ThreadMessagesByIdResponse.model_validate(mock_thread)
