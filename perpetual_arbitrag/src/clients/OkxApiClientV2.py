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
						price_feed_client,
						funding_rate_enable: bool,
						is_simulated: bool = False,
				):
		pass

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
		pass

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