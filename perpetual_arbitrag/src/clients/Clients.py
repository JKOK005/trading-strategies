from abc import ABCMeta
from abc import abstractmethod

class ExchangeClients(metaclass = ABCMeta):
	@abstractmethod
	def get_spot_trading_price(self, symbol: str):
		"""
		Retrieves current spot pricing for trading symbol
		"""
		pass

	@abstractmethod
	def get_futures_trading_price(self, symbol: str):
		"""
		Retrieves current futures price for trading symbol
		"""
		pass

	@abstractmethod
	def get_spot_open_orders(self, symbol: str):
		"""
		Gets information of all open spot orders by the user
		"""
		pass

	@abstractmethod
	def get_futures_open_orders(self, symbol: str):
		"""
		Gets information of all open future orders by the user
		"""
		pass

	@abstractmethod
	def get_spot_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent spot trade that have been fulfilled
		"""
		pass

	@abstractmethod
	def get_futures_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent futures trade that have been fulfilled
		"""
		pass

	@abstractmethod 
	def place_spot_order(self, *args, **kwargs):
		pass

	@abstractmethod
	def place_futures_order(self, *args, **kwargs):
		pass

	@abstractmethod
	def cancel_spot_order(self, order_id: str):
		pass

	@abstractmethod
	def cancel_futures_order(self, order_id: str):
		pass