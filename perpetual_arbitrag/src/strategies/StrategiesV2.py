from abc import ABCMeta
from abc import abstractmethod

class StrategiesV2(metaclass = ABCMeta):
	@abstractmethod
	def change_asset_holdings(self, *args, **kwargs):
		pass

	@abstractmethod
	def get_asset_holdings(self, *args, **kwargs):
		pass

	@abstractmethod
	def current_position(self, *args, **kwargs):
		pass

	@abstractmethod
	def trade_decision(self, *args, **kwargs):
		"""
		Returns a decision on which asset to buy / sell or do nothing
		"""
		pass