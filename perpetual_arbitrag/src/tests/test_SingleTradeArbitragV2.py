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

	# def test_entry_long_futures_short_spot_on_market(self):
	# 	with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
	# 		mock_current_position.return_value = TradePosition.NO_POSITION_TAKEN
	# 		decision 	= self.strategy.bid_ask_trade_decision(	spot_bid_price 			= 150,
	# 															spot_ask_price 			= 200,
	# 															futures_bid_price 		= 200,
	# 															futures_ask_price 		= 100,
	# 															futures_funding_rate 	= 0, 
	# 															futures_estimated_funding_rate = 0,
	# 															entry_threshold 		= 0.1,
	# 															take_profit_threshold 	= 1,
	# 														)
	# 		assert(decision == ExecutionDecision.GO_LONG_FUTURE_SHORT_SPOT)

	# def test_continued_long_futures_short_spot_on_market(self):
	# 	with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
	# 		mock_current_position.return_value = TradePosition.LONG_FUTURE_SHORT_SPOT
	# 		decision 	= self.strategy.bid_ask_trade_decision(	spot_bid_price 			= 150,
	# 															spot_ask_price 			= 200,
	# 															futures_bid_price 		= 200,
	# 															futures_ask_price 		= 100,
	# 															futures_funding_rate 	= 0, 
	# 															futures_estimated_funding_rate = 0,
	# 															entry_threshold 		= 0.1,
	# 															take_profit_threshold 	= 1,
	# 														)
	# 		assert(decision == ExecutionDecision.GO_LONG_FUTURE_SHORT_SPOT)

	# def test_take_profit_long_spot_short_futures_on_market(self):
	# 	with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
	# 		mock_current_position.return_value = TradePosition.LONG_SPOT_SHORT_FUTURE
	# 		decision 	= self.strategy.bid_ask_trade_decision(	spot_bid_price 			= 150,
	# 															spot_ask_price 			= 200,
	# 															futures_bid_price 		= 200,
	# 															futures_ask_price 		= 100,
	# 															futures_funding_rate 	= 0, 
	# 															futures_estimated_funding_rate = 0,
	# 															entry_threshold 		= 1,
	# 															take_profit_threshold 	= 0.1,
	# 														)
	# 		assert(decision == ExecutionDecision.TAKE_PROFIT_LONG_SPOT_SHORT_FUTURE)

	# def test_take_profit_long_futures_short_spot_on_market(self):
	# 	with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
	# 		mock_current_position.return_value = TradePosition.LONG_FUTURE_SHORT_SPOT
	# 		decision 	= self.strategy.bid_ask_trade_decision(	spot_bid_price 			= 200,
	# 															spot_ask_price 			= 100,
	# 															futures_bid_price 		= 150,
	# 															futures_ask_price 		= 200,
	# 															futures_funding_rate 	= 0, 
	# 															futures_estimated_funding_rate = 0,
	# 															entry_threshold 		= 1,
	# 															take_profit_threshold 	= 0.1,
	# 														)
	# 		assert(decision == ExecutionDecision.TAKE_PROFIT_LONG_FUTURE_SHORT_SPOT)

	# def test_do_not_exceed_maximum_spot_holdings_on_long(self):
	# 	_strategy 					= copy.deepcopy(self.strategy)
	# 	_strategy.current_spot_vol 	= 11

	# 	with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
	# 		mock_current_position.return_value = TradePosition.LONG_SPOT_SHORT_FUTURE
	# 		decision 	= _strategy.bid_ask_trade_decision(	spot_bid_price 			= 200,
	# 														spot_ask_price 			= 100,
	# 														futures_bid_price 		= 150,
	# 														futures_ask_price 		= 200,
	# 														futures_funding_rate 	= 0, 
	# 														futures_estimated_funding_rate = 0,
	# 														entry_threshold 		= 0.1,
	# 														take_profit_threshold 	= 1,
	# 													)
	# 		assert(decision == ExecutionDecision.NO_DECISION)

	# def test_do_not_exceed_maximum_spot_holdings_on_short(self):
	# 	_strategy 					= copy.deepcopy(self.strategy)
	# 	_strategy.current_spot_vol 	= -11

	# 	with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
	# 		mock_current_position.return_value = TradePosition.LONG_FUTURE_SHORT_SPOT
	# 		decision 	= _strategy.bid_ask_trade_decision(	spot_bid_price 			= 150,
	# 														spot_ask_price 			= 200,
	# 														futures_bid_price 		= 200,
	# 														futures_ask_price 		= 100,
	# 														futures_funding_rate 	= 0, 
	# 														futures_estimated_funding_rate = 0,
	# 														entry_threshold 		= 0.1,
	# 														take_profit_threshold 	= 1,
	# 													)
	# 		assert(decision == ExecutionDecision.NO_DECISION)

	# def test_do_not_exceed_maximum_futures_holdings_on_long(self):
	# 	_strategy 							= copy.deepcopy(self.strategy)
	# 	_strategy.current_futures_lot_size 	= 11

	# 	with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
	# 		mock_current_position.return_value = TradePosition.LONG_FUTURE_SHORT_SPOT
	# 		decision 	= _strategy.bid_ask_trade_decision(	spot_bid_price 			= 150,
	# 														spot_ask_price 			= 200,
	# 														futures_bid_price 		= 200,
	# 														futures_ask_price 		= 100,
	# 														futures_funding_rate 	= 0, 
	# 														futures_estimated_funding_rate = 0,
	# 														entry_threshold 		= 0.3,
	# 														take_profit_threshold 	= 0.1,
	# 													)
	# 		assert(decision == ExecutionDecision.NO_DECISION)

	# def test_do_not_exceed_maximum_futures_holdings_on_short(self):
	# 	_strategy 					= copy.deepcopy(self.strategy)
	# 	_strategy.current_spot_vol 	= -11

	# 	with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
	# 		mock_current_position.return_value = TradePosition.LONG_SPOT_SHORT_FUTURE
	# 		decision 	= _strategy.bid_ask_trade_decision(	spot_bid_price 			= 200,
	# 														spot_ask_price 			= 100,
	# 														futures_bid_price 		= 150,
	# 														futures_ask_price 		= 200,
	# 														futures_funding_rate 	= 0, 
	# 														futures_estimated_funding_rate = 0,
	# 														entry_threshold 		= 0.1,
	# 														take_profit_threshold 	= 1,
	# 													)
	# 		assert(decision == ExecutionDecision.NO_DECISION)

	# def test_funding_rate_permit_entry_long_futures_short_spot_on_limit(self):
	# 	with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
	# 		mock_current_position.return_value = TradePosition.NO_POSITION_TAKEN
	# 		decision = self.strategy.trade_decision(spot_price = 100, futures_price = 110, 
	# 												futures_funding_rate = -0.8, futures_estimated_funding_rate = 0,
	# 												entry_threshold = 0.2, take_profit_threshold = 1)
	# 		assert(decision == ExecutionDecision.GO_LONG_FUTURE_SHORT_SPOT)

	# def test_funding_rate_deny_entry_long_futures_short_spot_on_limit(self):
	# 	with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
	# 		mock_current_position.return_value = TradePosition.NO_POSITION_TAKEN
	# 		decision = self.strategy.trade_decision(spot_price = 150, futures_price = 100, 
	# 												futures_funding_rate = 0.8, futures_estimated_funding_rate = 0,
	# 												entry_threshold = 0.2, take_profit_threshold = 1)
	# 		assert(decision != ExecutionDecision.GO_LONG_FUTURE_SHORT_SPOT)

	# def test_funding_rate_permit_entry_long_spot_short_futures_on_limit(self):
	# 	with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
	# 		mock_current_position.return_value = TradePosition.NO_POSITION_TAKEN
	# 		decision = self.strategy.trade_decision(spot_price = 110, futures_price = 100,
	# 												futures_funding_rate = 0.8, futures_estimated_funding_rate = 0,
	# 												entry_threshold = 0.2, take_profit_threshold = 1)
	# 		assert(decision == ExecutionDecision.GO_LONG_SPOT_SHORT_FUTURE)

	# def test_funding_rate_deny_entry_long_spot_short_futures_on_limit(self):
	# 	with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
	# 		mock_current_position.return_value = TradePosition.NO_POSITION_TAKEN
	# 		decision = self.strategy.trade_decision(spot_price = 100, futures_price = 150,
	# 												futures_funding_rate = -0.8, futures_estimated_funding_rate = 0,
	# 												entry_threshold = 0.2, take_profit_threshold = 1)
	# 		assert(decision != ExecutionDecision.GO_LONG_SPOT_SHORT_FUTURE)

	# def test_funding_rate_deny_entry_long_spot_short_futures_on_market(self):
	# 	with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
	# 		mock_current_position.return_value = TradePosition.NO_POSITION_TAKEN
	# 		decision 	= self.strategy.bid_ask_trade_decision(	spot_bid_price 			= 10,
	# 															spot_ask_price 			= 100,
	# 															futures_bid_price 		= 150,
	# 															futures_ask_price 		= 200,
	# 															futures_funding_rate 	= -0.8,
	# 															futures_estimated_funding_rate = 0,
	# 															entry_threshold 		= 0.2,
	# 															take_profit_threshold 	= 1,
	# 														)
	# 		assert(decision != ExecutionDecision.GO_LONG_SPOT_SHORT_FUTURE)

	# def test_funding_rate_permit_entry_long_spot_short_futures_on_market(self):
	# 	with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
	# 		mock_current_position.return_value = TradePosition.NO_POSITION_TAKEN
	# 		decision 	= self.strategy.bid_ask_trade_decision(	spot_bid_price 			= 10,
	# 															spot_ask_price 			= 100,
	# 															futures_bid_price 		= 100,
	# 															futures_ask_price 		= 200,
	# 															futures_funding_rate 	= 0.8, 
	# 															futures_estimated_funding_rate = 0,
	# 															entry_threshold 		= 0.2,
	# 															take_profit_threshold 	= 0,
	# 														)
	# 		assert(decision == ExecutionDecision.GO_LONG_SPOT_SHORT_FUTURE)

	# def test_funding_rate_deny_entry_short_spot_long_futures_on_market(self):
	# 	with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
	# 		mock_current_position.return_value = TradePosition.NO_POSITION_TAKEN
	# 		decision 	= self.strategy.bid_ask_trade_decision(	spot_bid_price 			= 150,
	# 															spot_ask_price 			= 200,
	# 															futures_bid_price 		= 10,
	# 															futures_ask_price 		= 100,
	# 															futures_funding_rate 	= 0.8,
	# 															futures_estimated_funding_rate = 0,
	# 															entry_threshold 		= 0.2,
	# 															take_profit_threshold 	= 1,
	# 														)
	# 		assert(decision != ExecutionDecision.GO_LONG_FUTURE_SHORT_SPOT)

	# def test_funding_rate_permit_entry_short_spot_long_futures_on_market(self):
	# 	with patch.object(SingleTradeArbitrag, "current_position") as mock_current_position:
	# 		mock_current_position.return_value = TradePosition.NO_POSITION_TAKEN
	# 		decision 	= self.strategy.bid_ask_trade_decision(	spot_bid_price 			= 100,
	# 															spot_ask_price 			= 200,
	# 															futures_bid_price 		= 10,
	# 															futures_ask_price 		= 100,
	# 															futures_funding_rate 	= -0.8,
	# 															futures_estimated_funding_rate = 0,
	# 															entry_threshold 		= 0.2,
	# 															take_profit_threshold 	= 1,
	# 														)
	# 		assert(decision == ExecutionDecision.GO_LONG_FUTURE_SHORT_SPOT)