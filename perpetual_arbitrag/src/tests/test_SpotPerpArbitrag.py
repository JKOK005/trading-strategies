import copy
from strategies.SpotPerpArbitrag import SpotPerpArbitrag, SpotPerpExecutionDecision, SpotPerpTradePosition
from strategies.SingleTradeArbitragV2 import ExecutionDecision, TradePosition
from unittest import TestCase
from unittest.mock import patch

class TestSpotPerpArbitrag(TestCase):
	def setUp(self):
		self.strategy 	= 	SpotPerpArbitrag(spot_symbol 			= "BTC-USDT",
											 current_spot_vol		= 0,
											 max_spot_vol 			= 10,
											 perp_symbol			= "XBTUSDTM",
											 current_perp_lot_size 	= 0,
											 max_perp_lot_size 		= 10,
										)

	def test_get_current_position_no_position(self):
		with patch.object(SpotPerpArbitrag, "_current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.NO_POSITION_TAKEN
			assert(self.strategy.current_position() == SpotPerpTradePosition.NO_POSITION_TAKEN)

	def test_get_current_position_long_spot_short_perp(self):
		with patch.object(SpotPerpArbitrag, "_current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_A_SHORT_B
			assert(self.strategy.current_position() == SpotPerpTradePosition.LONG_SPOT_SHORT_PERP)

	def test_get_current_position_long_perp_short_spot(self):
		with patch.object(SpotPerpArbitrag, "_current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_B_SHORT_A
			assert(self.strategy.current_position() == SpotPerpTradePosition.LONG_PERP_SHORT_SPOT)

	def test_get_asset_holdings(self):
		assert(self.strategy.get_asset_holdings() == (0, 0))

	def test_change_asset_holdings(self):
		_strategy = copy.deepcopy(self.strategy)
		_strategy.change_asset_holdings(delta_spot = 2, delta_perp = -1)
		assert(_strategy.get_asset_holdings() == (2, -1))

	def test_trade_no_decision(self):
		with patch.object(SpotPerpArbitrag, "_trade_decision") as mock_trade_decision:
			mock_trade_decision.return_value = ExecutionDecision.NO_DECISION
			assert(self.strategy.trade_decision(spot_bid_price = 0,
												spot_ask_price = 0,
												perp_bid_price = 0,
												perp_ask_price = 0,
												perp_funding_rate = 0,
												perp_estimated_funding_rate = 0,
												entry_threshold = 0,
												take_profit_threshold = 0) == SpotPerpExecutionDecision.NO_DECISION)

	def test_trade_go_long_spot_short_perp(self):
		with patch.object(SpotPerpArbitrag, "_trade_decision") as mock_trade_decision:
			mock_trade_decision.return_value = ExecutionDecision.GO_LONG_A_SHORT_B
			assert(self.strategy.trade_decision(spot_bid_price = 0,
												spot_ask_price = 0,
												perp_bid_price = 0,
												perp_ask_price = 0,
												perp_funding_rate = 0,
												perp_estimated_funding_rate = 0,
												entry_threshold = 0,
												take_profit_threshold = 0) == SpotPerpExecutionDecision.GO_LONG_SPOT_SHORT_PERP)

	def test_trade_go_long_perp_short_spot(self):
		with patch.object(SpotPerpArbitrag, "_trade_decision") as mock_trade_decision:
			mock_trade_decision.return_value = ExecutionDecision.GO_LONG_B_SHORT_A
			assert(self.strategy.trade_decision(spot_bid_price = 0,
												spot_ask_price = 0,
												perp_bid_price = 0,
												perp_ask_price = 0,
												perp_funding_rate = 0,
												perp_estimated_funding_rate = 0,
												entry_threshold = 0,
												take_profit_threshold = 0) == SpotPerpExecutionDecision.GO_LONG_PERP_SHORT_SPOT)

	def test_trade_take_profit_long_spot_short_perp(self):
		with patch.object(SpotPerpArbitrag, "_trade_decision") as mock_trade_decision:
			mock_trade_decision.return_value = ExecutionDecision.TAKE_PROFIT_LONG_A_SHORT_B
			assert(self.strategy.trade_decision(spot_bid_price = 0,
												spot_ask_price = 0,
												perp_bid_price = 0,
												perp_ask_price = 0,
												perp_funding_rate = 0,
												perp_estimated_funding_rate = 0,
												entry_threshold = 0,
												take_profit_threshold = 0) == SpotPerpExecutionDecision.TAKE_PROFIT_LONG_SPOT_SHORT_PERP)

	def test_trade_take_profit_long_perp_short_spot(self):
		with patch.object(SpotPerpArbitrag, "_trade_decision") as mock_trade_decision:
			mock_trade_decision.return_value = ExecutionDecision.TAKE_PROFIT_LONG_B_SHORT_A
			assert(self.strategy.trade_decision(spot_bid_price = 0,
												spot_ask_price = 0,
												perp_bid_price = 0,
												perp_ask_price = 0,
												perp_funding_rate = 0,
												perp_estimated_funding_rate = 0,
												entry_threshold = 0,
												take_profit_threshold = 0) == SpotPerpExecutionDecision.TAKE_PROFIT_LONG_PERP_SHORT_SPOT)