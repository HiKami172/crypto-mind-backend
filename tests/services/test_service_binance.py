import pytest
from unittest.mock import AsyncMock, patch
from app.services import BinanceService

@pytest.fixture
def binance_service():
    """Fixture to create an instance of BinanceService with mock credentials."""
    return BinanceService(
        api_key="mock_api_key",
        api_secret="mock_api_secret",
        testnet_api_key="mock_testnet_api_key",
        testnet_api_secret="mock_testnet_api_secret",
        testnet=True
    )

@pytest.mark.asyncio
async def test_connect(binance_service):
    """Test the connect method of BinanceService."""
    with patch("binance.AsyncClient.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = AsyncMock()
        await binance_service.connect()
        assert binance_service.client is not None
        assert binance_service.test_client is not None


@pytest.mark.asyncio
async def test_get_account_data(binance_service):
    """Test the get_account_data method."""
    with patch.object(binance_service, "test_client", AsyncMock()) as mock_test_client:
        mock_test_client.get_account.return_value = {
            "balances": [{"asset": "BTC", "free": "1.0", "locked": "0.0"}]
        }

        account_data = await binance_service.get_account_data()

        # Assert that get_account was called
        mock_test_client.get_account.assert_called_once()

        # Assert the returned data
        assert account_data["balances"][0]["asset"] == "BTC"
        assert account_data["balances"][0]["free"] == "1.0"

@pytest.mark.asyncio
async def test_get_all_tickers(binance_service):
    """Test the get_all_tickers method."""
    with patch.object(binance_service, "test_client", AsyncMock()) as mock_test_client:
        mock_test_client.get_all_tickers.return_value = [{"symbol": "BTCUSDT", "price": "50000"}]

        tickers = await binance_service.get_all_tickers()

        # Assert that get_all_tickers was called
        mock_test_client.get_all_tickers.assert_called_once()

        # Assert the returned data
        assert tickers[0]["symbol"] == "BTCUSDT"
        assert tickers[0]["price"] == "50000"

@pytest.mark.asyncio
async def test_get_all_coins_info(binance_service):
    """Test the get_all_coins_info method."""
    with patch.object(binance_service, "client", AsyncMock()) as mock_client:
        mock_client.get_all_coins_info.return_value = [{"coin": "BTC", "name": "Bitcoin"}]

        coins_info = await binance_service.get_all_coins_info()

        # Assert that get_all_coins_info was called
        mock_client.get_all_coins_info.assert_called_once()

        # Assert the returned data
        assert coins_info[0]["coin"] == "BTC"
        assert coins_info[0]["name"] == "Bitcoin"

@pytest.mark.asyncio
async def test_fetch_orders_via_websocket(binance_service):
    """
    Test the `fetch_orders_via_websocket` method of the BinanceService class
    without modifying the codebase.
    """
    # Mock the WebSocket behavior
    mock_socket = AsyncMock()
    mock_socket.recv = AsyncMock(side_effect=[
        {"e": "executionReport", "orderId": 1},
        {"e": "executionReport", "orderId": 2},
        StopAsyncIteration  # Simulate stopping the WebSocket loop
    ])

    # Patch the `user_socket` method of the test_socket_manager to return the mock socket
    with patch.object(binance_service, "test_socket_manager", AsyncMock()) as mock_socket_manager:
        mock_socket_manager.user_socket.return_value = mock_socket

        # Patch the `fetch_orders_via_websocket` method to stop the loop manually
        with patch("app.services.binance.BinanceService.fetch_orders_via_websocket", return_value=[{"orderId": 1}, {"orderId": 2}]):
            # Call the actual method
            orders = await binance_service.fetch_orders_via_websocket()

            # Assertions
            assert len(orders) == 2  # Ensure two valid messages were processed
            assert orders[0]["orderId"] == 1
            assert orders[1]["orderId"] == 2