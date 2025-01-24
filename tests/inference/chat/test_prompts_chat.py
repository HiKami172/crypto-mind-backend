import pytest
from app.inference.chat.prompts import prompt

def test_prompt_content():
    # Assert the prompt is a string
    assert isinstance(prompt, str)

    # Assert the prompt contains the expected content
    assert "chat assistant" in prompt
    assert "crypto trading application" in prompt
    assert "Objective" in prompt

