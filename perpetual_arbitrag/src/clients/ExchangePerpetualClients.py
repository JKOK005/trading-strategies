import deprecation
from abc import ABCMeta
from abc import abstractmethod

class ExchangePerpetualClients(metaclass = ABCMeta):
	@abstractmethod
	def get_perpetual_trading_account_details(self, currency: str):
		"""
		Retrieves perpetual trading account details
		"""
		pass

	@abstractmethod
	def get_perpetual_trading_price(self, symbol: str):
		"""
		Retrieves current perpetual price for trading symbol
		"""
		pass

	@abstractmethod
	def get_perpetual_min_lot_size(self, symbol: str):
		"""
		Retrieves minimum order lot size for perpetual trading symbol
		"""
		pass

	@abstractmethod
	def get_perpetual_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the perpetual asset, assuming that we intend to trade at a given lot size. 
		"""
		pass

	@abstractmethod
	def get_perpetual_open_orders(self, symbol: str):
		"""
		Gets information of all open perpetual orders by the user
		"""
		pass

	@abstractmethod
	def get_perpetual_most_recent_open_order(self, symbol: str):
		"""
		Gets the most recent open orders for perpetual
		"""
		pass

	@abstractmethod
	def get_perpetual_fulfilled_orders(self, symbol: str):
		"""
		Gets information of all fulfilled perpetual orders by the user
		"""
		pass

	@abstractmethod
	def get_perpetual_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent perpetual trade that have been fulfilled
		"""
		pass

	@abstractmethod
	def get_perpetual_effective_funding_rate(self, symbol: str, seconds_before: int):
		"""
		Gets the effective funding rate for perpetual contract.

		Effective funding rate takes into account a variety of factors to decide on the funding rate.
		"""
		pass

	@abstractmethod
	def place_perpetual_order(self, *args, **kwargs):
		pass

	@abstractmethod
	def revert_perpetual_order(self, order_resp, *args, **kwargs):
		pass

	@abstractmethod
	def assert_perpetual_resp_error(self, order_resp):
		"""
		Function looks at an order response created after placing an order and decides if we should raise an error.

		A raised error indicates a failed order attempt.
		"""
		pass