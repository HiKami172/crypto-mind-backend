from binance import AsyncClient, BinanceSocketManager


class BinanceService:
    def __init__(self,
                 api_key: str,
                 api_secret: str,
                 testnet_api_key: str,
                 testnet_api_secret: str,
                 testnet: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet_api_key = testnet_api_key
        self.testnet_api_secret = testnet_api_secret
        self.testnet = testnet

        self.client = None
        self.test_client = None
        self.socket_manager = None
        self.test_socket_manager = None

    async def connect(self):
        """Initialize the AsyncClient and SocketManager."""
        self.client = await AsyncClient.create(
            api_key=self.api_key,
            api_secret=self.api_secret,
        )
        self.test_client = await AsyncClient.create(
            api_key=self.testnet_api_key,
            api_secret=self.testnet_api_secret,
            testnet=self.testnet,
        )
        self.socket_manager = BinanceSocketManager(self.client)
        self.test_socket_manager = BinanceSocketManager(self.test_client)

    async def close(self):
        """Properly close clients."""
        if self.client:
            await self.client.close_connection()
        if self.test_client:
            await self.test_client.close_connection()

    async def get_account_data(self):
        """Fetch account data including balances."""
        return await self.test_client.get_account()

    async def get_all_tickers(self):
        """Fetch all ticker prices."""
        return await self.test_client.get_all_tickers()

    async def get_all_orders(self, symbol: str):
        """Fetch all orders for a specific symbol."""
        return await self.test_client.get_all_orders(symbol=symbol)

    async def get_all_coins_info(self):
        """Fetch all coin information."""
        return await self.client.get_all_coins_info()

