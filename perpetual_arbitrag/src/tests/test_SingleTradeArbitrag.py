import copy
from strategies.SingleTradeArbitrag import SingleTradeArbitrag, ExecutionDecision, TradePosition
from unittest import TestCase
from unittest.mock import patch

class TestSingleTradeArbitrag(TestCase):
	
	@patch("clients.KucoinApiClient")
	def setUp(self, api_client):
		self.strategy 	= SingleTradeArbitrag(	spot_symbol 			= "BTC-USDT",
												max_spot_vol 			= 10,
												futures_symbol			= "XBTUSDTM",
												max_futures_lot_size 	= 10,
												api_client 				= api_client
											)

	def test_do_not_enter_when_threshold_not_met_on_limit_case_A(self):
		with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.NO_POSITION_TAKEN
			decision = self.strategy.trade_decision(spot_price = 100, futures_price = 150, entry_threshold = 0.6, take_profit_threshold = 0.1)
			assert(decision == ExecutionDecision.NO_DECISION)

	def test_do_not_enter_when_threshold_not_met_on_limit_case_B(self):
		with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.NO_POSITION_TAKEN
			decision = self.strategy.trade_decision(spot_price = 150, futures_price = 100, entry_threshold = 0.6, take_profit_threshold = 0.1)
			assert(decision == ExecutionDecision.NO_DECISION)

	def test_do_not_take_profit_when_take_profit_threshold_not_met_on_limit_case_A(self):
		with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_SPOT_SHORT_FUTURE
			decision = self.strategy.trade_decision(spot_price = 150, futures_price = 100, entry_threshold = 0.7, take_profit_threshold = 0.6)
			assert(decision == ExecutionDecision.NO_DECISION)

	def test_do_not_take_profit_when_take_profit_threshold_not_met_on_limit_case_B(self):
		with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_FUTURE_SHORT_SPOT
			decision = self.strategy.trade_decision(spot_price = 100, futures_price = 150, entry_threshold = 0.7, take_profit_threshold = 0.6)
			assert(decision == ExecutionDecision.NO_DECISION)

	def test_entry_long_spot_short_futures_on_limit(self):
		with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.NO_POSITION_TAKEN
			decision = self.strategy.trade_decision(spot_price = 100, futures_price = 150, entry_threshold = 0.3, take_profit_threshold = 0.5)
			assert(decision == ExecutionDecision.GO_LONG_SPOT_SHORT_FUTURE)

	def test_continued_long_spot_short_futures_on_limit(self):
		with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_SPOT_SHORT_FUTURE
			decision = self.strategy.trade_decision(spot_price = 100, futures_price = 150, entry_threshold = 0.3, take_profit_threshold = 0.5)
			assert(decision == ExecutionDecision.GO_LONG_SPOT_SHORT_FUTURE)

	def test_entry_long_futures_short_spot_on_limit(self):
		with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.NO_POSITION_TAKEN
			decision = self.strategy.trade_decision(spot_price = 150, futures_price = 100, entry_threshold = 0.3, take_profit_threshold = 0.5)
			assert(decision == ExecutionDecision.GO_LONG_FUTURE_SHORT_SPOT)

	def test_continued_long_futures_short_spot_on_limit(self):
		with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_FUTURE_SHORT_SPOT
			decision = self.strategy.trade_decision(spot_price = 150, futures_price = 100, entry_threshold = 0.3, take_profit_threshold = 0.5)
			assert(decision == ExecutionDecision.GO_LONG_FUTURE_SHORT_SPOT)

	def test_take_profit_long_spot_short_futures_on_limit(self):
		with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_SPOT_SHORT_FUTURE
			decision = self.strategy.trade_decision(spot_price = 150, futures_price = 100, entry_threshold = 0.3, take_profit_threshold = 0.3)
			assert(decision == ExecutionDecision.TAKE_PROFIT_LONG_SPOT_SHORT_FUTURE)

	def test_take_profit_long_futures_short_spot_on_limit(self):
		with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_FUTURE_SHORT_SPOT
			decision = self.strategy.trade_decision(spot_price = 100, futures_price = 150, entry_threshold = 0.3, take_profit_threshold = 0.3)
			assert(decision == ExecutionDecision.TAKE_PROFIT_LONG_FUTURE_SHORT_SPOT)

	def test_do_not_exceed_maximum_spot_holdings_on_long(self):
		_strategy 					= copy.deepcopy(self.strategy)
		_strategy.current_spot_vol 	= 11

		with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_SPOT_SHORT_FUTURE
			decision = _strategy.trade_decision(spot_price = 100, futures_price = 150, entry_threshold = 0.3, take_profit_threshold = 0.5)
			assert(decision == ExecutionDecision.NO_DECISION)

	def test_do_not_exceed_maximum_spot_holdings_on_short(self):
		_strategy 					= copy.deepcopy(self.strategy)
		_strategy.current_spot_vol 	= -11

		with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_FUTURE_SHORT_SPOT
			decision = _strategy.trade_decision(spot_price = 150, futures_price = 100, entry_threshold = 0.3, take_profit_threshold = 0.5)
			assert(decision == ExecutionDecision.NO_DECISION)

	def test_do_not_exceed_maximum_futures_holdings_on_long(self):
		_strategy 							= copy.deepcopy(self.strategy)
		_strategy.current_futures_lot_size 	= 11

		with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_FUTURE_SHORT_SPOT
			decision = _strategy.trade_decision(spot_price = 150, futures_price = 100, entry_threshold = 0.3, take_profit_threshold = 0.5)
			assert(decision == ExecutionDecision.NO_DECISION)

	def test_do_not_exceed_maximum_futures_holdings_on_short(self):
		_strategy 							= copy.deepcopy(self.strategy)
		_strategy.current_futures_lot_size 	= -11

		with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_SPOT_SHORT_FUTURE
			decision = _strategy.trade_decision(spot_price = 100, futures_price = 150, entry_threshold = 0.3, take_profit_threshold = 0.5)
			assert(decision == ExecutionDecision.NO_DECISION)

	def test_do_not_enter_when_threshold_not_met_on_market_case_A(self):
		pass

	def test_do_not_enter_when_threshold_not_met_on_market_case_B(self):
		pass

	def test_do_not_take_profit_when_take_profit_threshold_not_met_on_market_case_A(self):
		pass

	def test_do_not_take_profit_when_take_profit_threshold_not_met_on_market_case_B(self):
		pass

	def test_entry_long_spot_short_futures_on_market(self):
		pass

	def test_continued_long_spot_short_futures_on_market(self):
		pass

	def test_entry_long_futures_short_spot_on_market(self):
		pass

	def test_continued_long_futures_short_spot_on_market(self):
		pass

	def test_take_profit_long_spot_short_futures_on_market(self):
		pass

	def test_take_profit_long_futures_short_spot_on_market(self):
		pass

	def test_do_not_exceed_maximum_spot_holdings_on_long(self):
		pass

	def test_do_not_exceed_maximum_spot_holdings_on_short(self):
		pass

	def test_do_not_exceed_maximum_futures_holdings_on_long(self):
		pass

	def test_do_not_exceed_maximum_futures_holdings_on_short(self):
		pass