from enum import Enum
from strategies.Strategies import Strategies

class TradePosition(Enum):
	NO_POSITION_TAKEN 		= 1
	LONG_SPOT_SHORT_FUTURE 	= 2
	LONG_FUTURE_SHORT_SPOT 	= 3

class SingleTradeArbitrag(Strategies):
	spot_symbol 		= None
	futures_symbol 		= None
	lot_size_entry 		= None
	entry_percent_gap	= None
	api_client 			= None
	current_position 	= TradePosition.NO_POSITION_TAKEN

	def __init__(self,	spot_symbol: str,
						futures_symbol: str,
						lot_size_entry: int,
						entry_percent_gap: float,
						api_client,
				):
		"""
		Class only maintains 1 position at a time. 

		lot_size_entry 		- How much of the asset to enter. 
		entry_percent_gap 	- Gap between assets at which we can consider entry
		api_client 			- Exchange api client
		"""
		super(SingleTradeArbitrag, self).__init__()
		self.spot_symbol 		= spot_symbol
		self.futures_symbol 	= futures_symbol
		self.lot_size_entry 	= lot_size_entry
		self.entry_percent_gap 	= entry_percent_gap
		self.api_client 		= api_client
		self.check_position_taken()
		return

	def check_position_taken(self):
		"""
		Determines the current position that we are taking up for the spot / future asset pair

		1) 	We will check if there are any open orders in place.
			- Only the latest spot / futures orders are considered

		2) 	If no active orders, we will check the order entries for spot & futures position within the last 24 hours.
			Of these, we will retrieve the latest entries for spot & future positions and determine the following:
			- If we sold spot and buy future, our position is LONG_FUTURE_SHORT_SPOT
			- If we sold future and buy spot, our position is LONG_SPOT_SHORT_FUTURE
		"""
		
		# Part 1
		most_recent_open_spot_order 	= self.api_client.get_spot_most_recent_open_order(symbol = self.spot_symbol)
		most_recent_open_futures_order 	= self.api_client.get_futures_most_recent_open_order(symbol = self.futures_symbol)

		# TODO: Complete implementation of check position taken function


	def trade_decision(self, spot_price: float, futures_price: float):
		"""
		Returns a decision on which asset to buy / sell or do nothing
		"""
		pass