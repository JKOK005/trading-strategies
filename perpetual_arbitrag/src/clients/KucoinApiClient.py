import logging
from kucoin.client import Market as Market_C, Trade as Trade_C, User as User_C
from kucoin_futures.client import Market as Market_F, Trade as Trade_F, User as User_F
from clients.Clients import ExchangeClients

class KucoinApiClient(ExchangeClients):
	default_page_size 			= 50
	spot_client 				= None
	futures_client 				= None
	futures_trade 				= None
	futures_user 				= None
	kucoin_spot_url 			= "https://api.kucoin.com"
	kucoin_spot_sandbox_url 	= "https://openapi-sandbox.kucoin.com"
	kucoin_futures_url 			= "https://api-futures.kucoin.com"
	kucoin_futures_sandbox_url 	= "https://api-sandbox-futures.kucoin.com"
	logger 						= logging.getLogger('KucoinApiClient')

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

	def get_spot_open_orders(self, symbol: str):
		"""
		Gets information of all open spot orders by the user

		symbol 	- Filter out all orders with matching symbol
		"""		
		resp 			= self.spot_trade.get_order_list(status = "active")
		pages 			= resp["totalPage"]
		active_orders 	= resp["items"]

		if pages > 1:
			for each_page_num in range(1, pages +1):
				resp 	= self.spot_trade.get_order_list(status = "active", currentPage = each_page_num, pageSize = self.default_page_size)
				active_orders += resp["items"]
		return list(filter(lambda x: x["symbol"] == symbol, active_orders))

	def get_futures_open_orders(self, symbol: str):
		"""
		Gets information of all open future orders by the user

		symbol 	- Filter out all orders with matching symbol
		"""
		resp 			= self.futures_trade.get_order_list(status = "active")
		pages 			= resp["totalPage"]
		active_orders 	= resp["items"]

		if pages > 1:
			for each_page_num in range(1, pages +1):
				resp 	= self.futures_trade.get_order_list(status = "active", currentPage = each_page_num, pageSize = self.default_page_size)
				active_orders += resp["items"]
		return list(filter(lambda x: x["symbol"] == symbol, active_orders))

	def get_spot_most_recent_open_order(self, symbol: str):
		"""
		Gets the most recent open orders for spot
		"""
		all_open_orders = self.get_spot_open_orders(symbol = symbol)
		if len(all_open_orders) > 0:
			return sorted(all_open_orders, key = lambda x: x["createdAt"], reverse = True)[0]
		else:
			return None

	def get_futures_most_recent_open_order(self, symbol: str):
		"""
		Gets the most recent open orders for futures
		"""
		all_open_orders = self.get_futures_open_orders(symbol = symbol)
		if len(all_open_orders) > 0:
			return sorted(all_open_orders, key = lambda x: x["createdAt"], reverse = True)[0]
		else:
			return None

	def get_spot_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent spot trades that have been fulfilled
		"""
		recent_trades 	= self.spot_trade.get_recent_orders()
		if type(recent_trades) == dict:
			recent_trades = recent_trades["data"]

		if len(recent_trades) > 0:
			return sorted(recent_trades, key = lambda x: x["createdAt"], reverse = True)[0]
		else:
			return None

	def get_futures_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent futures trades that have been fulfilled
		"""
		recent_fills 	= self.futures_trade.get_recent_fills()
		if type(recent_fills) == dict:
			recent_fills = recent_fills["data"]

		if len(recent_fills) > 0:
			return sorted(recent_fills, key = lambda x: x["createdAt"], reverse = True)[0]
		else:
			return None

	def place_spot_order(self, 	symbol: str, 
								order_type: str, 
								order_side: str, 
								price: int,
								size: float,
								*args, **kwargs):
		"""
		order_type 	- Either limit or market
		order_side 	- Either buy or sell
		size 		- VOLUME of asset to purchase

		Ref: https://docs.kucoin.com/#place-a-new-order
		"""
		self.logger.info(f"Sport order - asset: {symbol}, side: {order_side}, type: {order_type}, price: {price}, size: {size}")
		return 	self.spot_trade.create_market_order(symbol 	= symbol,
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
		self.logger.info(f"Futures order - asset: {symbol}, side: {order_side}, type: {order_type}, price: {price}, size: {size}, leverage: {lever}")
		return 	self.futures_trade.create_limit_order( 	symbol 	= symbol,
														type 	= order_type,
														side 	= order_side,
														price 	= price,
														size 	= size,
														lever	= lever
													)

	def cancel_spot_order(self, order_id: str):
		self.logger.info(f"Cancelling spot order ID {order_id}")

		try:
			self.spot_trade.cancel_order(orderId = order_id)
		except Exception as ex:
			self.logger.error(ex)
		return

	def cancel_futures_order(self, order_id: str):
		self.logger.info(f"Cancelling futures order ID {order_id}")
		
		try:
			self.futures_trade.cancel_order(orderId = order_id)
		except Exception as ex:
			self.logger.error(ex)
		return