import copy
from strategies.SingleTradeArbitragV2 import SingleTradeArbitragV2, ExecutionDecision, TradePosition
from unittest import TestCase
from unittest.mock import patch

class SingleTradeArbitragV2Mock(SingleTradeArbitragV2):
	def __init__(self, *args, **kwargs):
		super(SingleTradeArbitragV2Mock, self).__init__(*args, **kwargs)
		return

	def change_asset_holdings(self, *args, **kwargs):
		pass

	def get_asset_holdings(self, *args, **kwargs):
		pass

	def current_position(self, *args, **kwargs):
		pass

	def trade_decision(self, *args, **kwargs):
		pass

class TestSingleTradeArbitrag(TestCase):
	def setUp(self):
		self.strategy 	= SingleTradeArbitragV2Mock(A_symbol 			= "BTC-USDT",
													current_A_position	= 0,
													max_A_position 		= 10,
													B_symbol			= "XBTUSDTM",
													current_B_position 	= 0,
													max_B_position 		= 10,
												)

	def test_do_not_enter_when_threshold_not_met_on_market_case_A(self):
		# Do not enter on long spot short future
		with patch.object(SingleTradeArbitragV2Mock, "_current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.NO_POSITION_TAKEN
			decision 	= self.strategy._trade_decision(asset_A_bid_price 			= 200,
														asset_A_effective_bid_price = 200,
														asset_A_ask_price 			= 100,
														asset_A_effective_ask_price = 100,
														asset_B_bid_price 			= 150,
														asset_B_effective_bid_price = 150,
														asset_B_ask_price 			= 200,
														asset_B_effective_ask_price = 200,
														entry_threshold 			= 1,
														take_profit_threshold 		= 1,
													)
			assert(decision == ExecutionDecision.NO_DECISION)

	def test_do_not_enter_when_threshold_not_met_on_market_case_B(self):
		# Do not enter on long future short spot
		with patch.object(SingleTradeArbitragV2Mock, "_current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.NO_POSITION_TAKEN
			decision 	= self.strategy._trade_decision(asset_A_bid_price 			= 150,
														asset_A_effective_bid_price = 150,
														asset_A_ask_price 			= 200,
														asset_A_effective_ask_price = 200,
														asset_B_bid_price 			= 200,
														asset_B_effective_bid_price = 200,
														asset_B_ask_price 			= 100,
														asset_B_effective_ask_price = 100,
														entry_threshold 			= 1,
														take_profit_threshold 		= 1,
													)
			assert(decision == ExecutionDecision.NO_DECISION)

	def test_do_not_take_profit_when_take_profit_threshold_not_met_on_market_case_A(self):
		# Do not take profit on long spot short future
		with patch.object(SingleTradeArbitragV2Mock, "_current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_A_SHORT_B
			decision 	= self.strategy._trade_decision(asset_A_bid_price 			= 150,
														asset_A_effective_bid_price = 150,
														asset_A_ask_price 			= 200,
														asset_A_effective_ask_price = 200,
														asset_B_bid_price 			= 200,
														asset_B_effective_bid_price = 200,
														asset_B_ask_price 			= 100,
														asset_B_effective_ask_price = 100,
														entry_threshold 			= 1,
														take_profit_threshold 		= 1,
													)
			assert(decision == ExecutionDecision.NO_DECISION)

	def test_do_not_take_profit_when_take_profit_threshold_not_met_on_market_case_B(self):
		# Do not take profit on long future short spot
		with patch.object(SingleTradeArbitragV2, "_current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_B_SHORT_A
			decision 	= self.strategy._trade_decision(asset_A_bid_price 			= 200,
														asset_A_effective_bid_price = 200,
														asset_A_ask_price 			= 100,
														asset_A_effective_ask_price = 100,
														asset_B_bid_price 			= 150,
														asset_B_effective_bid_price = 150,
														asset_B_ask_price 			= 200,
														asset_B_effective_ask_price = 200,
														entry_threshold 			= 1,
														take_profit_threshold 		= 1,
													)
			assert(decision == ExecutionDecision.NO_DECISION)

	def test_entry_long_A_short_B_on_market(self):
		with patch.object(SingleTradeArbitragV2, "_current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.NO_POSITION_TAKEN
			decision 	= self.strategy._trade_decision(asset_A_bid_price 			= 200,
														asset_A_effective_bid_price = 200,
														asset_A_ask_price 			= 100,
														asset_A_effective_ask_price = 100,
														asset_B_bid_price 			= 150,
														asset_B_effective_bid_price = 150,
														asset_B_ask_price 			= 200,
														asset_B_effective_ask_price = 200,
														entry_threshold 			= 0.1,
														take_profit_threshold 		= 1,
													)
			assert(decision == ExecutionDecision.GO_LONG_A_SHORT_B)

	def test_continued_long_A_short_B_on_market(self):
		with patch.object(SingleTradeArbitragV2, "_current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_A_SHORT_B
			decision 	= self.strategy._trade_decision(asset_A_bid_price 			= 200,
														asset_A_effective_bid_price = 200,
														asset_A_ask_price 			= 100,
														asset_A_effective_ask_price = 100,
														asset_B_bid_price 			= 150,
														asset_B_effective_bid_price = 150,
														asset_B_ask_price 			= 200,
														asset_B_effective_ask_price = 200,
														entry_threshold 			= 0.1,
														take_profit_threshold 		= 1,
													)
			assert(decision == ExecutionDecision.GO_LONG_A_SHORT_B)

	def test_entry_long_B_short_A_on_market(self):
		with patch.object(SingleTradeArbitragV2, "_current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.NO_POSITION_TAKEN
			decision 	= self.strategy._trade_decision(asset_A_bid_price 			= 150,
														asset_A_effective_bid_price = 150,
														asset_A_ask_price 			= 200,
														asset_A_effective_ask_price = 200,
														asset_B_bid_price 			= 200,
														asset_B_effective_bid_price = 200,
														asset_B_ask_price 			= 100,
														asset_B_effective_ask_price = 100,
														entry_threshold 			= 0.1,
														take_profit_threshold 		= 1,
													)
			assert(decision == ExecutionDecision.GO_LONG_B_SHORT_A)

	def test_continued_long_B_short_A_on_market(self):
		with patch.object(SingleTradeArbitragV2, "_current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_B_SHORT_A
			decision 	= self.strategy._trade_decision(asset_A_bid_price 			= 150,
														asset_A_effective_bid_price = 150,
														asset_A_ask_price 			= 200,
														asset_A_effective_ask_price = 200,
														asset_B_bid_price 			= 200,
														asset_B_effective_bid_price = 200,
														asset_B_ask_price 			= 100,
														asset_B_effective_ask_price = 100,
														entry_threshold 			= 0.1,
														take_profit_threshold 		= 1,
													)
			assert(decision == ExecutionDecision.GO_LONG_B_SHORT_A)

	def test_take_profit_long_A_short_B_on_market(self):
		with patch.object(SingleTradeArbitragV2, "_current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_A_SHORT_B
			decision 	= self.strategy._trade_decision(asset_A_bid_price 			= 150,
														asset_A_effective_bid_price = 150,
														asset_A_ask_price 			= 200,
														asset_A_effective_ask_price = 200,
														asset_B_bid_price 			= 200,
														asset_B_effective_bid_price = 200,
														asset_B_ask_price 			= 100,
														asset_B_effective_ask_price = 100,
														entry_threshold 			= 1,
														take_profit_threshold 		= 0.1,
													)
			assert(decision == ExecutionDecision.TAKE_PROFIT_LONG_A_SHORT_B)

	def test_take_profit_long_B_short_A_on_market(self):
		with patch.object(SingleTradeArbitragV2, "_current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_B_SHORT_A
			decision 	= self.strategy._trade_decision(asset_A_bid_price 			= 200,
														asset_A_effective_bid_price = 200,
														asset_A_ask_price 			= 100,
														asset_A_effective_ask_price = 100,
														asset_B_bid_price 			= 150,
														asset_B_effective_bid_price = 150,
														asset_B_ask_price 			= 200,
														asset_B_effective_ask_price = 200,
														entry_threshold 			= 1,
														take_profit_threshold 		= 0.1,
													)
			assert(decision == ExecutionDecision.TAKE_PROFIT_LONG_B_SHORT_A)

	def test_do_not_exceed_maximum_A_position_on_long(self):
		_strategy 						= copy.deepcopy(self.strategy)
		_strategy.current_A_position 	= 11
		with patch.object(SingleTradeArbitragV2, "_current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_A_SHORT_B
			decision 	= _strategy._trade_decision(asset_A_bid_price 			= 200,
													asset_A_effective_bid_price = 200,
													asset_A_ask_price 			= 100,
													asset_A_effective_ask_price = 100,
													asset_B_bid_price 			= 150,
													asset_B_effective_bid_price = 150,
													asset_B_ask_price 			= 200,
													asset_B_effective_ask_price = 200,
													entry_threshold 			= 0.1,
													take_profit_threshold 		= 1,
												)
			assert(decision == ExecutionDecision.NO_DECISION)

	def test_do_not_exceed_maximum_A_position_on_short(self):
		_strategy 					 	= copy.deepcopy(self.strategy)
		_strategy.current_A_position 	= -11
		with patch.object(SingleTradeArbitragV2, "_current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_B_SHORT_A
			decision 	= _strategy._trade_decision(asset_A_bid_price 			= 150,
													asset_A_effective_bid_price = 150,
													asset_A_ask_price 			= 200,
													asset_A_effective_ask_price = 200,
													asset_B_bid_price 			= 200,
													asset_B_effective_bid_price = 200,
													asset_B_ask_price 			= 100,
													asset_B_effective_ask_price = 100,
													entry_threshold 			= 0.1,
													take_profit_threshold 		= 1,
												)
			assert(decision == ExecutionDecision.NO_DECISION)

	def test_do_not_exceed_maximum_B_position_on_long(self):
		_strategy 						= copy.deepcopy(self.strategy)
		_strategy.current_B_position 	= 11
		with patch.object(SingleTradeArbitragV2, "_current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_B_SHORT_A
			decision 	= _strategy._trade_decision(asset_A_bid_price 			= 150,
													asset_A_effective_bid_price = 150,
													asset_A_ask_price 			= 200,
													asset_A_effective_ask_price = 200,
													asset_B_bid_price 			= 200,
													asset_B_effective_bid_price = 200,
													asset_B_ask_price 			= 100,
													asset_B_effective_ask_price = 100,
													entry_threshold 			= 0.3,
													take_profit_threshold 		= 0.1,
												)
			assert(decision == ExecutionDecision.NO_DECISION)

	def test_do_not_exceed_maximum_B_position_on_short(self):
		_strategy 						= copy.deepcopy(self.strategy)
		_strategy.current_B_position 	= -11
		with patch.object(SingleTradeArbitragV2, "_current_position") as mock_current_position:
			mock_current_position.return_value = TradePosition.LONG_A_SHORT_B
			decision 	= _strategy._trade_decision(asset_A_bid_price 			= 200,
													asset_A_effective_bid_price = 200,
													asset_A_ask_price 			= 100,
													asset_A_effective_ask_price = 100,
													asset_B_bid_price 			= 150,
													asset_B_effective_bid_price = 150,
													asset_B_ask_price 			= 200,
													asset_B_effective_ask_price = 200,
													entry_threshold 			= 0.1,
													take_profit_threshold 		= 1,
												)
			assert(decision == ExecutionDecision.NO_DECISION)