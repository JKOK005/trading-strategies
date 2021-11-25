from kucoin.client import Market as Market_C, Trade as Trade_C, User as User_C
from kucoin_futures.client import Market as Market_F, Trade as Trade_F, User as User_F
from clients.Clients import ExchangeClients

class KucoinApiClient(ExchangeClients):
	spot_client 				= None
	futures_client 				= None
	futures_trade 				= None
	futures_user 				= None
	kucoin_spot_url 			= "https://api.kucoin.com"
	kucoin_spot_sandbox_url 	= "https://openapi-sandbox.kucoin.com"
	kucoin_futures_url 			= "https://api-futures.kucoin.com"
	kucoin_futures_sandbox_url 	= "https://api-sandbox-futures.kucoin.com"

	def __init__(self, 	spot_client_api_key: str, 
						spot_client_api_secret_key: str, 
						spot_client_pass_phrase: str,
						futures_client_api_key: str, 
						futures_client_api_secret_key: str, 
						futures_client_pass_phrase: str,
						sandbox: bool
				):

		super(KucoinApiClient, self).__init__()

		self.spot_client 	= 	Market_C(url = self.kucoin_spot_sandbox_url if sandbox else self.kucoin_spot_url)

		self.spot_trade 	= 	Trade_C(key 		= spot_client_api_key, 
										secret 		= spot_client_api_secret_key, 
										passphrase 	= spot_client_pass_phrase, 
										url 		= self.kucoin_spot_sandbox_url if sandbox else self.kucoin_spot_url
									)

		self.spot_user 		= 	User_C( key 		= spot_client_api_key, 
										secret 		= spot_client_api_secret_key, 
										passphrase 	= spot_client_pass_phrase, 
										url 		= self.kucoin_spot_sandbox_url if sandbox else self.kucoin_spot_url
									)


		self.futures_client = 	Market_F(url = self.kucoin_futures_sandbox_url if sandbox else self.kucoin_futures_url)
		
		self.futures_trade 	= 	Trade_F(key 		= futures_client_api_key, 
										secret 		= futures_client_api_secret_key, 
										passphrase 	= futures_client_pass_phrase, 
										url 		= self.kucoin_futures_sandbox_url if sandbox else self.kucoin_futures_url
									)

		self.futures_user 	= 	User_F( key 		= futures_client_api_key, 
										secret 		= futures_client_api_secret_key, 
										passphrase 	= futures_client_pass_phrase, 
										url 		= self.kucoin_futures_sandbox_url if sandbox else self.kucoin_futures_url
									)

	def get_spot_trading_price(self, symbol: str):
		"""
		Retrieves current spot pricing for trading symbol
		"""
		return float(self.spot_client.get_ticker(symbol)["price"])

	def get_futures_trading_price(self, symbol: str):
		"""
		Retrieves current futures price for trading symbol
		"""
		return float(self.futures_client.get_ticker(symbol)["price"])

	def get_spot_position(self, symbol: str):
		"""
		Gets the amount of assets position by the user
		"""
		pass

	def get_futures_position(self, symbol: str):
		"""
		Gets the amount of futures position by the user
		"""
		pass

	def place_spot_order(self, 	symbol: str, 
								order_type: str, 
								order_side: str, 
								price: int,
								size: int,
								*args, **kwargs):
		"""
		order_type 	- Either limit or market
		order_side 	- Either buy or sell
		size 		- VOLUME of asset to purchase

		Ref: https://docs.kucoin.com/#place-a-new-order
		"""
		return 	self.spot_trade.create_market_order(symbol = symbol,
													type 	= order_type,
													side 	= order_side,
													price 	= price,
													size 	= size
												)

	def place_futures_order(self, 	symbol: str, 
									order_type: str, 
									order_side: str, 
									price: int,
									size: int,
									lever: int,
									*args, **kwargs):
		"""
		order_type 	- Either limit or market
		order_side 	- Either buy or sell
		size 		- LOTS of asset to purchase
		lever 		- Leverage value

		Ref: https://docs.kucoin.com/futures/#place-an-order
		"""
		return 	self.futures_trade.create_limit_order( 	symbol 	= symbol,
														type 	= order_type,
														side 	= order_side,
														price 	= price,
														size 	= size,
														lever	= lever
													)

	def delete_spot_order(self, order_id: str):
		pass

	def delete_futures_order(self, order_id: str):
		pass