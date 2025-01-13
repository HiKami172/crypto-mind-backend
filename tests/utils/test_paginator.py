import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.utils.paginator import Paginator, paginate


@pytest.mark.asyncio
@patch("app.utils.paginator.request_object")
async def test_paginator_normal_pagination(mock_request_object):
    """Dummy test for normal pagination."""
    # Mock request_object.get to avoid LookupError
    mock_request_object.get.return_value = None

    # Arrange
    mock_session = AsyncMock()
    mock_query = MagicMock()

    paginator = Paginator(
        session=mock_session,
        query=mock_query,
        page=1,
        per_page=5,
        fetch_method="scalars",
    )

    paginator._get_total_count = AsyncMock(return_value=20)
    paginator._get_items = AsyncMock(return_value=[1, 2, 3, 4, 5])
    paginator._get_next_page = MagicMock(return_value=2)  # Mock next page
    paginator._get_previous_page = MagicMock(return_value=None)  # Mock previous page

    # Act
    response = await paginator.get_response()

    # Assert
    assert response["offset"] == 0
    assert response["count"] == 20
    assert response["next_page"] == 2
    assert response["previous_page"] is None
    assert response["items"] == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
@patch("app.utils.paginator.request_object")
async def test_paginator_reversed_pagination(mock_request_object):
    """Dummy test for reversed pagination."""
    # Mock request_object.get to avoid LookupError
    mock_request_object.get.return_value = None

    # Arrange
    mock_session = AsyncMock()
    mock_query = MagicMock()

    paginator = Paginator(
        session=mock_session,
        query=mock_query,
        page=2,
        per_page=5,
        fetch_method="scalars",
        is_reversed=True,
    )

    paginator._get_total_count = AsyncMock(return_value=20)
    paginator._get_items = AsyncMock(return_value=[15, 16, 17, 18, 19])
    paginator._get_next_page = MagicMock(return_value=3)  # Mock next page
    paginator._get_previous_page = MagicMock(return_value=1)  # Mock previous page

    # Act
    response = await paginator.get_response()

    # Assert
    assert response["offset"] == 10
    assert response["count"] == 20
    assert response["next_page"] == 3
    assert response["previous_page"] == 1
    assert response["items"] == [15, 16, 17, 18, 19]


@pytest.mark.asyncio
@patch("app.utils.paginator.request_object")
async def test_paginate_function(mock_request_object):
    """Dummy test for the paginate function."""
    # Mock request_object.get to avoid LookupError
    mock_request_object.get.return_value = None

    # Arrange
    mock_session = AsyncMock()
    mock_query = MagicMock()

    # Mock Paginator methods
    with patch("app.utils.paginator.Paginator._get_total_count", new=AsyncMock(return_value=20)):
        with patch("app.utils.paginator.Paginator._get_items", new=AsyncMock(return_value=[1, 2, 3, 4, 5])):
            with patch("app.utils.paginator.Paginator._get_next_page", new=MagicMock(return_value=2)):
                with patch("app.utils.paginator.Paginator._get_previous_page", new=MagicMock(return_value=None)):
                    # Act
                    response = await paginate(
                        session=mock_session,
                        query=mock_query,
                        page=1,
                        per_page=5,
                        fetch_method="scalars",
                    )

    # Assert
    assert response["offset"] == 0
    assert response["count"] == 20
    assert response["next_page"] == 2
    assert response["previous_page"] is None
    assert response["items"] == [1, 2, 3, 4, 5]


@pytest.mark.asyncio
@patch("app.utils.paginator.request_object")
async def test_paginator_extra_page(mock_request_object):
    """Dummy test for pagination with an extra page."""
    # Mock request_object.get to avoid LookupError
    mock_request_object.get.return_value = None

    # Arrange
    mock_session = AsyncMock()
    mock_query = MagicMock()

    paginator = Paginator(
        session=mock_session,
        query=mock_query,
        page=5,
        per_page=5,
        fetch_method="scalars",
        add_extra_page=True,
    )

    paginator._get_total_count = AsyncMock(return_value=20)
    paginator._get_items = AsyncMock(return_value=[16, 17, 18, 19, 20])
    paginator._get_next_page = MagicMock(return_value=None)  # Mock next page
    paginator._get_previous_page = MagicMock(return_value=4)  # Mock previous page

    # Act
    response = await paginator.get_response()

    # Assert
    assert response["offset"] == 20
    assert response["count"] == 20
    assert response["next_page"] is None
    assert response["previous_page"] == 4
    assert response["items"] == [16, 17, 18, 19, 20]
