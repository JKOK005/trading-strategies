from abc import ABCMeta
from abc import abstractmethod

class Strategies(metaclass = ABCMeta)
	@abstractmethod
	def trade_decision(self, spot_price: float, futures_price: float):
		"""
		Returns a decision on which asset to buy / sell or do nothing
		"""
		pass