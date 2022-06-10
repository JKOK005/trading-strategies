import hashlib
import logging
from enum import Enum
from strategies.SingleTradeArbitragV2 import SingleTradeArbitragV2, TradePosition, ExecutionDecision

class MarginPerpTradePosition(Enum):
	NO_POSITION_TAKEN 		= 1
	LONG_MARGIN_SHORT_PERP 	= 2
	LONG_PERP_SHORT_MARGIN 	= 3

class MarginPerpExecutionDecision(Enum):
	NO_DECISION 						= 1
	GO_LONG_MARGIN_SHORT_PERP 			= 2
	GO_LONG_PERP_SHORT_MARGIN 			= 3
	TAKE_PROFIT_LONG_MARGIN_SHORT_PERP 	= 4
	TAKE_PROFIT_LONG_PERP_SHORT_MARGIN 	= 5

mapping = {
	TradePosition.NO_POSITION_TAKEN 				: MarginPerpTradePosition.NO_POSITION_TAKEN,
	TradePosition.LONG_A_SHORT_B 					: MarginPerpTradePosition.LONG_MARGIN_SHORT_PERP,
	TradePosition.LONG_B_SHORT_A 					: MarginPerpTradePosition.LONG_PERP_SHORT_MARGIN,
	ExecutionDecision.NO_DECISION 					: MarginPerpExecutionDecision.NO_DECISION,
	ExecutionDecision.GO_LONG_A_SHORT_B 			: MarginPerpExecutionDecision.GO_LONG_MARGIN_SHORT_PERP,
	ExecutionDecision.GO_LONG_B_SHORT_A 			: MarginPerpExecutionDecision.GO_LONG_PERP_SHORT_MARGIN,
	ExecutionDecision.TAKE_PROFIT_LONG_A_SHORT_B 	: MarginPerpExecutionDecision.TAKE_PROFIT_LONG_MARGIN_SHORT_PERP,
	ExecutionDecision.TAKE_PROFIT_LONG_B_SHORT_A 	: MarginPerpExecutionDecision.TAKE_PROFIT_LONG_PERP_SHORT_MARGIN,
}

class MarginPerpArbitrag(SingleTradeArbitragV2):
	def __init__(self, 	margin_symbol: str,
						current_margin_position: float,
						max_margin_position: float,
						perp_symbol: str,
						current_perp_position: int,
						max_perp_position: int,
				):
		super(MarginPerpArbitrag, self).__init__(A_symbol = margin_symbol,
												 current_A_position = current_margin_position,
												 max_A_position = max_margin_position,
												 B_symbol = perp_symbol,
												 current_B_position = current_perp_position,
												 max_B_position = max_perp_position)

	def change_asset_holdings(self, delta_margin: float, delta_perp: float):
		return self._change_asset_holdings(delta_A_position = delta_margin, delta_B_position = delta_perp)

	def get_asset_holdings(self):
		return self._get_asset_holdings()

	def current_position(self):
		position = self._current_position()
		return mapping[position]

	def trade_decision(self, margin_bid_price: float,
							 margin_ask_price: float,
							 margin_interest_rate: float,
							 perp_bid_price: float,
							 perp_ask_price: float,
							 perp_funding_rate: float,
							 perp_estimated_funding_rate: float,
							 entry_threshold: float,
							 take_profit_threshold: float,
					):
		
		effective_margin_bid_price 	= (1 - margin_interest_rate) * margin_bid_price
		effective_margin_ask_price 	= (1 + margin_interest_rate) * margin_ask_price
		effective_perp_bid_price 	= perp_bid_price * (1 + perp_funding_rate + perp_estimated_funding_rate)
		effective_perp_ask_price 	= perp_ask_price * (1 + perp_funding_rate + perp_estimated_funding_rate)

		decision 	= self._trade_decision(	asset_A_bid_price = margin_bid_price,
										  	asset_A_effective_bid_price = effective_margin_bid_price, 
										  	asset_A_ask_price = margin_ask_price, 
										  	asset_A_effective_ask_price = effective_margin_ask_price,
										  	asset_B_bid_price = perp_bid_price,
										  	asset_B_effective_bid_price = effective_perp_bid_price,
										  	asset_B_ask_price = perp_ask_price,
										  	asset_B_effective_ask_price = effective_perp_ask_price,
										  	entry_threshold = entry_threshold,
										  	take_profit_threshold = take_profit_threshold,
									  	)
		return mapping[decision]