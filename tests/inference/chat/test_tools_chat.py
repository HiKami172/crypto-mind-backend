import pytest
from unittest.mock import MagicMock, patch
from app.inference.chat.tools import (
    place_order,
    check_balance,
    get_latest_price,
    get_open_orders,
    cancel_order,
    check_order_status,
    get_recent_trades,
)


@pytest.fixture
def mock_binance_client():
    """Fixture to mock the Binance client."""
    with patch("app.inference.chat.tools.test_client") as mock_client:
        yield mock_client


def test_place_order(mock_binance_client):
    """Test the place_order tool."""
    # Arrange
    mock_binance_client.create_order.return_value = {"status": "SUCCESS"}
    tool_input = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "order_type": "LIMIT",
        "quantity": 0.01,
        "price": 30000,
        "time_in_force": "GTC",
    }

    # Act
    response = place_order.run(tool_input)

    # Assert
    mock_binance_client.create_order.assert_called_once_with(
        symbol="BTCUSDT",
        side="BUY",
        type="LIMIT",
        quantity=0.01,
        timeInForce="GTC",
        price=30000,
    )
    assert response == {"status": "SUCCESS"}


def test_check_balance(mock_binance_client):
    """Test the check_balance tool."""
    # Arrange
    mock_binance_client.get_account.return_value = {
        "balances": [{"asset": "BTC", "free": 0.5, "locked": 0.1}]
    }
    tool_input = {"asset": "BTC"}

    # Act
    response = check_balance.run(tool_input)

    # Assert
    mock_binance_client.get_account.assert_called_once()
    assert response == {"asset": "BTC", "free": 0.5, "locked": 0.1}


def test_get_latest_price(mock_binance_client):
    """Test the get_latest_price tool."""
    # Arrange
    mock_binance_client.get_symbol_ticker.return_value = {"symbol": "BTCUSDT", "price": 29500.0}
    tool_input = {"symbol": "BTCUSDT"}

    # Act
    response = get_latest_price.run(tool_input)

    # Assert
    mock_binance_client.get_symbol_ticker.assert_called_once_with(symbol="BTCUSDT")
    assert response == {"symbol": "BTCUSDT", "price": 29500.0}


def test_get_open_orders(mock_binance_client):
    """Test the get_open_orders tool."""
    # Arrange
    mock_binance_client.get_open_orders.return_value = [
        {"symbol": "BTCUSDT", "orderId": 12345, "price": 30000, "quantity": 0.001}
    ]
    tool_input = {"symbol": ""}  # Use an empty string to signify 'all symbols'

    # Act
    response = get_open_orders.run(tool_input)

    # Assert
    mock_binance_client.get_open_orders.assert_called_once_with(symbol="")
    assert isinstance(response, list)
    assert len(response) > 0
    assert "symbol" in response[0]
    assert "orderId" in response[0]



def test_cancel_order(mock_binance_client):
    """Test the cancel_order tool."""
    # Arrange
    mock_binance_client.cancel_order.return_value = {"status": "CANCELED", "orderId": 12345}
    tool_input = {"symbol": "BTCUSDT", "order_id": 12345}

    # Act
    response = cancel_order.run(tool_input)

    # Assert
    mock_binance_client.cancel_order.assert_called_once_with(symbol="BTCUSDT", orderId=12345)
    assert response == {"status": "CANCELED", "orderId": 12345}


def test_check_order_status(mock_binance_client):
    """Test the check_order_status tool."""
    # Arrange
    mock_binance_client.get_order.return_value = {"symbol": "BTCUSDT", "orderId": 12345, "status": "FILLED"}
    tool_input = {"symbol": "BTCUSDT", "order_id": 12345}

    # Act
    response = check_order_status.run(tool_input)

    # Assert
    mock_binance_client.get_order.assert_called_once_with(symbol="BTCUSDT", orderId=12345)
    assert response == {"symbol": "BTCUSDT", "orderId": 12345, "status": "FILLED"}


def test_get_recent_trades(mock_binance_client):
    """Test the get_recent_trades tool."""
    # Arrange
    mock_binance_client.get_all_orders.return_value = [
        {"price": 29400.00, "quantity": 0.002, "time": "2024-10-22T10:00:00Z"},
        {"price": 29500.00, "quantity": 0.001, "time": "2024-10-22T10:01:00Z"}
    ]
    tool_input = {"symbol": "BTCUSDT", "limit": 5}

    # Act
    response = get_recent_trades.run(tool_input)

    # Assert
    mock_binance_client.get_all_orders.assert_called_once_with(symbol="BTCUSDT", limit=5)
    assert response == [
        {"price": 29400.00, "quantity": 0.002, "time": "2024-10-22T10:00:00Z"},
        {"price": 29500.00, "quantity": 0.001, "time": "2024-10-22T10:01:00Z"}
    ]
