from abc import ABCMeta
from abc import abstractmethod

class Strategies(metaclass = ABCMeta):
	@abstractmethod
	def trade_decision(self, spot_price: float, futures_price: float, *args, **kwargs):
		"""
		Returns a decision on which asset to buy / sell or do nothing
		"""
		pass

	@abstractmethod
	def bid_ask_trade_decision(self, 	spot_bid_price: float,
										spot_ask_price: float,
										futures_bid_price: float,
										futures_ask_price: float,
										threshold: float,
										*args,
										**kwargs):
		pass