import deprecation
from abc import ABCMeta
from abc import abstractmethod

class ExchangeSpotClients(metaclass = ABCMeta):
	@abstractmethod
	def get_spot_symbols(self):
		"""
		Fetches all spot instrument symbols
		"""
		pass

	@abstractmethod
	def get_spot_trading_account_details(self, currency: str):
		"""
		Retrieves spot trading details
		"""
		pass

	@abstractmethod
	def get_spot_trading_price(self, symbol: str):
		"""
		Retrieves current spot pricing for trading symbol
		"""
		pass

	@abstractmethod
	def get_spot_min_volume(self, symbol: str):
		"""
		Retrieves minimum order volume for spot trading symbol
		"""
		pass

	@abstractmethod
	def get_spot_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the spot asset, assuming that we intend to trade at a given volume. 
		"""
		pass


	@abstractmethod
	def get_spot_open_orders(self, symbol: str):
		"""
		Gets information of all open spot orders by the user
		"""
		pass

	@abstractmethod
	def get_spot_most_recent_open_order(self, symbol: str):
		"""
		Gets the most recent open orders for spot
		"""
		pass

	@abstractmethod
	def get_spot_fulfilled_orders(self, symbol: str):
		"""
		Gets information for all fulfilled spot orders by the user
		"""
		pass

	@abstractmethod
	def get_spot_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent spot trade that have been fulfilled
		"""
		pass

	@abstractmethod 
	def place_spot_order(self, *args, **kwargs):
		pass

	@abstractmethod
	def revert_spot_order(self, order_resp, *args, **kwargs):
		pass

	@abstractmethod
	def assert_spot_resp_error(self, order_resp):
		"""
		Function looks at an order response created after placing an order and decides if we should raise an error.

		A raised error indicates a failed order attempt.
		"""
		pass