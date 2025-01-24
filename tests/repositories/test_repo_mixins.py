from unittest.mock import AsyncMock, MagicMock, patch
from app.repositories.mixins import PaginateListMixins
from sqlalchemy.sql import Select
import pytest


class MockModel:
    pass


class TestPaginateListMixins:
    @pytest.mark.asyncio
    async def test_list(self):
        # Mock the session and paginate function
        mock_session = MagicMock()
        mock_paginate = AsyncMock(return_value={"items": [], "total": 0, "page": 1, "per_page": 10})

        # Mock the Select object and simulate its behavior
        mock_select = MagicMock(spec=Select)
        mock_select.filter_by.return_value = "dummy_filtered_select"

        # Patch the `paginate` function and `select`
        with patch("app.repositories.mixins.paginate", mock_paginate), \
             patch("app.repositories.mixins.select", return_value=mock_select):

            # Create an instance of the mixin
            mixin = PaginateListMixins()
            mixin.session = mock_session
            mixin.model = MockModel

            # Call the `list` method
            result = await mixin.list(page=1, per_page=10, is_reversed=False, filter_key="value")

            # Assertions
            mock_select.filter_by.assert_called_once_with(filter_key="value")
            mock_paginate.assert_called_once_with(
                mock_session,
                "dummy_filtered_select",
                page=1,
                per_page=10,
                is_reversed=False
            )

            # Verify the result
            assert result == {"items": [], "total": 0, "page": 1, "per_page": 10}
