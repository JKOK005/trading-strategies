import datetime
import ftx
import logging
import sys
from datetime import timedelta
from clients.ExchangeSpotClients import ExchangeSpotClients
from clients.ExchangePerpetualClients import ExchangePerpetualClients
from clients.ExchangeMarginClients import ExchangeMarginClients

class FtxApiClient(ExchangePerpetualClients):
	client 	= None
	logger 	= logging.getLogger('FtxApiClient')

	ftx_funding_rate_snapshot_times = [...]

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