import pytest
from unittest.mock import MagicMock, patch
from app.inference.chat.model import ChatModel

@pytest.fixture
def mock_agent_executor():
    """Fixture to mock the agent executor."""
    mock_executor = MagicMock()
    mock_executor.invoke.return_value = {
        'messages': [{'content': 'Test response'}]
    }
    return mock_executor

@pytest.fixture
def mock_create_react_agent(mock_agent_executor):
    """Fixture to mock create_react_agent."""
    with patch("app.inference.chat.model.create_react_agent", return_value=mock_agent_executor):
        yield mock_agent_executor

@pytest.fixture
def mock_chat_openai():
    """Fixture to mock ChatOpenAI."""
    with patch("app.inference.chat.model.ChatOpenAI") as mock_model:
        mock_instance = MagicMock()
        mock_model.return_value = mock_instance
        yield mock_instance

def test_chat_model_initialization(mock_create_react_agent, mock_chat_openai):
    """Test that ChatModel initializes properly."""
    model = ChatModel()
    assert model.model == mock_chat_openai
    assert model.agent_executor == mock_create_react_agent

def test_chat_model_run(mock_create_react_agent, mock_chat_openai):
    """Test the run method of ChatModel."""
    # Create a sample input message
    input_messages = [{"role": "user", "content": "Hello, how are you?"}]

    # Mock the response to match the expected structure
    mock_response_message = MagicMock()
    mock_response_message.content = "Mock response content"

    # Mock the `invoke` return value
    mock_create_react_agent.invoke.return_value = {
        'messages': [mock_response_message]
    }

    # Initialize the model
    model = ChatModel()

    # Call the `run` method
    response = model.run(input_messages)

    # Assertions
    mock_create_react_agent.invoke.assert_called_once_with({'messages': input_messages})
    assert response == "Mock response content"



