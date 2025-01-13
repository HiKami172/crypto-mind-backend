from uuid import uuid4, UUID
from datetime import datetime
from app.schemas.threads import (
    ThreadCreateRequest,
    ThreadCreateResponse,
    Thread,
    MessageMain,
    ThreadMessagesByIdResponse,
    ThreadList,
)


def test_thread_create_request_validation():
    data = {"title": "Test Thread"}
    schema = ThreadCreateRequest(**data)
    assert schema.title == "Test Thread"


def test_thread_create_response():
    thread_id = uuid4()  # Generate a UUID4
    schema = ThreadCreateResponse(thread_id=thread_id)

    # Check if the `thread_id` was properly assigned
    assert str(schema.thread_id) == str(thread_id)

    # Ensure `thread_id` in schema is of the correct type
    assert isinstance(schema.thread_id, UUID)  # Use UUID instead of UUID4


def test_thread_serialization():
    thread_id = uuid4()
    now = datetime.now()
    schema = Thread(
        id=thread_id,
        title="Test Thread",
        created_at=now,
        updated_at=now,
    )
    serialized = schema.dict()
    assert serialized["id"] == str(thread_id)
    assert serialized["created_at"] == now.isoformat()
    assert serialized["updated_at"] == now.isoformat()


def test_message_main_serialization():
    message_id = uuid4()
    thread_id = uuid4()
    now = datetime.now()
    schema = MessageMain(
        id=message_id,
        text="Hello, world!",
        type="user",
        created_at=now,
        thread_id=thread_id,
    )
    serialized = schema.dict()
    assert serialized["id"] == str(message_id)
    assert serialized["thread_id"] == str(thread_id)
    assert serialized["created_at"] == now.isoformat()


def test_thread_messages_by_id_response():
    thread_id = uuid4()
    now = datetime.now()
    messages = [
        {
            "id": uuid4(),
            "text": "Message 1",
            "type": "user",
            "created_at": now,
            "thread_id": thread_id,
        },
        {
            "id": uuid4(),
            "text": "Message 2",
            "type": "assistant",
            "created_at": now,
            "thread_id": thread_id,
        },
    ]
    schema = ThreadMessagesByIdResponse(
        id=thread_id,
        title="Test Thread",
        created_at=now,
        updated_at=now,
        messages=[MessageMain(**msg) for msg in messages],
    )
    assert len(schema.messages) == 2
    assert schema.messages[0].type == "user"
    assert schema.messages[1].type == "assistant"


def test_thread_list_serialization():
    thread_id1 = uuid4()
    thread_id2 = uuid4()
    now = datetime.now()
    threads = [
        Thread(
            id=thread_id1,
            title="Thread 1",
            created_at=now,
            updated_at=now,
        ),
        Thread(
            id=thread_id2,
            title="Thread 2",
            created_at=now,
            updated_at=now,
        ),
    ]
    schema = ThreadList(threads=threads)
    serialized = schema.model_dump()
    assert len(serialized) == 2
    assert serialized[0]["id"] == str(thread_id1)
    assert serialized[1]["id"] == str(thread_id2)
