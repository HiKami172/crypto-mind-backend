import pytest
from starlette.requests import Request
from starlette.responses import Response
from unittest.mock import AsyncMock, MagicMock
from app.middlewares.context import RequestMiddleware, request_object


@pytest.mark.asyncio
async def test_request_middleware():
    # Create a mock app
    mock_app = MagicMock()

    # Create a mock request
    mock_request = MagicMock(spec=Request)

    # Create a mock response
    mock_response = MagicMock(spec=Response)

    # Mock the next handler (call_next)
    async def mock_call_next(request: Request):
        return mock_response

    # Create an instance of the middleware with the mock app
    middleware = RequestMiddleware(app=mock_app)

    # Dispatch the middleware
    response = await middleware.dispatch(mock_request, mock_call_next)

    # Assertions
    assert response == mock_response  # Ensure the response is correctly returned
    assert request_object.get() == mock_request  # Check that the context variable is set
