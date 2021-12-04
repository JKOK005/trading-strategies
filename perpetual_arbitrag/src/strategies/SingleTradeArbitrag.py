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
	NO_DECISION 				= 1
	GO_LONG_SPOT_SHORT_FUTURE 	= 2
	GO_LONG_FUTURE_SHORT_SPOT 	= 3

class SingleTradeArbitrag(Strategies):
	spot_symbol 		= None
	futures_symbol 		= None
	entry_percent_gap	= None
	api_client 			= None
	logger 				= logging.getLogger('SingleTradeArbitrag')
	current_position 	= TradePosition.NO_POSITION_TAKEN

	def __init__(self,	spot_symbol: str,
						futures_symbol: str,
						entry_percent_gap: float,
						api_client,
				):
		"""
		Class only maintains 1 position at a time. 

		entry_percent_gap 	- Gap between assets at which we can consider entry
		api_client 			- Exchange api client
		"""
		super(SingleTradeArbitrag, self).__init__()
		self.spot_symbol 		= spot_symbol
		self.futures_symbol 	= futures_symbol
		self.entry_percent_gap 	= entry_percent_gap
		self.api_client 		= api_client
		# self.current_position 	= self.check_position_taken()
		return

	def check_open_order_position_taken(self):
		"""
		Estalishes position taken for all open orders
		"""
		most_recent_open_spot_order 	= self.api_client.get_spot_most_recent_open_order(symbol = self.spot_symbol)
		most_recent_open_futures_order 	= self.api_client.get_futures_most_recent_open_order(symbol = self.futures_symbol)
		position 						= TradePosition.NO_POSITION_TAKEN

		if most_recent_open_spot_order is not None and most_recent_open_futures_order is not None:
			if most_recent_open_spot_order["side"] == "buy" and most_recent_open_futures_order["side"] == "sell":
				position = TradePosition.LONG_SPOT_SHORT_FUTURE
			elif most_recent_open_spot_order["side"] == "sell" and most_recent_open_futures_order["side"] == "buy":
				position = TradePosition.LONG_FUTURE_SHORT_SPOT				

		self.logger.debug(f"Current open order position is {position}")
		return position

	def check_fulfilled_order_position_taken(self):
		"""
		Establishes position taken for recently fulfilled orders
		"""
		most_recent_fulfilled_spot_order 	= self.api_client.get_spot_most_recent_fulfilled_order(symbol = self.spot_symbol)
		most_recent_fulfilled_futures_order = self.api_client.get_futures_most_recent_fulfilled_order(symbol = self.futures_symbol)
		position 							= TradePosition.NO_POSITION_TAKEN

		if most_recent_fulfilled_spot_order is not None and most_recent_fulfilled_futures_order is not None:
			if most_recent_fulfilled_spot_order["side"] == "buy" and most_recent_fulfilled_futures_order["side"] == "sell":
				position = TradePosition.LONG_SPOT_SHORT_FUTURE
			elif most_recent_fulfilled_spot_order["side"] == "sell" and most_recent_fulfilled_futures_order["side"] == "buy":
				position = TradePosition.LONG_FUTURE_SHORT_SPOT

		self.logger.debug(f"Current fulfilled order position is {position}")
		return position

	def check_position_taken(self):
		"""
		Determines the current position that we are taking up for the spot / future asset pair

		1) 	We will check if there are any open orders in place.
			- Only the latest spot / futures orders are considered
			- If we have open positions, then we maintain the state of that position
			- If we are unable to determine the position taken, then we clear all active orders of that position

		2) 	If no active orders, we will check the order entries for spot & futures position within the last 24 hours.
			Of these, we will retrieve the latest entries for spot & future positions and determine the following:
			- If we sold spot and buy future, our position is LONG_FUTURE_SHORT_SPOT
			- If we sold future and buy spot, our position is LONG_SPOT_SHORT_FUTURE
		"""
		
		# Part 1
		open_order_position 	= self.check_open_order_position_taken()
		current_position 		= open_order_position
		
		if current_position == TradePosition.NO_POSITION_TAKEN:
			# Part 2
			current_position 	= self.check_fulfilled_order_position_taken()

		self.logger.info(f"Current position is {current_position}")
		return current_position

	@deprecation.deprecated(deprecated_in = "1.0",
                        	details = "Use Bid / Ask pricing instead")
	def trade_decision(self, 	spot_price: float, 
								futures_price: float, 
								threshold: float,
								*args,
								**kwargs):
		"""
		Returns a decision on which asset to buy / sell or do nothing
		"""
		decision = ExecutionDecision.NO_DECISION
		if (spot_price > futures_price) and (spot_price / futures_price > threshold) and (self.current_position is not TradePosition.LONG_FUTURE_SHORT_SPOT):
			decision = ExecutionDecision.GO_LONG_FUTURE_SHORT_SPOT
		elif (futures_price > spot_price) and (futures_price / spot_price > threshold) and (self.current_position is not TradePosition.LONG_SPOT_SHORT_FUTURE):
			decision = ExecutionDecision.GO_LONG_SPOT_SHORT_FUTURE
		return decision

	def bid_ask_trade_decision(self, 	spot_bid_price: float,
										spot_ask_price: float,
										futures_bid_price: float,
										futures_ask_price: float,
										threshold: float,
										*args,
										**kwargs
							):
		"""
		Returns a decision on which asset to buy / sell or do nothing
		"""
		decision = ExecutionDecision.NO_DECISION

		profit_from_long_spot_short_futures = futures_bid_price - spot_ask_price
		profit_from_short_spot_long_futures = spot_bid_price - futures_ask_price

		if 		(profit_from_long_spot_short_futures > profit_from_short_spot_long_futures) \
				and (futures_bid_price / spot_ask_price - 1 > threshold) \
				and (self.current_position is not TradePosition.LONG_SPOT_SHORT_FUTURE):
				decision = ExecutionDecision.GO_LONG_SPOT_SHORT_FUTURE

		elif 	(profit_from_short_spot_long_futures > profit_from_long_spot_short_futures) \
				and (spot_bid_price / futures_ask_price -1 > threshold) \
				and (self.current_position is not TradePosition.LONG_FUTURE_SHORT_SPOT):
				decision = ExecutionDecision.GO_LONG_FUTURE_SHORT_SPOT

		return decision