from langchain_core.tools import tool


@tool
def place_order(symbol: str, side: str, order_type: str, quantity: float, price: float = None, stop_price: float = None, time_in_force: str = 'GTC'):
    """
    Places an order on Binance based on the provided parameters.

    Args:
        symbol (str): The trading pair symbol (e.g., 'BTCUSDT').
        side (str): The order side, either 'BUY' or 'SELL'.
        order_type (str): The type of order (e.g., 'LIMIT', 'MARKET', 'STOP_LOSS', 'TAKE_PROFIT').
        quantity (float): The quantity of the asset to trade.
        price (float, optional): The price for limit and stop-limit orders. Not required for market orders.
        stop_price (float, optional): The stop price for stop-loss or take-profit orders. Defaults to None.
        time_in_force (str, optional): Order time policy (e.g., 'GTC' for Good Till Cancelled, 'IOC' for Immediate or Cancel). Defaults to 'GTC'.

    Returns:
        dict: The response from the Binance API containing order details, or an error message if the order failed.

    Example:
        place_order('BTCUSDT', 'BUY', 'LIMIT', 0.001, price=30000, time_in_force='GTC')
        place_order('ETHUSDT', 'SELL', 'MARKET', 0.5)
    """
    order_params = {
        'symbol': symbol,
        'side': side,
        'type': order_type,
        'quantity': quantity,
        'timeInForce': time_in_force
    }

    if price is not None:
        order_params['price'] = price

    if stop_price is not None:
        order_params['stopPrice'] = stop_price

    # Example API call (You need to replace with actual Binance API request)
    # response = client.new_order(**order_params)
    response = {"status": "order placed"}  # Placeholder for actual API call

    return response

@tool
def check_balance(asset: str):
    """
    Retrieves the account balance for a specific asset.

    Args:
        asset (str): The asset symbol (e.g., 'BTC', 'ETH') for which the balance is requested.

    Returns:
        dict: The balance details from Binance for the specified asset, including free and locked amounts.

    Example:
        check_balance('BTC')
    """
    # Example API call to get account balances (Replace with actual Binance API call)
    # response = client.get_account()
    response = {"asset": asset, "free": 0.5, "locked": 0.0}  # Placeholder

    return response

@tool
def get_latest_price(symbol: str):
    """
    Retrieves the latest market price for a specified trading pair.

    Args:
        symbol (str): The trading pair symbol (e.g., 'BTCUSDT').

    Returns:
        dict: A dictionary containing the current market price for the trading pair.

    Example:
        get_latest_price('BTCUSDT')
    """
    # Example API call (Replace with actual Binance API call)
    # response = client.get_symbol_ticker(symbol=symbol)
    response = {"symbol": symbol, "price": 29500.00}  # Placeholder for actual API response

    return response

@tool
def get_open_orders(symbol: str = None):
    """
    Retrieves open orders for a specific symbol or all open orders if no symbol is provided.

    Args:
        symbol (str, optional): The trading pair symbol (e.g., 'BTCUSDT'). Defaults to None, which retrieves all open orders.

    Returns:
        list: A list of dictionaries containing open order details.

    Example:
        get_open_orders('BTCUSDT')
        get_open_orders()
    """
    # Example API call (Replace with actual Binance API call)
    # response = client.get_open_orders(symbol=symbol)
    response = [
        {"symbol": "BTCUSDT", "orderId": 12345, "price": 30000, "quantity": 0.001},
        {"symbol": "ETHUSDT", "orderId": 12346, "price": 2000, "quantity": 0.5}
    ]  # Placeholder for actual API response

    return response

@tool
def cancel_order(symbol: str, order_id: int):
    """
    Cancels an open order by order ID for a specified trading pair.

    Args:
        symbol (str): The trading pair symbol (e.g., 'BTCUSDT').
        order_id (int): The ID of the order to cancel.

    Returns:
        dict: The response from the Binance API containing details about the canceled order, or an error message if it failed.

    Example:
        cancel_order('BTCUSDT', 12345)
    """
    # Example API call (Replace with actual Binance API call)
    # response = client.cancel_order(symbol=symbol, orderId=order_id)
    response = {"status": "order canceled", "orderId": order_id}  # Placeholder for actual API response

    return response

@tool
def check_order_status(symbol: str, order_id: int):
    """
    Retrieves the status of a specific order by order ID for a given trading pair.

    Args:
        symbol (str): The trading pair symbol (e.g., 'BTCUSDT').
        order_id (int): The ID of the order whose status is requested.

    Returns:
        dict: The response from the Binance API containing the order status and other details.

    Example:
        check_order_status('BTCUSDT', 12345)
    """
    # Example API call (Replace with actual Binance API call)
    # response = client.get_order(symbol=symbol, orderId=order_id)
    response = {"symbol": symbol, "orderId": order_id, "status": "FILLED"}  # Placeholder for actual API response

    return response

@tool
def get_recent_trades(symbol: str, limit: int = 10):
    """
    Retrieves the most recent trades for a specific trading pair.

    Args:
        symbol (str): The trading pair symbol (e.g., 'BTCUSDT').
        limit (int, optional): The number of recent trades to retrieve. Defaults to 10.

    Returns:
        list: A list of recent trades, including price, quantity, and trade time.

    Example:
        get_recent_trades('BTCUSDT', limit=5)
    """
    # Example API call (Replace with actual Binance API call)
    # response = client.get_recent_trades(symbol=symbol, limit=limit)
    response = [
        {"price": 29400.00, "quantity": 0.002, "time": "2024-10-22T10:00:00Z"},
        {"price": 29500.00, "quantity": 0.001, "time": "2024-10-22T10:01:00Z"}
    ]  # Placeholder for actual API response

    return response


toolkit = [
    place_order,
    check_balance,
    get_open_orders,
    get_latest_price,
    cancel_order,
    check_order_status,
    get_recent_trades
]