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
	def get_spot_position(self, symbol: str):
		"""
		Gets the amount of assets position by the user
		"""
		pass

	@abstractmethod
	def get_futures_position(self, symbol: str):
		"""
		Gets the amount of futures position by the user
		"""
		pass

	@abstractmethod 
	def place_spot_order(self, *args, **kwargs):
		pass

	@abstractmethod
	def place_futures_order(self, *args, **kwargs):
		pass

	@abstractmethod
	def delete_spot_order(self, order_id: str):
		pass

	@abstractmethod
	def delete_futures_order(self, order_id: str):
		pass