import deprecation
import logging
from enum import Enum
from strategies.Strategies import Strategies

class TradePosition(Enum):
	# Current position that the bot has taken up
	NO_POSITION_TAKEN 		= 1
	LONG_SPOT_SHORT_FUTURE 	= 2
	LONG_FUTURE_SHORT_SPOT 	= 3

class ExecutionDecision(Enum):
	# What should the bot do given the information
	NO_DECISION 						= 1
	GO_LONG_SPOT_SHORT_FUTURE 			= 2
	GO_LONG_FUTURE_SHORT_SPOT 			= 3
	TAKE_PROFIT_LONG_SPOT_SHORT_FUTURE 	= 4
	TAKE_PROFIT_LONG_FUTURE_SHORT_SPOT 	= 5

class SingleTradeArbitrag(Strategies):
	spot_symbol 		= None
	futures_symbol 		= None
	api_client 			= None
	current_spot_vol	= 0
	current_futures_lot = 0
	logger 				= logging.getLogger('SingleTradeArbitrag')

	def __init__(self,	spot_symbol: str,
						futures_symbol: str,
						api_client,
				):
		"""
		Class only maintains 1 position at a time. 

		api_client 			- Exchange api client
		"""
		super(SingleTradeArbitrag, self).__init__()
		self.spot_symbol 		= spot_symbol
		self.futures_symbol 	= futures_symbol
		self.api_client 		= api_client
		self.init_asset_holdings()
		return

	def init_asset_holdings(self):
		"""
		Determines how much of the assets have we gone long / short on.

		Spots are measured using the vol and futures are measured by the lot size.

		TODO: 
		- Implement API calls to check for positions taken on spot & futures assets on Kucoin
		"""
		self.logger.info(f"Spot vol: {self.current_spot_vol}, Futures lot size: {self.current_futures_lot}")
		pass

	def change_asset_holdings(self, delta_spot, delta_futures):
		self.current_spot_vol 		+= delta_spot
		self.current_futures_lot 	+= delta_futures
		self.logger.info(f"Spot vol: {self.current_spot_vol}, Futures lot size: {self.current_futures_lot}")
		return

	def current_position(self):
		_current_position = TradePosition.NO_POSITION_TAKEN
		if self.current_spot_vol > 0 and self.current_futures_lot < 0:
			_current_position = TradePosition.LONG_SPOT_SHORT_FUTURE
		elif self.current_spot_vol < 0 and self.current_futures_lot > 0:
			_current_position = TradePosition.LONG_FUTURE_SHORT_SPOT
		return _current_position

	def trade_decision(self, 	spot_price: float, 
								futures_price: float, 
								entry_threshold: float,
								take_profit_threshold: float,
								*args,
								**kwargs):
		"""
		Returns a decision on which asset to buy / sell or do nothing
		"""
		decision 			= ExecutionDecision.NO_DECISION
		current_position 	= self.current_position()

		if 	(current_position is TradePosition.LONG_SPOT_SHORT_FUTURE) \
			and (spot_price / futures_price - 1 >= take_profit_threshold):
			decision = ExecutionDecision.TAKE_PROFIT_LONG_SPOT_SHORT_FUTURE

		elif (current_position is TradePosition.LONG_FUTURE_SHORT_SPOT) \
			 and (futures_price / spot_price - 1 >= take_profit_threshold):
			decision = ExecutionDecision.TAKE_PROFIT_LONG_FUTURE_SHORT_SPOT

		elif (spot_price > futures_price) \
			 and (spot_price / futures_price - 1 >= entry_threshold) \
			 and (current_position is not TradePosition.LONG_FUTURE_SHORT_SPOT):
			decision = ExecutionDecision.GO_LONG_FUTURE_SHORT_SPOT

		elif (futures_price > spot_price) \
			 and (futures_price / spot_price - 1 >= entry_threshold) \
			 and (current_position is not TradePosition.LONG_SPOT_SHORT_FUTURE):
			decision = ExecutionDecision.GO_LONG_SPOT_SHORT_FUTURE
		return decision

	def bid_ask_trade_decision(self, 	spot_bid_price: float,
										spot_ask_price: float,
										futures_bid_price: float,
										futures_ask_price: float,
										entry_threshold: float,
										take_profit_threshold: float,
										*args,
										**kwargs
							):
		"""
		Returns a decision on which asset to buy / sell or do nothing
		"""
		decision 			= ExecutionDecision.NO_DECISION
		current_position 	= self.current_position()

		profit_from_long_spot_short_futures = futures_bid_price - spot_ask_price
		profit_from_short_spot_long_futures = spot_bid_price - futures_ask_price
		self.logger.info(f"""Current position: {current_position}. Profits long_spot_short_futures: {profit_from_long_spot_short_futures}, short_spot_long_futures: {profit_from_short_spot_long_futures}""")

		if 	(current_position is TradePosition.LONG_SPOT_SHORT_FUTURE) \
			and (spot_bid_price / futures_ask_price - 1 >= take_profit_threshold):
			decision = ExecutionDecision.TAKE_PROFIT_LONG_SPOT_SHORT_FUTURE

		elif (current_position is TradePosition.LONG_FUTURE_SHORT_SPOT) \
			 and (futures_bid_price / spot_ask_price - 1 >= take_profit_threshold):
			decision = ExecutionDecision.TAKE_PROFIT_LONG_FUTURE_SHORT_SPOT

		elif (profit_from_long_spot_short_futures > profit_from_short_spot_long_futures) \
			 and (futures_bid_price / spot_ask_price - 1 >= entry_threshold) \
			 and (current_position is not TradePosition.LONG_SPOT_SHORT_FUTURE):
			decision = ExecutionDecision.GO_LONG_SPOT_SHORT_FUTURE

		elif (profit_from_short_spot_long_futures > profit_from_long_spot_short_futures) \
			 and (spot_bid_price / futures_ask_price - 1 >= entry_threshold) \
			 and (current_position is not TradePosition.LONG_FUTURE_SHORT_SPOT):
			decision = ExecutionDecision.GO_LONG_FUTURE_SHORT_SPOT

		return decision