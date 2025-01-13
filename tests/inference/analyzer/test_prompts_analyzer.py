from app.inference.analyzer.prompts import prompt


def test_prompt_content():

    # Assert the prompt is a string
    assert isinstance(prompt, str)

    # Assert the prompt contains the expected content
    assert "AI analyzer" in prompt
    assert "trade crypto assets" in prompt
    assert "Objective" in prompt
