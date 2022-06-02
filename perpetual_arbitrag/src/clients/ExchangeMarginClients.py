import deprecation
from abc import ABCMeta
from abc import abstractmethod

class ExchangeMarginClients(metaclass = ABCMeta):
	@abstractmethod
	def get_margin_symbols(self):
		"""
		Fetches all margin instrument symbols
		"""
		pass

	@abstractmethod
	def get_margin_trading_account_details(self, currency: str):
		"""
		Retrieves margin trading account details
		"""
		pass

	@abstractmethod
	def get_margin_trading_price(self, symbol: str):
		"""
		Retrieves current margin price for trading symbol
		"""
		pass

	@abstractmethod
	def get_margin_min_lot_size(self, symbol: str):
		"""
		Retrieves minimum order lot size for margin trading symbol
		"""
		pass

	@abstractmethod
	def get_margin_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the margin asset, assuming that we intend to trade at a given lot size. 
		"""
		pass

	@abstractmethod
	def get_margin_open_orders(self, symbol: str):
		"""
		Gets information of all open margin orders by the user
		"""
		pass

	@abstractmethod
	def get_margin_most_recent_open_order(self, symbol: str):
		"""
		Gets the most recent open orders for margin
		"""
		pass

	@abstractmethod
	def get_margin_fulfilled_orders(self, symbol: str):
		"""
		Gets information of all fulfilled margin orders by the user
		"""
		pass

	@abstractmethod
	def get_margin_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent margin trade that have been fulfilled
		"""
		pass

	@abstractmethod
	def get_margin_effective_funding_rate(self, symbol: str, seconds_before_current: int, seconds_before_estimated: int):
		"""
		Gets the effective funding rate for margin contract.

		Effective funding rate takes into account a variety of factors to decide on the funding rate.
		"""
		pass

	@abstractmethod
	def place_margin_order(self, *args, **kwargs):
		pass

	@abstractmethod
	def revert_margin_order(self, order_resp, *args, **kwargs):
		pass

	@abstractmethod
	def assert_margin_resp_error(self, order_resp):
		"""
		Function looks at an order response created after placing an order and decides if we should raise an error.

		A raised error indicates a failed order attempt.
		"""
		pass