import deprecation
import hashlib
import logging
from enum import Enum
from strategies.StrategiesV2 import StrategiesV2

class TradePosition(Enum):
	# Current position that the bot has taken up
	NO_POSITION_TAKEN 	= 1
	LONG_A_SHORT_B 		= 2
	LONG_B_SHORT_A 		= 3

class ExecutionDecision(Enum):
	# What should the bot do given the information
	NO_DECISION 				= 1
	GO_LONG_A_SHORT_B 			= 2
	GO_LONG_B_SHORT_A 			= 3
	TAKE_PROFIT_LONG_A_SHORT_B 	= 4
	TAKE_PROFIT_LONG_B_SHORT_A 	= 5

class SingleTradeArbitragV2(StrategiesV2):
	logger 				= logging.getLogger('SingleTradeArbitragV2')
	A_symbol 			= None
	current_A_position	= 0
	max_A_position 		= 0
	B_symbol 			= None
	current_B_position 	= 0
	max_B_position 		= 0

	def __init__(self,	A_symbol: str,
						current_A_position: float,
						max_A_position: float,
						B_symbol: str,
						current_B_position: int,
						max_B_position: int,
				):
		"""
		Class only maintains 1 position at a time. 
		"""
		super(SingleTradeArbitragV2, self).__init__()
		self.A_symbol 				= A_symbol
		self.current_A_position 	= current_A_position
		self.max_A_position 		= max_A_position
		self.B_symbol 				= B_symbol
		self.current_B_position 	= current_B_position
		self.max_B_position 		= max_B_position
		self.logger.info(f"{self.A_symbol} position: {self.current_A_position}, {self.B_symbol} position: {self.current_B_position}")
		return

	@classmethod
	def get_strategy_id(cls):
		hash_obj 	= hashlib.sha256(str(cls.__name__).encode('utf-8'))
		hex_dig 	= hash_obj.hexdigest()
		return hex_dig[:10]

	def _change_asset_holdings(self, delta_A_position, delta_B_position):
		self.current_A_position += delta_A_position
		self.current_B_position += delta_B_position
		self.logger.info(f"{self.A_symbol} position: {self.current_A_position}, {self.B_symbol} position: {self.current_B_position}")
		return

	def _get_asset_holdings(self):
		return (self.current_A_position, self.current_B_position)

	def _current_position(self):
		_current_position = TradePosition.NO_POSITION_TAKEN
		if self.current_A_position > 0 and self.current_B_position < 0:
			_current_position = TradePosition.LONG_A_SHORT_B
		elif self.current_A_position < 0 and self.current_B_position > 0:
			_current_position = TradePosition.LONG_B_SHORT_A
		return _current_position

	def _trade_decision(self, asset_A_bid_price: float,
							  asset_A_effective_bid_price: float, 
							  asset_A_ask_price: float, 
							  asset_A_effective_ask_price: float,
							  asset_B_bid_price: float,
							  asset_B_effective_bid_price: float,
							  asset_B_ask_price: float,
							  asset_B_effective_ask_price: float,
							  entry_threshold: float,
							  take_profit_threshold: float,
							  *args,
							  **kwargs):
		"""
		Returns a decision on which asset to buy / sell or do nothing
		"""
		decision 			= ExecutionDecision.NO_DECISION
		current_position 	= self._current_position()

		profit_from_long_A_short_B 	= asset_B_effective_bid_price - asset_A_effective_ask_price
		profit_from_short_A_long_B 	= asset_A_effective_bid_price - asset_B_effective_ask_price

		if 	(current_position is TradePosition.LONG_A_SHORT_B) \
			and (profit_from_short_A_long_B >= take_profit_threshold * (asset_A_bid_price + asset_B_ask_price)):
			decision = ExecutionDecision.TAKE_PROFIT_LONG_A_SHORT_B

		elif (current_position is TradePosition.LONG_B_SHORT_A) \
			 and (profit_from_long_A_short_B >= take_profit_threshold * (asset_A_ask_price + asset_B_bid_price)):
			decision = ExecutionDecision.TAKE_PROFIT_LONG_B_SHORT_A

		else:
			if 	(abs(self.current_A_position) >= self.max_A_position) \
			 	or (abs(self.current_B_position) >= self.max_B_position):
			 	decision = ExecutionDecision.NO_DECISION

			elif (profit_from_long_A_short_B > profit_from_short_A_long_B) \
				 and (profit_from_long_A_short_B >= entry_threshold * (asset_A_ask_price + asset_B_bid_price)) \
				 and (current_position is not TradePosition.LONG_B_SHORT_A):
				decision = ExecutionDecision.GO_LONG_A_SHORT_B

			elif (profit_from_short_A_long_B > profit_from_long_A_short_B) \
				 and (profit_from_short_A_long_B >= entry_threshold * (asset_A_bid_price + asset_B_ask_price)) \
				 and (current_position is not TradePosition.LONG_A_SHORT_B):
				decision = ExecutionDecision.GO_LONG_B_SHORT_A

		return decision