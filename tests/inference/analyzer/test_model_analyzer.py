import pytest
from unittest.mock import MagicMock, patch
from app.inference.analyzer.model import AnalyzerModel
from langchain_core.messages import BaseMessage


@pytest.fixture
def mock_agent_executor():
    """Fixture to mock the agent executor."""
    mock_executor = MagicMock()
    mock_executor.invoke.return_value = MagicMock(content="Test response")
    return mock_executor


@pytest.fixture
def mock_create_react_agent(mock_agent_executor):
    """Fixture to mock create_react_agent."""
    with patch("app.inference.analyzer.model.create_react_agent", return_value=mock_agent_executor):
        yield mock_agent_executor


@pytest.fixture
def mock_chat_openai():
    """Fixture to mock ChatOpenAI."""
    with patch("app.inference.analyzer.model.ChatOpenAI") as mock_model:
        mock_instance = MagicMock()
        mock_model.return_value = mock_instance
        yield mock_instance


def test_analyzer_model_initialization(mock_create_react_agent, mock_chat_openai):
    """Test that AnalyzerModel initializes properly."""
    model = AnalyzerModel()
    assert model.model == mock_chat_openai
    assert model.agent_executor == mock_create_react_agent


def test_analyzer_model_run(mock_create_react_agent, mock_chat_openai):
    """Test the run method of AnalyzerModel."""
    # Create a sample message
    sample_message = MagicMock(spec=BaseMessage)
    messages = [sample_message]

    # Initialize the model
    model = AnalyzerModel()

    # Call the run method
    response = model.run(messages)

    # Assertions
    mock_create_react_agent.invoke.assert_called_once_with({'messages': messages})
    assert response == "Test response"
