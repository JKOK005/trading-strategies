import datetime
import deprecation
import logging
import sys
from datetime import timedelta
from kucoin.client import Market as Market_C, Trade as Trade_C, User as User_C
from kucoin_futures.client import Market as Market_F, Trade as Trade_F, User as User_F
from clients.ExchangeSpotClients import ExchangeSpotClients
from clients.ExchangeFutureClients import ExchangeFutureClients

class KucoinApiClient(ExchangeSpotClients, ExchangeFutureClients):
	default_page_size 			= 50
	spot_client 				= None
	futures_client 				= None
	futures_trade 				= None
	futures_user 				= None
	logger 						= logging.getLogger('KucoinApiClient')

	kucoin_spot_url 			= "https://api.kucoin.com"
	kucoin_spot_sandbox_url 	= "https://openapi-sandbox.kucoin.com"
	kucoin_futures_url 			= "https://api-futures.kucoin.com"
	kucoin_futures_sandbox_url 	= "https://api-sandbox-futures.kucoin.com"
	kucoin_funding_rate_snapshot_times = ["04:00", "12:00", "20:00"]
	
	def __init__(self, 	spot_client_api_key: str, 
						spot_client_api_secret_key: str, 
						spot_client_pass_phrase: str,
						futures_client_api_key: str, 
						futures_client_api_secret_key: str, 
						futures_client_pass_phrase: str,
						sandbox: bool,
						funding_rate_enable: bool
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

		self.funding_rate_enable = funding_rate_enable
		self.logger.info(f"Enable for funding rate computation set to {funding_rate_enable}")
		return

	def get_spot_trading_account_details(self, currency: str):
		"""
		Retrieves spot trading details
		"""
		spot_accounts 	= self.spot_user.get_account_list()
		return list(filter(lambda x: x["type"] == "trade" and x["currency"] == currency, spot_accounts))[0]

	def get_futures_trading_account_details(self, currency: str):
		"""
		Retrieves futures trading account details
		"""
		futures_account = self.futures_user.get_account_overview(currency = currency)
		return futures_account

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

	def get_spot_min_volume(self, symbol: str):
		"""
		Retrieves minimum order volume for spot trading symbol
		"""
		all_spot_info 	= self.spot_client.get_symbol_list()
		spot_info 		= next(filter(lambda x: x["symbol"] == symbol, all_spot_info))
		return float(spot_info["baseMinSize"])

	def get_futures_min_lot_size(self, symbol: str):
		"""
		Retrieves minimum order lot size for futures trading symbol
		"""
		futures_info = self.futures_client.get_contract_detail(symbol = symbol)
		return int(futures_info["lotSize"])

	def _compute_average_margin_purchase_price(self, price_qty_pairs_ordered: [float, float], size: float):
		"""
		We will read pricing - qty data from the first entry of the list. 

		This logic will differ, depending on whether we want to go long / short on the asset. 
		As such, the ordering of the price-qty pairs in the list has to be handled properly by the user. 
		"""
		all_trade_qty 		= size
		trade_amt 			= 0
		executed_trade_qty 	= 0
		for each_price_qty_pairs in price_qty_pairs_ordered:
			if all_trade_qty < 0:
				break
			else:
				[price, qty] 	=  each_price_qty_pairs
				trade_qty 		=  min(all_trade_qty, qty)
				trade_amt 	 	+= price * trade_qty
				all_trade_qty 	-= trade_qty
				executed_trade_qty += trade_qty
		return trade_amt / executed_trade_qty

	def _compute_average_bid_price(self, bids: [[float, float]], size: float):
		# Sell into bids starting from the highest to the lowest.
		_bids 	= sorted(bids, key = lambda x: x[0], reverse = True)
		if len(_bids) > 0:
			return self._compute_average_margin_purchase_price(price_qty_pairs_ordered = _bids, size = size)
		return 0

	def _compute_average_ask_price(self, asks: [[float, float]], size: float):
		# Buy into asks starting from the lowest to the highest.
		_asks 	= sorted(asks, key = lambda x: x[0], reverse = False)
		if len(_asks) > 0:
			return self._compute_average_margin_purchase_price(price_qty_pairs_ordered = _asks, size = size)
		return sys.maxsize

	def get_spot_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the spot asset.
		Assuming that we buy / sell all the asset at the given volume. 
		"""
		bid_ask_orders 		= self.spot_client.get_part_order(symbol = symbol, pieces = 100)
		bids 				= bid_ask_orders["bids"]
		bids 				= list(map(lambda x: [float(x[0]), float(x[1])], bids))
		average_bid_price 	= self._compute_average_bid_price(bids = bids, size = size)

		asks 				= bid_ask_orders["asks"]
		asks 				= list(map(lambda x: [float(x[0]), float(x[1])], asks))
		average_sell_price 	= self._compute_average_ask_price(asks = asks, size = size)
		return (average_bid_price, average_sell_price)

	def get_futures_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the futures asset.
		Assuming that we buy / sell all the asset at the given lot size. 
		"""
		# bid_ask_orders 		= self.futures_client.l2_order_book(symbol = symbol)
		bid_ask_orders 		= self.futures_client.l2_part_order_book(symbol = symbol, depth = 100)
		bids 				= bid_ask_orders["bids"]
		bids 				= list(map(lambda x: [float(x[0]), float(x[1])], bids))
		average_bid_price 	= self._compute_average_bid_price(bids = bids, size = size)

		asks 				= bid_ask_orders["asks"]
		asks 				= list(map(lambda x: [float(x[0]), float(x[1])], asks))
		average_sell_price 	= self._compute_average_ask_price(asks = asks, size = size)
		return (average_bid_price, average_sell_price)

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

	def get_spot_fulfilled_orders(self, symbol: str):
		"""
		Gets information for all fulfilled spot orders by the user

		symbol 	- Filter out all orders with matching symbol

		TODO:
		- Complete implementation
		"""
		resp 			= self.spot_trade.get_recent_orders()
		recent_trades 	= resp["data"]
		return list(filter(lambda x: x["symbol"] == symbol, recent_trades))

	def get_futures_fulfilled_orders(self, symbol: str):
		"""
		Gets information of all fulfilled future orders by the user

		symbol 	- Filter out all orders with matching symbol

		TODO:
		- Complete implementation
		"""
		resp 			= self.futures_trade.get_recent_fills()
		recent_fills 	= resp["data"]
		return list(filter(lambda x: x["symbol"] == symbol, recent_fills))

	def get_spot_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent spot trades that have been fulfilled

		TODO:
		- Make call to get_spot_fulfilled_orders before filtering
		"""
		recent_trades 	= self.get_spot_fulfilled_orders(symbol = symbol)

		if len(recent_trades) > 0:
			return sorted(recent_trades, key = lambda x: x["createdAt"], reverse = True)[0]
		else:
			return None

	def get_futures_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent futures trades that have been fulfilled

		TODO:
		- Make call to get_futures_fulfilled_orders before filtering
		"""
		recent_fills 	= self.get_futures_fulfilled_orders(symbol = symbol)

		if len(recent_fills) > 0:
			return sorted(recent_fills, key = lambda x: x["createdAt"], reverse = True)[0]
		else:
			return None

	def get_futures_funding_rate(self, symbol: str):
		"""
		Gets the immediate and predicted funding rate for futures contract
		"""
		funding_rate_info = self.futures_client.get_current_fund_rate(symbol = f".{symbol}FPI8H")
		return (funding_rate_info["value"], funding_rate_info["predictedValue"])

	def funding_rate_valid_interval(self, seconds_before: int):
		current_time = datetime.datetime.utcnow()
		for each_snaphsot_time in self.kucoin_funding_rate_snapshot_times:
			ts = datetime.datetime.strptime(each_snaphsot_time, "%H:%M")
			snapshot_timestamp = current_time.replace(hour = ts.hour, minute = ts.minute, second = 0)
			if snapshot_timestamp - timedelta(seconds = seconds_before) <= current_time and current_time <= snapshot_timestamp:
				return True
		return False

	def get_futures_effective_funding_rate(self, symbol: str, seconds_before: int):
		"""
		Effective funding rate takes into account a variety of factors to decide on the funding rate.

		1) If we are not within a valid funding interval, then the estimated funding rates are 0.
		2) If funding rate computation has been disabled, then all rates are 0.
		"""
		(funding_rate, estimated_funding_rate) = (0, 0)
		if self.funding_rate_enable: 
			if self.funding_rate_valid_interval(seconds_before = seconds_before):
				(funding_rate, estimated_funding_rate) = self.get_futures_funding_rate(symbol = symbol)
			else:
				(funding_rate, _) = self.get_futures_funding_rate(symbol = symbol)
		self.logger.info(f"Funding rate: {funding_rate}, Estimated funding rate: {estimated_funding_rate}")
		return (funding_rate, estimated_funding_rate)

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

	def cancel_spot_order(self, order_resp):
		order_id = order_resp["orderId"]
		self.logger.info(f"Cancelling spot order ID {order_id}")

		try:
			self.spot_trade.cancel_order(orderId = order_id)
		except Exception as ex:
			self.logger.error(ex)
		return

	def cancel_futures_order(self, order_resp):
		order_id = order_resp["orderId"]
		self.logger.info(f"Cancelling futures order ID {order_id}")
		
		try:
			self.futures_trade.cancel_order(orderId = order_id)
		except Exception as ex:
			self.logger.error(ex)
		return

	def revert_spot_order(self, order_resp, revert_params):
		self.logger.info(f"Reverting spot order")
		return self.place_spot_order(**revert_params)

	def revert_futures_order(self, order_resp, revert_params):
		self.logger.info(f"Reverting futures order")
		return self.place_futures_order(**revert_params)

	def assert_spot_resp_error(self, order_resp):
		"""
		Kucoin throws a response error on failure, hence no need to implement logics
		"""
		return

	def assert_futures_resp_error(self, order_resp):
		"""
		Kucoin throws a response error on failure, hence no need to implement logics
		"""
		return