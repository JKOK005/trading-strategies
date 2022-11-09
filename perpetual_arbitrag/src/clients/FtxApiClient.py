import asyncio
import datetime
import ftx
import logging
import sys
from datetime import timedelta
from clients.ExchangeSpotClients import ExchangeSpotClients
from clients.ExchangePerpetualClients import ExchangePerpetualClients
from clients.ExchangeMarginClients import ExchangeMarginClients

class FtxApiClient(ExchangeMarginClients, ExchangePerpetualClients):
	client 	= None
	logger 	= logging.getLogger('FtxApiClient')

	def __init__(self, 	api_key: str, 
						api_secret_key: str,
						funding_rate_enable: bool,
				):
		self.client 				= ftx.FtxClient(api_key = api_key, api_secret = api_secret_key)
		self.api_key 				= api_key
		self.api_secret_key 		= api_secret_key
		self.funding_rate_enable 	= funding_rate_enable
		self.logger.info(f"Enable for funding rate computation set to {funding_rate_enable}")
		return

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

	def set_account_leverage(self, leverage: int):
		self.logger.debug(f"Set account leverage: {leverage}")
		self.client.set_leverage(leverage = leverage)
		return

	def get_perpetual_symbols(self):
		"""
		Fetches all perpetual instrument symbols
		"""
		resp 	= self.client.get_markets()
		assets 	= list(map(lambda x: x["name"], resp))
		return list(filter(lambda x: "-PERP" in x.upper(), assets))

	def get_perpetual_trading_account_details(self, currency: str):
		"""
		Retrieves perpetual trading account details
		"""
		resp = self.client.get_positions()
		relevant_asset_position = next(filter(lambda x: x["future"] == currency, resp))
		return relevant_asset_position["netSize"]

	def get_perpetual_trading_price(self, symbol: str):
		"""
		Retrieves current perpetual price for trading symbol
		"""
		resp = self.client.get_market(market = symbol)
		return resp["price"]

	def get_perpetual_min_lot_size(self, symbol: str):
		"""
		Retrieves minimum order lot size for perpetual trading symbol
		"""
		resp = self.client.get_market(market = symbol)
		return resp["sizeIncrement"]

	def get_perpetual_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the perpetual asset, assuming that we intend to trade at a given lot size. 
		"""
		bid_ask_resp 		= self.client.get_orderbook(market = symbol, depth = 10)
		
		bids 				= bid_ask_orders["bids"]
		average_bid_price 	= self._compute_average_bid_price(bids = bids, size = size)

		asks 				= bid_ask_orders["asks"]
		average_sell_price 	= self._compute_average_ask_price(asks = asks, size = size)		
		return (average_bid_price, average_sell_price)

	def get_perpetual_open_orders(self, symbol: str):
		"""
		Gets information of all open perpetual orders by the user
		"""
		open_orders = self.client.get_open_orders(market = symbol)
		return open_orders

	def get_perpetual_most_recent_open_order(self, symbol: str):
		"""
		Gets the most recent open orders for perpetual
		"""
		open_orders 			= self.get_perpetual_open_orders(market = symbol)
		sorted_orders 			= sorted(open_orders, key = lambda d: d['createdAt'], reverse = True)
		most_recent_open_order 	= sorted_orders[0] if len(sorted_orders) > 0 else sorted_orders
		return most_recent_open_order

	def get_perpetual_fulfilled_orders(self, symbol: str):
		"""
		Gets information of all fulfilled perpetual orders by the user
		"""
		order_history 		= self.client.get_order_history(market = symbol)
		fulfilled_orders 	= list(filter(lambda x: x["status"] == "closed", order_history))
		return fulfilled_orders

	def get_perpetual_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent perpetual trade that have been fulfilled
		"""
		fulfilled_orders 			= self.get_perpetual_fulfilled_orders(symbol = symbol)
		sorted_orders 				= sorted(fulfilled_orders, key = lambda d: d['createdAt'], reverse = True)
		most_recent_fulfilled_order = sorted_orders[0] if len(sorted_orders) > 0 else sorted_orders
		return most_recent_fulfilled_order

	def get_perpetual_funding_rate(self, symbol: str):
		"""
		Gets the immediate and predicted funding rate for futures contract
		"""
		funding_rate_resp = self.client.get_future_stats(future_name = symbol)
		return float(funding_rate_resp["nextFundingRate"]), funding_rate_resp["nextFundingTime"]

	def get_perpetual_effective_funding_rate(self, symbol: str, seconds_before_current: int):
		"""
		Gets the effective funding rate for perpetual contract.

		Effective funding rate takes into account a variety of factors to decide on the funding rate.

		1) If we are not within a valid funding interval, then the funding rates are 0.
		2) If we are within the valid funding interval, then the funding rate is non-zero.
		3) If funding rate computation has been disabled, then all rates are 0.
		"""
		current_time 					= datetime.datetime.utcnow()
		funding_rate, next_funding_time = self.get_perpetual_funding_rate(symbol = symbol)
		next_funding_time 				= datetime.datetime.strptime(next_funding_time.split("+")[0], "%Y-%m-%dT%H:%M:%S")
		return funding_rate if (next_funding_time - timedelta(seconds = seconds_before_current) <= current_time) and \
								self.funding_rate_enable \
							else 0

	def place_perpetual_order(self, *args, **kwargs):
		# Unimplemented as we will be using WS client for trades
		raise Exception("Function <place_perpetual_order> should not be invoked on REST client")

	def revert_perpetual_order(self, order_resp, *args, **kwargs):
		# Unimplemented as we will be using WS client for trades
		raise Exception("Function <revert_perpetual_order> should not be invoked on REST client")

	def assert_perpetual_resp_error(self, order_resp):
		resp  			= order_resp["resp"]
		order_resp_code = resp.status
		if order_resp_code != "200":
			raise Exception(f"Perpetual order failed: {resp}")
		return

	async def place_perpetual_order_async(self, market: str,
												side: str,
												price: float,
												size: float, 
												order_type: str,
										):
		resp = self.client.place_order(	market 	= market,
  										side	= side,
										price 	= price,
										size 	= size,
 										type    = order_type
									)
		return {"id" : f"{market}-{side}", "resp" : resp}

	async def revert_perpetual_order_async(self, order_resp, revert_params):
		self.logger.debug(f"Reverting margin order")
		return await self.place_perpetual_order_async(**revert_params)

	def get_margin_symbols(self):
		resp 	= self.client.get_markets()
		assets 	= list(map(lambda x: x["name"], resp))
		return list(filter(lambda x: "-PERP" not in x.upper(), assets))

	def get_margin_trading_account_details(self, currency: str):
		resp 	= self.client.get_balances()
		symbol 	= currency.split("/")[0] 	# If currency is "BTC/USDT", then we want "BTC"
		relevant_asset_position = next(filter(lambda x: x["coin"] == symbol, resp))
		return relevant_asset_position["spotBorrow"]

	def get_margin_trading_price(self, symbol: str):
		resp = self.client.get_market(market = symbol)
		return resp["price"]

	def get_margin_min_volume(self, symbol: str):
		resp = self.client.get_market(market = symbol)
		return resp["sizeIncrement"]

	def get_margin_average_bid_ask_price(self, symbol: str, size: float):
		bid_ask_resp 		= self.client.get_orderbook(market = symbol, depth = 10)
		
		bids 				= bid_ask_orders["bids"]
		average_bid_price 	= self._compute_average_bid_price(bids = bids, size = size)

		asks 				= bid_ask_orders["asks"]
		average_sell_price 	= self._compute_average_ask_price(asks = asks, size = size)		
		return (average_bid_price, average_sell_price)

	def get_margin_open_orders(self, symbol: str):
		open_orders = self.client.get_open_orders(market = symbol)
		return open_orders

	def get_margin_most_recent_open_order(self, symbol: str):
		pass

	def get_margin_fulfilled_orders(self, symbol: str):
		pass

	def get_margin_most_recent_fulfilled_order(self, symbol: str):
		pass

	def get_margin_effective_funding_rate(self, symbol: str):
		pass

	def place_margin_order(self, *args, **kwargs):
		# Unimplemented as we will be using WS client for trades
		raise Exception("Function <place_margin_order> should not be invoked on REST client")

	def revert_margin_order(self, order_resp, *args, **kwargs):
		# Unimplemented as we will be using WS client for trades
		raise Exception("Function <revert_margin_order> should not be invoked on REST client")

	def assert_margin_resp_error(self, order_resp):
		pass

	async def place_perpetual_order_async(self, ...):
		pass

	async def revert_perpetual_order_async(self, ...):
		pass