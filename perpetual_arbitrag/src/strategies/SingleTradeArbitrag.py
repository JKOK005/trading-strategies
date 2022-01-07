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
	logger 						= logging.getLogger('SingleTradeArbitrag')
	api_client 					= None
	spot_symbol 				= None
	current_spot_vol			= 0
	max_spot_vol 				= 0
	futures_symbol 				= None
	current_futures_lot_size 	= 0
	max_futures_lot_size 		= 0

	def __init__(self,	spot_symbol: str,
						current_spot_vol: float,
						max_spot_vol: float,
						futures_symbol: str,
						current_futures_lot_size: int,
						max_futures_lot_size: int,
						api_client,
				):
		"""
		Class only maintains 1 position at a time. 

		api_client 			- Exchange api client
		"""
		super(SingleTradeArbitrag, self).__init__()
		self.spot_symbol 				= spot_symbol
		self.current_spot_vol 			= current_spot_vol
		self.max_spot_vol 				= max_spot_vol
		self.futures_symbol 			= futures_symbol
		self.current_futures_lot_size 	= current_futures_lot_size
		self.max_futures_lot_size 		= max_futures_lot_size
		self.api_client 				= api_client
		
		self.logger.info(f"Spot vol: {self.current_spot_vol}, Futures lot size: {self.current_futures_lot_size}")
		return

	def change_asset_holdings(self, delta_spot, delta_futures):
		self.current_spot_vol 			+= delta_spot
		self.current_futures_lot_size 	+= delta_futures
		self.logger.info(f"Spot vol: {self.current_spot_vol}, Futures lot size: {self.current_futures_lot_size}")
		return

	def get_asset_holdings(self):
		return (self.current_spot_vol, self.current_futures_lot_size)

	def current_position(self):
		_current_position = TradePosition.NO_POSITION_TAKEN
		if self.current_spot_vol > 0 and self.current_futures_lot_size < 0:
			_current_position = TradePosition.LONG_SPOT_SHORT_FUTURE
		elif self.current_spot_vol < 0 and self.current_futures_lot_size > 0:
			_current_position = TradePosition.LONG_FUTURE_SHORT_SPOT
		return _current_position

	def trade_decision(self, 	spot_price: float, 
								futures_price: float,
								futures_funding_rate: float,
								futures_estimated_funding_rate: float,
								entry_threshold: float,
								take_profit_threshold: float,
								*args,
								**kwargs):
		"""
		Returns a decision on which asset to buy / sell or do nothing
		"""
		decision 			= ExecutionDecision.NO_DECISION
		current_position 	= self.current_position()

		effective_futures_bid_price 	= futures_price * (1 + futures_funding_rate + futures_estimated_funding_rate)
		effective_futures_ask_price 	= futures_price * (1 - futures_funding_rate - futures_estimated_funding_rate)

		if 	(current_position is TradePosition.LONG_SPOT_SHORT_FUTURE) \
			and (spot_price / effective_futures_ask_price - 1 >= take_profit_threshold):
			decision = ExecutionDecision.TAKE_PROFIT_LONG_SPOT_SHORT_FUTURE

		elif (current_position is TradePosition.LONG_FUTURE_SHORT_SPOT) \
			 and (effective_futures_bid_price / spot_price - 1 >= take_profit_threshold):
			decision = ExecutionDecision.TAKE_PROFIT_LONG_FUTURE_SHORT_SPOT

		else:
			if 	(abs(self.current_spot_vol) >= self.max_spot_vol) \
			 	or (abs(self.current_futures_lot_size) >= self.max_futures_lot_size):
			 	decision = ExecutionDecision.NO_DECISION

			elif (spot_price > effective_futures_ask_price) \
				 and (spot_price / effective_futures_ask_price - 1 >= entry_threshold):
				decision = ExecutionDecision.GO_LONG_FUTURE_SHORT_SPOT

			elif (effective_futures_bid_price > spot_price) \
				 and (effective_futures_bid_price / spot_price - 1 >= entry_threshold):
				decision = ExecutionDecision.GO_LONG_SPOT_SHORT_FUTURE

		return decision

	def bid_ask_trade_decision(self, 	spot_bid_price: float,
										spot_ask_price: float,
										futures_bid_price: float,
										futures_ask_price: float,
										futures_funding_rate: float,
										futures_estimated_funding_rate: float, 
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

		effective_futures_bid_price 	= futures_ask_price * (1 + futures_funding_rate + futures_estimated_funding_rate)
		effective_futures_ask_price 	= futures_bid_price * (1 - futures_funding_rate - futures_estimated_funding_rate)

		profit_from_long_spot_short_futures = effective_futures_bid_price - spot_ask_price
		profit_from_short_spot_long_futures = spot_bid_price - effective_futures_ask_price
		self.logger.info(f"""Current position: {current_position}. Profits long_spot_short_futures: {profit_from_long_spot_short_futures}, short_spot_long_futures: {profit_from_short_spot_long_futures}""")

		if 	(current_position is TradePosition.LONG_SPOT_SHORT_FUTURE) \
			and (spot_bid_price / effective_futures_ask_price - 1 >= take_profit_threshold):
			decision = ExecutionDecision.TAKE_PROFIT_LONG_SPOT_SHORT_FUTURE

		elif (current_position is TradePosition.LONG_FUTURE_SHORT_SPOT) \
			 and (effective_futures_bid_price / spot_ask_price - 1 >= take_profit_threshold):
			decision = ExecutionDecision.TAKE_PROFIT_LONG_FUTURE_SHORT_SPOT

		else:
			if 	(abs(self.current_spot_vol) >= self.max_spot_vol) \
			 	or (abs(self.current_futures_lot_size) >= self.max_futures_lot_size):
			 	decision = ExecutionDecision.NO_DECISION

			elif (profit_from_long_spot_short_futures > profit_from_short_spot_long_futures) \
				 and (effective_futures_bid_price / spot_ask_price - 1 >= entry_threshold):
				decision = ExecutionDecision.GO_LONG_SPOT_SHORT_FUTURE

			elif (profit_from_short_spot_long_futures > profit_from_long_spot_short_futures) \
				 and (spot_bid_price / effective_futures_ask_price - 1 >= entry_threshold):
				decision = ExecutionDecision.GO_LONG_FUTURE_SHORT_SPOT

		return decision