import datetime
import logging
import sys
from datetime import timedelta
from okex.Account_api import AccountAPI
from okex.Market_api import MarketAPI
from okex.Public_api import PublicAPI
from okex.Trade_api import TradeAPI
from clients.ExchangeSpotClients import ExchangeSpotClients
from clients.ExchangePerpetualClients import ExchangePerpetualClients

class OkxApiClient(ExchangeSpotClients, ExchangePerpetualClients):
	account_client 	= None
	trade_client 	= None
	market_client 	= None
	logger 			= logging.getLogger('okxApiClient')

	okx_funding_rate_snapshot_times = ["04:00", "12:00", "20:00"]

	def __init__(self, 	api_key: str, 
						api_secret_key: str,
						passphrase: str,
						funding_rate_enable: bool,
						is_simulated: bool = False,
				):
		
		self.account_client = AccountAPI(api_key = api_key, 
										 api_secret_key = api_secret_key, 
										 passphrase = passphrase,
										 flag = '1' if is_simulated else '0'
								   	)

		self.market_client 	= MarketAPI(api_key = api_key, 
										api_secret_key = api_secret_key, 
										passphrase = passphrase,
										flag = '1' if is_simulated else '0'
								  	)

		self.public_client 	= PublicAPI(api_key = api_key, 
										api_secret_key = api_secret_key, 
										passphrase = passphrase,
										flag = '1' if is_simulated else '0'
								 	)

		self.trade_client 	= TradeAPI(	api_key = api_key, 
										api_secret_key = api_secret_key, 
										passphrase = passphrase, 
										flag = '1' if is_simulated else '0'
									)

		self.funding_rate_enable = funding_rate_enable
		self.logger.info(f"Enable for funding rate computation set to {funding_rate_enable}")
		return

	def get_spot_trading_account_details(self, currency: str):
		"""
		Retrieves spot trading details
		"""
		spot_info = self.account_client.get_account(ccy = currency)
		return float(spot_info["data"][0]["details"][0]["eq"])

	def get_perpetual_trading_account_details(self, currency: str):
		"""
		Retrieves perpetual trading account details
		"""
		perpetual_info = self.account_client.get_positions(instType = "SWAP", instId = currency)
		positions = list(map(lambda x: (x["availPos"], x["posSide"]), perpetual_info["data"]))
		net_position = 0
		for each_position in positions:
			if each_position[0] is not '':
				pos_multiplier = -1 if each_position[-1] == "short" else 1
				net_position += pos_multiplier * float(each_position[0]) 
		return net_position

	def get_spot_trading_price(self, symbol: str):
		"""
		Retrieves current spot pricing for trading symbol
		"""
		asset_resp = self.market_client.get_ticker(instId = symbol)
		asset_info = asset_resp["data"][0]
		return float(asset_info["last"])

	def get_perpetual_trading_price(self, symbol: str):
		"""
		Retrieves current perpetual price for trading symbol
		"""
		asset_resp = self.market_client.get_ticker(instId = symbol)
		asset_info = asset_resp["data"][0]
		return float(asset_info["last"])

	def get_spot_min_volume(self, symbol: str):
		"""
		Retrieves minimum order volume for spot trading symbol
		"""
		asset_resp = self.public_client.get_instruments(instType = "SPOT", instId = symbol)
		asset_info = asset_resp["data"][0]
		return float(asset_info["minSz"])

	def get_perpetual_min_lot_size(self, symbol: str):
		"""
		Retrieves minimum order lot size for perpetual trading symbol
		"""
		asset_resp = self.public_client.get_instruments(instType = "SWAP", instId = symbol)
		asset_info = asset_resp["data"][0]
		return float(asset_info["minSz"])

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
		Returns the average bid / ask price of the spot asset, assuming that we intend to trade at a given volume.
		"""
		bid_ask_resp 		= self.market_client.get_orderbook(instId = symbol, sz = 100)
		bid_ask_orders 		= bid_ask_resp["data"][0]
		
		bids 				= bid_ask_orders["bids"]
		bids 				= list(map(lambda x: [float(x[0]), float(x[1])], bids))
		average_bid_price 	= self._compute_average_bid_price(bids = bids, size = size)

		asks 				= bid_ask_orders["asks"]
		asks 				= list(map(lambda x: [float(x[0]), float(x[1])], asks))
		average_sell_price 	= self._compute_average_ask_price(asks = asks, size = size)
		return (average_bid_price, average_sell_price)

	def get_perpetual_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the perpetual asset, assuming that we intend to trade at a given lot size. 
		"""
		bid_ask_resp 		= self.market_client.get_orderbook(instId = symbol, sz = 100)
		bid_ask_orders 		= bid_ask_resp["data"][0]

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
		"""
		resp = self.trade_client.get_order_list(instType = "SPOT", instId = symbol, limit = 50)
		return resp["data"]

	def get_perpetual_open_orders(self, symbol: str):
		"""
		Gets information of all open future orders by the user
		"""
		resp = self.trade_client.get_order_list(instType = "SWAP", instId = symbol, limit = 50)
		return resp["data"]

	def get_spot_most_recent_open_order(self, symbol: str):
		"""
		Gets the most recent open orders for spot
		"""
		open_orders 	= self.get_spot_open_orders(symbol = symbol)
		sorted_orders 	= sorted(open_orders, key = lambda d: d['uTime'], reverse = True) 
		most_recent_open_order = sorted_orders[0] if len(sorted_orders) > 0 else sorted_orders
		return most_recent_open_order

	def get_perpetual_most_recent_open_order(self, symbol: str):
		"""
		Gets the most recent open orders for perpetual

		Based on https://www.okx.com/docs/en/#futures-list , the most recent order is at the first entry
		"""
		open_orders 	= self.get_perpetual_open_orders(symbol = symbol)
		sorted_orders 	= sorted(open_orders, key = lambda d: d['uTime'], reverse = True) 
		most_recent_open_order = sorted_orders[0] if len(sorted_orders) > 0 else sorted_orders
		return most_recent_open_order

	def get_spot_fulfilled_orders(self, symbol: str):
		"""
		Gets information for all fulfilled spot orders by the user
		"""
		resp = self.trade_client.get_orders_history(instType = "SPOT", instId = symbol, state = "filled", limit = 50)
		return resp["data"]

	def get_perpetual_fulfilled_orders(self, symbol: str):
		"""
		Gets information of all fulfilled future orders by the user
		"""
		resp = self.trade_client.get_orders_history(instType = "SWAP", instId = symbol, state = "filled", limit = 50)
		return resp["data"]

	def get_spot_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent spot trade that have been fulfilled
		"""
		fulfilled_orders 	= self.get_spot_fulfilled_orders(symbol = symbol)
		sorted_orders 		= sorted(fulfilled_orders, key = lambda d: int(d['uTime']), reverse = True) 
		most_recent_fulfilled_order = sorted_orders[0] if len(sorted_orders) > 0 else sorted_orders
		return most_recent_fulfilled_order

	def get_perpetual_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent perpetual trade that have been fulfilled
		"""
		fulfilled_orders 	= self.get_perpetual_fulfilled_orders(symbol = symbol)
		sorted_orders 		= sorted(fulfilled_orders, key = lambda d: int(d['uTime']), reverse = True) 
		most_recent_fulfilled_order = sorted_orders[0] if len(sorted_orders) > 0 else sorted_orders
		return most_recent_fulfilled_order

	def get_perpetual_funding_rate(self, symbol: str):
		"""
		Gets the immediate and predicted funding rate for futures contract
		"""
		funding_rate_resp = self.public_client.get_funding_rate(instId = symbol)
		funding_rate_info = funding_rate_resp["data"][0]
		return (float(funding_rate_info["fundingRate"]), float(funding_rate_info["nextFundingRate"]))

	def funding_rate_valid_interval(self, seconds_before: int):
		current_time = datetime.datetime.utcnow()
		for each_snaphsot_time in self.okx_funding_rate_snapshot_times:
			ts = datetime.datetime.strptime(each_snaphsot_time, "%H:%M")
			snapshot_timestamp = current_time.replace(hour = ts.hour, minute = ts.minute, second = 0)
			if snapshot_timestamp - timedelta(seconds = seconds_before) <= current_time and current_time <= snapshot_timestamp:
				return True
		return False

	def get_perpetual_effective_funding_rate(self, symbol: str, seconds_before: int):
		"""
		Gets the effective funding rate for perpetual contract.

		Effective funding rate takes into account a variety of factors to decide on the funding rate.

		1) If we are not within a valid funding interval, then the estimated funding rates are 0.
		2) If funding rate computation has been disabled, then all rates are 0.
		"""
		(funding_rate, estimated_funding_rate) = (0, 0)
		if self.funding_rate_enable: 
			if self.funding_rate_valid_interval(seconds_before = seconds_before):
				(funding_rate, estimated_funding_rate) = self.get_perpetual_funding_rate(symbol = symbol)
			else:
				(funding_rate, _) = self.get_perpetual_funding_rate(symbol = symbol)
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
		"""
		self.logger.info(f"Sport order - asset: {symbol}, side: {order_side}, type: {order_type}, price: {price}, size: {size}")
		if order_type == "limit":
			return self.trade_client.place_order(instId 	= symbol,
												 tdMode		= "cash",
												 side 		= order_side,
												 ordType 	= order_type,
												 sz 		= size,
												 px 		= price,
											)
		elif order_type == "market":
			return self.trade_client.place_order(instId 	= symbol,
												 tdMode		= "cash",
												 side 		= order_side,
												 ordType 	= order_type,
												 sz 		= size,
											)

	def place_perpetual_order(self, symbol: str, 
									position_side: str, 
									order_type: str, 
									order_side: str,
									price: int,
									size: int,
									*args, **kwargs):
		"""
		order_type 	- Either limit or market
		order_side 	- Either buy or sell
		size 		- LOTS of asset to purchase

		position_side = long, order_side = buy 		-> Open long on asset
		position_side = long, order_side = sell 	-> Close long on asset
		position_side = short, order_side = buy 	-> Close short on asset
		position_side = short, order_side = sell 	-> Open short on asset
		"""
		self.logger.info(f"Open perpetual order - asset: {symbol}, side: {order_side}, type: {order_type}, price: {price}, size: {size}")
		if order_type == "limit":
			return self.trade_client.place_order(instId 	= symbol,
												 tdMode		= "cross",
												 posSide 	= position_side,
												 ordType 	= order_type,
												 side 		= order_side,
												 sz 		= size,
												 px 		= price,
												 reduceOnly = "true",
											)
		elif order_type == "market":
			return self.trade_client.place_order(instId 	= symbol,
												 tdMode		= "cross",
												 posSide 	= position_side,
												 ordType 	= order_type,
												 side 		= order_side,
												 sz 		= size,
												 reduceOnly = "true",
											)

	def cancel_spot_order(self, symbol: str, order_id: str):
		self.logger.info(f"Cancelling spot order ID {order_id}")

		try:
			self.trade_client.cancel_order(instId = symbol, ordId = order_id)
		except Exception as ex:
			self.logger.error(ex)
		return

	def cancel_perpetual_order(self, symbol: str, order_id: str):
		self.logger.info(f"Cancelling futures order ID {order_id}")

		try:
			self.trade_client.cancel_order(instId = symbol, ordId = order_id)
		except Exception as ex:
			self.logger.error(ex)
		return