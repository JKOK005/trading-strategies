import datetime
import logging
import sys
from datetime import timedelta
from clients.ExchangeSpotClients import ExchangeSpotClients
from clients.ExchangePerpetualClients import ExchangePerpetualClients

class OkxApiClientV2(ExchangeSpotClients, ExchangePerpetualClients):

	ws_client 	= None

	def __init__(self,	api_key: str,
						api_secret_key: str,
						passphrase: str,
						feed_client,
						funding_rate_enable: bool,
						is_simulated: bool = False,
				):
		self.api_key 		= api_key
		self.api_secret_key = api_secret_key
		self.passphrase 	= passphrase
		self.feed_client 	= feed_client
		self.is_simulated 	= is_simulated
		self.funding_rate_enable = funding_rate_enable
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

	def get_spot_trading_account_details(self, currency: str):
		"""
		Retrieves spot trading details
		"""
		pass

	def get_spot_trading_price(self, symbol: str):
		"""
		Retrieves current spot pricing for trading symbol
		"""
		pass

	def get_spot_min_volume(self, symbol: str):
		"""
		Retrieves minimum order volume for spot trading symbol
		"""
		pass

	def get_spot_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the spot asset, assuming that we intend to trade at a given volume. 
		"""
		order_book 			= self.sorted_order_book(exchange = "OKX", symbol = symbol)
		bids 				= order_book["bids"]
		average_bid_price 	= self._compute_average_bid_price(bids = bids, size = size)
		asks 				= order_book["asks"]
		average_ask_price 	= self._compute_average_ask_price(asks = asks, size = size)
		return (average_bid_price, average_sell_price)

	def get_spot_open_orders(self, symbol: str):
		"""
		Gets information of all open spot orders by the user
		"""
		pass

	def get_spot_most_recent_open_order(self, symbol: str):
		"""
		Gets the most recent open orders for spot
		"""
		pass

	def get_spot_fulfilled_orders(self, symbol: str):
		"""
		Gets information for all fulfilled spot orders by the user
		"""
		pass

	def get_spot_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent spot trade that have been fulfilled
		"""
		pass

	def place_spot_order(self, *args, **kwargs):
		pass

	def revert_spot_order(self, order_resp, *args, **kwargs):
		pass

	def assert_spot_resp_error(self, order_resp):
		"""
		Function looks at an order response created after placing an order and decides if we should raise an error.

		A raised error indicates a failed order attempt.
		"""
		pass

	def get_perpetual_trading_account_details(self, currency: str):
		"""
		Retrieves perpetual trading account details
		"""
		pass

	def get_perpetual_trading_price(self, symbol: str):
		"""
		Retrieves current perpetual price for trading symbol
		"""
		pass

	def get_perpetual_min_lot_size(self, symbol: str):
		"""
		Retrieves minimum order lot size for perpetual trading symbol
		"""
		pass

	def get_perpetual_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the perpetual asset, assuming that we intend to trade at a given lot size. 
		"""
		pass

	def get_perpetual_open_orders(self, symbol: str):
		"""
		Gets information of all open perpetual orders by the user
		"""
		pass

	def get_perpetual_most_recent_open_order(self, symbol: str):
		"""
		Gets the most recent open orders for perpetual
		"""
		pass

	def get_perpetual_fulfilled_orders(self, symbol: str):
		"""
		Gets information of all fulfilled perpetual orders by the user
		"""
		pass

	def get_perpetual_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent perpetual trade that have been fulfilled
		"""
		pass

	def get_perpetual_effective_funding_rate(self, symbol: str, seconds_before_current: int, seconds_before_estimated: int):
		"""
		Gets the effective funding rate for perpetual contract.

		Effective funding rate takes into account a variety of factors to decide on the funding rate.
		"""
		pass

	def place_perpetual_order(self, *args, **kwargs):
		pass

	def revert_perpetual_order(self, order_resp, *args, **kwargs):
		pass

	def assert_perpetual_resp_error(self, order_resp):
		"""
		Function looks at an order response created after placing an order and decides if we should raise an error.

		A raised error indicates a failed order attempt.
		"""
		pass