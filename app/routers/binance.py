import asyncio
import json
import random
from datetime import datetime, timedelta
from loguru import logger

from fastapi import APIRouter, HTTPException, status
from fastapi import APIRouter, Depends

from app.services import BinanceService
from app.routers.dependencies import get_binance_service

router = APIRouter(tags=["Binance"], prefix="/binance")


@router.get("/account")
async def get_account(service: BinanceService = Depends(get_binance_service)):
    account_data = await service.get_account_data()
    balances = {asset["asset"]: asset for asset in account_data["balances"]}

    tickers = await service.get_all_tickers()
    prices = {ticker["symbol"]: ticker["price"] for ticker in tickers}

    coins_info = await service.get_all_coins_info()
    coins = {coin["coin"]: coin for coin in coins_info}

    def create_url(coin_data) -> str:
        coin_name = coin_data["name"].lower().replace(" ", "-")
        coin_symbol = coin_data["coin"].lower()
        return f"https://cryptologos.cc/logos/{coin_name}-{coin_symbol}-logo.svg"

    balances["USDT"]["price"] = 1
    balances["USDT"]["logo_url"] = "https://cryptologos.cc/logos/tether-usdt-logo.svg"
    for symbol in balances:
        balances[symbol]["price"] = prices.get(f"{symbol}USDT")
        free = balances[symbol].get("free")
        locked = balances[symbol].get("locked")
        if symbol in coins:
            balances[symbol].update(coins[symbol])
            balances[symbol]["logo_url"] = create_url(coins[symbol])
            balances[symbol]["free"] = free
            balances[symbol]["locked"] = locked

    account_data["balances"] = balances
    return account_data


@router.get("/orders", name="Get Orders via WebSocket")
async def get_orders(service: BinanceService = Depends(get_binance_service)):
    """Fetch orders dynamically using WebSocket."""
    try:
        orders = await service.fetch_orders_via_websocket()
        return {"orders": orders}
    except Exception as e:
        return {"error": str(e)}


async def get_portfolio_value(client):
    """Fetch the total portfolio value."""

    async def get_asset_prices():
        """Fetch current prices for all assets."""
        prices = await client.get_all_tickers()
        return {item['symbol']: float(item['price']) for item in prices}

    try:
        account_info = await client.get_account()
        balances = account_info['balances']

        # Get current asset prices
        prices = await get_asset_prices()

        portfolio_value = 0
        historical_data = []

        # Aggregate total value and simulate historical data
        for asset in balances:
            asset_name = asset['asset']
            free_balance = float(asset['free'])
            locked_balance = float(asset['locked'])
            total_balance = free_balance + locked_balance

            if total_balance > 0:
                # Binance's ticker uses `ASSETUSDT` or `ASSETBTC`
                price_symbol = f"{asset_name}USDT"
                asset_price = prices.get(price_symbol, None)

                if asset_price:
                    asset_value = total_balance * asset_price
                    portfolio_value += asset_value

                    # Simulate daily historical values (replace this with actual historical data API if available)
                    start_date = datetime.now() - timedelta(days=30)
                    historical_data.append({
                        "asset": asset_name,
                        "values": [
                            {
                                "date": (start_date + timedelta(days=i)).strftime('%Y-%m-%d'),
                                "value": round(asset_value * (1 + random.uniform(-0.05, 0.05)), 2)
                            }
                            for i in range(30)
                        ]
                    })

        return {"total_value": portfolio_value, "history": historical_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching portfolio data: {str(e)}")


@router.get("/portfolio/card-data")
async def get_card_data(service: BinanceService = Depends(get_binance_service)):
    """
    Endpoint to fetch portfolio data formatted for StatCard.
    """
    try:
        client = service.test_client
        # Fetch portfolio value and simulate data
        portfolio_data = await get_portfolio_value(client)

        # Total portfolio value
        total_value = portfolio_data["total_value"]

        # Get the daily values for all assets in the portfolio
        daily_values = [0] * 30  # Assuming 30 days of data
        for asset in portfolio_data["history"]:
            for i, day in enumerate(asset["values"]):
                daily_values[i] += day["value"]

        change = (daily_values[-1] - daily_values[0]) / daily_values[0] * 100
        trend = "up" if daily_values[-1] > daily_values[0] else "down" if daily_values[-1] < daily_values[
            0] else "neutral"

        card_data = {
            "value": f"${total_value:,.0f}",
            "interval": "Last 30 days",
            "trend": trend,
            "change": change,
            "data": [round(value, 2) for value in daily_values],
        }

        return card_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating card data: {str(e)}")
