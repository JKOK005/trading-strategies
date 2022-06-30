import hashlib
import logging
from enum import Enum
from strategies.Strategies import Strategies

class SpotPerpTradePosition(Enum):
	NO_POSITION_TAKEN 		= 1
	LONG_SPOT_SHORT_PERP 	= 2
	LONG_PERP_SHORT_SPOT 	= 3

class SpotPerpExecutionDecision(Enum):
	NO_DECISION 						= 1
	GO_LONG_SPOT_SHORT_PERP 			= 2
	GO_LONG_PERP_SHORT_SPOT 			= 3
	TAKE_PROFIT_LONG_SPOT_SHORT_PERP 	= 4
	TAKE_PROFIT_LONG_PERP_SHORT_SPOT 	= 5

mapping = {
	TradePosition.NO_POSITION_TAKEN 				: SPOTPerpTradePosition.NO_POSITION_TAKEN,
	TradePosition.LONG_A_SHORT_B 					: SPOTPerpTradePosition.LONG_SPOT_SHORT_PERP,
	TradePosition.LONG_B_SHORT_A 					: SPOTPerpTradePosition.LONG_PERP_SHORT_SPOT,
	ExecutionDecision.NO_DECISION 					: SPOTPerpExecutionDecision.NO_DECISION,
	ExecutionDecision.GO_LONG_A_SHORT_B 			: SPOTPerpExecutionDecision.GO_LONG_SPOT_SHORT_PERP,
	ExecutionDecision.GO_LONG_B_SHORT_A 			: SPOTPerpExecutionDecision.GO_LONG_PERP_SHORT_SPOT,
	ExecutionDecision.TAKE_PROFIT_LONG_A_SHORT_B 	: SPOTPerpExecutionDecision.TAKE_PROFIT_LONG_SPOT_SHORT_PERP,
	ExecutionDecision.TAKE_PROFIT_LONG_B_SHORT_A 	: SPOTPerpExecutionDecision.TAKE_PROFIT_LONG_PERP_SHORT_SPOT,
}

class SpotPerpArbitrag(StrategiesV2):
	logger 						= logging.getLogger('SpotPerpArbitrag')
	spot_symbol 				= None
	current_spot_vol			= 0
	max_spot_vol 				= 0
	futures_symbol 				= None
	current_futures_lot_size 	= 0
	max_futures_lot_size 		= 0

	def __init__(self,	spot_symbol: str,
						current_spot_vol: float,
						max_spot_vol: float,
						perp_symbol: str,
						current_perp_lot_size: int,
						max_perp_lot_size: int,
				):
		"""
		Class only maintains 1 position at a time. 
		"""
		super(SpotPerpArbitrag, self).__init__(	A_symbol = spot_symbol,
												current_A_position = current_spot_vol,
												max_A_position = max_spot_vol,
												B_symbol = perp_symbol,
												current_B_position = current_perp_lot_size,
												max_B_position = max_perp_lot_size)
		return

	def change_asset_holdings(self, delta_spot: float, delta_perp: float):
		return self._change_asset_holdings(delta_A_position = delta_spot, delta_B_position = delta_perp)

	def get_asset_holdings(self):
		return self._get_asset_holdings()

	def current_position(self):
		position = self._current_position()
		return mapping[position]

	def trade_decision(self, spot_bid_price: float,
							 spot_ask_price: float,
							 perp_bid_price: float,
							 perp_ask_price: float,
							 perp_funding_rate: float,
							 perp_estimated_funding_rate: float,
							 entry_threshold: float,
							 take_profit_threshold: float,
					):
	
		effective_perp_bid_price 	= perp_bid_price * (1 + perp_funding_rate + perp_estimated_funding_rate)
		effective_perp_ask_price 	= perp_ask_price * (1 + perp_funding_rate + perp_estimated_funding_rate)

		decision 	= self._trade_decision(	asset_A_bid_price = spot_bid_price,
										  	asset_A_effective_bid_price = spot_bid_price, 
										  	asset_A_ask_price = spot_ask_price, 
										  	asset_A_effective_ask_price = spot_ask_price,
										  	asset_B_bid_price = perp_bid_price,
										  	asset_B_effective_bid_price = effective_perp_bid_price,
										  	asset_B_ask_price = perp_ask_price,
										  	asset_B_effective_ask_price = effective_perp_ask_price,
										  	entry_threshold = entry_threshold,
										  	take_profit_threshold = take_profit_threshold,
									  	)

		return mapping[decision]