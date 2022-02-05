import deprecation
from abc import ABCMeta
from abc import abstractmethod

class ExchangeFutureClients(metaclass = ABCMeta):
	@abstractmethod
	def get_futures_trading_account_details(self, currency: str):
		"""
		Retrieves futures trading account details
		"""
		pass

	@abstractmethod
	def get_futures_trading_price(self, symbol: str):
		"""
		Retrieves current futures price for trading symbol
		"""
		pass

	@abstractmethod
	def get_futures_min_lot_size(self, symbol: str):
		"""
		Retrieves minimum order lot size for futures trading symbol
		"""
		pass

	@abstractmethod
	def get_futures_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the futures asset, assuming that we intend to trade at a given lot size. 
		"""
		pass

	@abstractmethod
	def get_futures_open_orders(self, symbol: str):
		"""
		Gets information of all open future orders by the user
		"""
		pass

	@abstractmethod
	def get_futures_most_recent_open_order(self, symbol: str):
		"""
		Gets the most recent open orders for futures
		"""
		pass

	@abstractmethod
	def get_futures_fulfilled_orders(self, symbol: str):
		"""
		Gets information of all fulfilled future orders by the user
		"""
		pass

	@abstractmethod
	def get_futures_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent futures trade that have been fulfilled
		"""
		pass

	@abstractmethod
	def get_futures_effective_funding_rate(self, symbol: str, seconds_before: int):
		"""
		Gets the effective funding rate for futures contract.

		Effective funding rate takes into account a variety of factors to decide on the funding rate.
		"""
		pass

	@abstractmethod
	def place_futures_order(self, *args, **kwargs):
		pass

	@abstractmethod
	def cancel_futures_order(self, order_id: str):
		pass