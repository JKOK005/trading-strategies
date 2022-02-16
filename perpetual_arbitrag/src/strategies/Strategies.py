from abc import ABCMeta
from abc import abstractmethod
import hashlib

class Strategies(metaclass = ABCMeta):
	def get_strategy_id(self):
		hash_obj 	= hashlib.sha256(str(self.__class__.__name__).encode('utf-8'))
		hex_dig 	= hash_obj.hexdigest()
		return hex_dig[:10]

	@abstractmethod
	def trade_decision(self, 	spot_price: float, 
								futures_price: float,
								futures_latest_funding_rate: float,
								futures_estimated_funding_rate: float,
								*args, 
								**kwargs):
		"""
		Returns a decision on which asset to buy / sell or do nothing
		"""
		pass

	@abstractmethod
	def bid_ask_trade_decision(self, 	spot_bid_price: float,
										spot_ask_price: float,
										futures_bid_price: float,
										futures_ask_price: float,
										futures_latest_funding_rate: float,
										futures_estimated_funding_rate: float,
										threshold: float,
										*args,
										**kwargs):
		pass