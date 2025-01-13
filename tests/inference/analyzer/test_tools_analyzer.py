import pytest
from unittest.mock import MagicMock, patch
from app.inference.analyzer.tools import (
    place_order,
    check_balance,
    get_open_orders,
    get_latest_price,
    cancel_order,
    check_order_status,
    get_recent_trades
)


def test_place_order():
    # Arrange
    tool_input = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "order_type": "LIMIT",
        "quantity": 0.01,
        "price": 30000,
        "time_in_force": "GTC"
    }

    # Act
    response = place_order.run(tool_input)

    # Assert
    assert response == {"status": "order placed"}


def test_check_balance():
    # Arrange
    tool_input = "BTC"

    # Act
    response = check_balance.run(tool_input)

    # Assert
    assert response == {"asset": "BTC", "free": 0.5, "locked": 0.0}


def test_get_open_orders():
    # Arrange
    tool_input = {"symbol": ""}  # Provide a valid string (empty or placeholder)

    # Act
    response = get_open_orders.run(tool_input)

    # Assert
    assert isinstance(response, list)
    assert len(response) > 0
    assert "symbol" in response[0]
    assert "orderId" in response[0]



def test_get_latest_price():
    # Arrange
    tool_input = "BTCUSDT"

    # Act
    response = get_latest_price.run(tool_input)

    # Assert
    assert response == {"symbol": "BTCUSDT", "price": 29500.00}


def test_cancel_order():
    # Arrange
    tool_input = {"symbol": "BTCUSDT", "order_id": 12345}

    # Act
    response = cancel_order.run(tool_input)

    # Assert
    assert response == {"status": "order canceled", "orderId": 12345}


def test_check_order_status():
    # Arrange
    tool_input = {"symbol": "BTCUSDT", "order_id": 12345}

    # Act
    response = check_order_status.run(tool_input)

    # Assert
    assert response == {"symbol": "BTCUSDT", "orderId": 12345, "status": "FILLED"}


def test_get_recent_trades():
    # Arrange
    tool_input = {"symbol": "BTCUSDT", "limit": 2}

    # Act
    response = get_recent_trades.run(tool_input)

    # Assert
    assert isinstance(response, list)
    assert len(response) == 2
    assert response[0] == {"price": 29400.00, "quantity": 0.002, "time": "2024-10-22T10:00:00Z"}
    assert response[1] == {"price": 29500.00, "quantity": 0.001, "time": "2024-10-22T10:01:00Z"}
