from app.models.threads import Thread, Message
from uuid import uuid4


def test_thread_model():
    thread = Thread(
        id=uuid4(),
        title="Test Thread",
        user_id=1
    )
    assert thread.title == "Test Thread"
    assert thread.user_id == 1


def test_message_model():
    message = Message(
        id=uuid4(),
        role="user",
        content="Hello, this is a test message",
        thread_id=uuid4()
    )
    assert message.role == "user"
    assert message.content == "Hello, this is a test message"
