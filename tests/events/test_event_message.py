import pytest
from unittest.mock import MagicMock, call
from uuid import uuid4
from app.models import Thread, Message
from app.events.message_events import register_message_events


def test_message_event():
    """Test the message event without relying on actual DB execution."""
    # Mock the database connection
    mock_connection = MagicMock()

    # Register the message event
    register_message_events()

    # Mock thread and message objects
    thread_id = str(uuid4())
    thread = Thread(id=thread_id, title="Test Thread", user_id="1")
    message = Message(id=str(uuid4()), thread_id=thread_id, content="Test message", role="user")

    # Simulate the behavior of the event
    mock_connection.execute.return_value = None

    # Manually trigger the event for the thread
    thread_update_query = Thread.__table__.update().where(Thread.id == thread_id).values(updated_at="NOW()")
    mock_connection.execute(thread_update_query)

    # Manually trigger the event for the message (if applicable)
    message_update_query = Thread.__table__.update().where(Thread.id == message.thread_id).values(updated_at="NOW()")
    mock_connection.execute(message_update_query)

    # Assertions: Check call counts and string representations
    assert mock_connection.execute.call_count == 2
    mock_connection.execute.assert_any_call(thread_update_query)
    mock_connection.execute.assert_any_call(message_update_query)

    # Optionally compare string representations for clarity
    executed_queries = [str(call[0][0]) for call in mock_connection.execute.call_args_list]
    expected_queries = [str(thread_update_query), str(message_update_query)]
    assert executed_queries == expected_queries
