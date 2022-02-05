import copy
import sys
import pytest
from clients.KucoinApiClient import KucoinApiClient
from freezegun import freeze_time
from unittest import TestCase
from unittest.mock import patch

class TestKucoinApiClient(TestCase):
	
	def setUp(self):
		self.kucoin_api_client 	= KucoinApiClient(	spot_client_api_key 			= "123", 
													spot_client_api_secret_key 		= "123", 
													spot_client_pass_phrase 		= "fake_spot_passphrase",
													futures_client_api_key 			= "456", 
													futures_client_api_secret_key 	= "456", 
													futures_client_pass_phrase 		= "fake_futures_passphrase",
													sandbox = True, 
													funding_rate_enable = True,
												)

	@patch("kucoin.client.User")
	def test_spot_trading_account_details_filters_correct_symbol(self, patch_user):
		_kucoin_api_client 				= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.spot_user 	= patch_user
		patch_user.get_account_list.return_value 	= [ {"type" : "trade", 	"currency" : "BTC"},
														{"type" : "trade", 	"currency" : "USDT"},
														{"type" : "trade", 	"currency" : "XRP"},
														{"type" : "trade", 	"currency" : "ETH"},
														{"type" : "main", 	"currency" : "ETH"}]

		account_details 	= _kucoin_api_client.get_spot_trading_account_details(currency = "ETH")
		assert(account_details["type"] == "trade" and account_details["currency"] == "ETH")

	def test_average_margin_purchase_price_computation_exact_order(self):
		price_qty_pairs_ordered = [[100, 100], [200, 100], [300, 50]]
		size 					= 250
		assert(self.kucoin_api_client._compute_average_margin_purchase_price(price_qty_pairs_ordered = price_qty_pairs_ordered, size = size) == 180)

	def test_average_margin_purchase_price_computation_partial_order(self):
		price_qty_pairs_ordered = [[150, 100], [300, 100], [500, 50]]
		size 					= 150
		assert(self.kucoin_api_client._compute_average_margin_purchase_price(price_qty_pairs_ordered = price_qty_pairs_ordered, size = size) == 200)

	def test_average_margin_purchase_price_computation_above_all_available_order(self):
		price_qty_pairs_ordered = [[100, 100], [200, 100], [300, 50]]
		size 					= 1000
		assert(self.kucoin_api_client._compute_average_margin_purchase_price(price_qty_pairs_ordered = price_qty_pairs_ordered, size = size) == 180)

	def test_average_margin_purchase_price_computation_single_order(self):
		price_qty_pairs_ordered = [[100, 100], [200, 100], [300, 50]]
		size 					= 1
		assert(self.kucoin_api_client._compute_average_margin_purchase_price(price_qty_pairs_ordered = price_qty_pairs_ordered, size = size) == 100)

	def test_bid_price_default_for_no_bids(self):
		bids 	= []
		size 	= 100
		assert(self.kucoin_api_client._compute_average_bid_price(bids = bids, size = size) == 0)

	def test_prioritization_of_single_highest_bids(self):
		bids 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 50
		assert(self.kucoin_api_client._compute_average_bid_price(bids = bids, size = size) == 500)

	def test_prioritization_of_two_most_highest_bids(self):
		bids 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 100
		assert(self.kucoin_api_client._compute_average_bid_price(bids = bids, size = size) == 400)

	def test_ask_price_default_for_no_asks(self):
		asks 	= []
		size 	= 100
		assert(self.kucoin_api_client._compute_average_ask_price(asks = asks, size = size) == sys.maxsize)

	def test_prioritization_of_single_lowest_asks(self):
		asks 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 50
		assert(self.kucoin_api_client._compute_average_ask_price(asks = asks, size = size) == 100)

	def test_prioritization_of_two_most_lowest_asks(self):
		asks 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 200
		assert(self.kucoin_api_client._compute_average_ask_price(asks = asks, size = size) == 125)

	@patch("kucoin.client.Trade")
	def test_open_spot_orders_with_correct_symbol_retrieved(self, patch_trade):
		_kucoin_api_client 				= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.spot_trade 	= patch_trade

		patch_trade.get_order_list.return_value = 	{
													 	"totalPage" : 1,
													 	"items" 	: [ {"symbol" : "ETH", "createdAt" : 1},
																		{"symbol" : "ETH", "createdAt" : 2},
																		{"symbol" : "BTC", "createdAt" : 3},
																		{"symbol" : "ETH", "createdAt" : 4},
																		{"symbol" : "XRP", "createdAt" : 5}]
													}
		assert(len(_kucoin_api_client.get_spot_open_orders(symbol = "ETH")) == 3)

	@patch("kucoin.client.Trade")
	def test_no_open_spot_orders(self, patch_trade):
		_kucoin_api_client 				= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.spot_trade 	= patch_trade

		patch_trade.get_order_list.return_value = 	{
													 	"totalPage" : 1,
													 	"items" 	: []
													}
		assert(len(_kucoin_api_client.get_spot_open_orders(symbol = "BTC")) == 0)

	@patch("kucoin_futures.client.Trade")
	def test_open_futures_orders_with_correct_symbol_retrieved(self, patch_trade):
		_kucoin_api_client 					= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.futures_trade 	= patch_trade

		patch_trade.get_order_list.return_value = 	{
													 	"totalPage" : 1,
													 	"items" 	: [ {"symbol" : "XBTUSDTM", "createdAt" : 1},
																		{"symbol" : "ETHUSDT", 	"createdAt" : 2},
																		{"symbol" : "XBTUSDTM", "createdAt" : 3},
																		{"symbol" : "ETHUSDT", 	"createdAt" : 4},
																		{"symbol" : "XRPUSDT", 	"createdAt" : 5}]
													}
		assert(len(_kucoin_api_client.get_futures_open_orders(symbol = "XBTUSDTM")) == 2)

	@patch("kucoin_futures.client.Trade")
	def test_no_open_futures_orders(self, patch_trade):
		_kucoin_api_client 					= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.futures_trade 	= patch_trade

		patch_trade.get_order_list.return_value = 	{
													 	"totalPage" : 1,
													 	"items" 	: []
													}
		assert(len(_kucoin_api_client.get_futures_open_orders(symbol = "XBTUSDTM")) == 0)

	def test_most_recent_open_spot_orders_with_correct_symbol_retrieved(self):
		_kucoin_api_client 					= copy.deepcopy(self.kucoin_api_client)

		with patch.object(_kucoin_api_client, "get_spot_open_orders") as mock_get_spot_open_orders:
			mock_get_spot_open_orders.return_value 	=	[{"symbol" : "ETH", "createdAt" : 1},
														 {"symbol" : "ETH", "createdAt" : 2},
														 {"symbol" : "ETH", "createdAt" : 4}]

			assert(_kucoin_api_client.get_spot_most_recent_open_order(symbol = "ETH")["createdAt"] == 4)

	def test_most_recent_open_futures_orders_with_correct_symbol_retrieved(self):
		_kucoin_api_client 					= copy.deepcopy(self.kucoin_api_client)

		with patch.object(_kucoin_api_client, "get_spot_open_orders") as mock_get_spot_open_orders:
			mock_get_spot_open_orders.return_value 	=	[ 	{"symbol" : "XBTUSDTM", "createdAt" : 1},
															{"symbol" : "XBTUSDTM", "createdAt" : 3}
														]

			assert(_kucoin_api_client.get_spot_most_recent_open_order(symbol = "XBTUSDTM")["createdAt"] == 3)
	
	@patch("kucoin.client.Trade")
	def test_fulfilled_spot_orders_with_correct_symbol_retrieved(self, patch_trade):
		_kucoin_api_client 				= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.spot_trade 	= patch_trade

		patch_trade.get_recent_orders.return_value = {
													 	"status" : 200,
													 	"data" 	: [ {"symbol" : "ETH", "createdAt" : 1},
																	{"symbol" : "ETH", "createdAt" : 2},
																	{"symbol" : "BTC", "createdAt" : 3},
																	{"symbol" : "ETH", "createdAt" : 4},
																	{"symbol" : "XRP", "createdAt" : 5}]
													}
		assert(len(_kucoin_api_client.get_spot_fulfilled_orders(symbol = "ETH")) == 3)

	@patch("kucoin.client.Trade")
	def test_no_open_spot_orders(self, patch_trade):
		_kucoin_api_client 				= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.spot_trade 	= patch_trade

		patch_trade.get_recent_orders.return_value = {
													 	"status" : 200,
													 	"data" 	: []
													}
		assert(len(_kucoin_api_client.get_spot_fulfilled_orders(symbol = "BTC")) == 0)

	@patch("kucoin_futures.client.Trade")
	def test_fulfilled_futures_orders_with_correct_symbol_retrieved(self, patch_trade):
		_kucoin_api_client 					= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.futures_trade 	= patch_trade

		patch_trade.get_recent_fills.return_value = {
													 	"status" : 200,
													 	"data" 	: [ {"symbol" : "XBTUSDTM", "createdAt" : 1},
																	{"symbol" : "ETHUSDT", 	"createdAt" : 2},
																	{"symbol" : "XBTUSDTM", "createdAt" : 3},
																	{"symbol" : "ETHUSDT", 	"createdAt" : 4},
																	{"symbol" : "XRPUSDT", 	"createdAt" : 5}]
													}
		assert(len(_kucoin_api_client.get_futures_fulfilled_orders(symbol = "XBTUSDTM")) == 2)

	@patch("kucoin_futures.client.Trade")
	def test_no_open_futures_orders(self, patch_trade):
		_kucoin_api_client 					= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.futures_trade 	= patch_trade

		patch_trade.get_recent_fills.return_value = {
													 	"status" : 200,
													 	"data" 	: []
													}
		assert(len(_kucoin_api_client.get_futures_fulfilled_orders(symbol = "XBTUSDTM")) == 0)

	def test_most_recent_fulfilled_spot_orders_with_correct_symbol_retrieved(self):
		_kucoin_api_client 					= copy.deepcopy(self.kucoin_api_client)

		with patch.object(_kucoin_api_client, "get_spot_fulfilled_orders") as mock_get_spot_fulfilled_orders:
			mock_get_spot_fulfilled_orders.return_value = [{"symbol" : "ETH", "createdAt" : 1},
														   {"symbol" : "ETH", "createdAt" : 2},
														   {"symbol" : "ETH", "createdAt" : 4}]

			assert(_kucoin_api_client.get_spot_most_recent_fulfilled_order(symbol = "ETH")["createdAt"] == 4)

	def test_most_recent_fulfilled_futures_orders_with_correct_symbol_retrieved(self):
		_kucoin_api_client 					= copy.deepcopy(self.kucoin_api_client)

		with patch.object(_kucoin_api_client, "get_futures_fulfilled_orders") as mock_get_futures_fulfilled_orders:
			mock_get_futures_fulfilled_orders.return_value 	= [ {"symbol" : "XBTUSDTM", "createdAt" : 1},
																{"symbol" : "XBTUSDTM", "createdAt" : 3}
															]

			assert(_kucoin_api_client.get_futures_most_recent_fulfilled_order(symbol = "XBTUSDTM")["createdAt"] == 3)

	@patch("kucoin_futures.client.Trade")
	def test_spot_order_call_invoked(self, patch_trade):
		_kucoin_api_client 								= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.spot_trade 					= patch_trade
		patch_trade.create_market_order.return_value 	= {"orderId" : "0001"}

		_kucoin_api_client.place_spot_order(symbol 		= "BTC-USDT", 
											order_type 	= "market", 
											order_side 	= "sell", 
											price 		= 1,
											size 		= 1
										)

		assert(patch_trade.create_market_order.called)

	@patch("kucoin_futures.client.Trade")
	def test_futures_order_call_invoked(self, patch_trade):
		_kucoin_api_client 								= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.futures_trade 				= patch_trade
		patch_trade.create_limit_order.return_value 	= {"orderId" : "0001"}

		_kucoin_api_client.place_futures_order(	symbol 		= "XBTUSDTM", 
												order_type 	= "market", 
												order_side 	= "buy", 
												price 		= 1,
												size 		= 1,
												lever		= 1
											)
		assert(patch_trade.create_limit_order.called)

	@patch("kucoin_futures.client.Trade")
	def test_spot_order_cancellation_without_error(self, patch_trade):
		_kucoin_api_client 						= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.spot_trade 			= patch_trade
		patch_trade.cancel_order.return_value 	= True

		_kucoin_api_client.cancel_spot_order(order_id = "0001")
		assert(patch_trade.cancel_order.called)

	@patch("kucoin_futures.client.Trade")
	def test_spot_order_cancellation_with_error_handelled_internally(self, patch_trade):
		# Main program should not crash
		_kucoin_api_client 						= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.spot_trade 			= patch_trade
		patch_trade.cancel_order.return_value 	= True
		patch_trade.cancel_order.side_effect 	= Exception("Test throw error")

		try:
			_kucoin_api_client.cancel_spot_order(order_id = "0001")
		except Exception as ex:
			assert(False)
		return

	@patch("kucoin_futures.client.Trade")
	def test_futures_order_cancellation_without_error(self, patch_trade):
		_kucoin_api_client 						= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.futures_trade 		= patch_trade
		patch_trade.cancel_order.return_value 	= True

		_kucoin_api_client.cancel_futures_order(order_id = "0001")
		assert(patch_trade.cancel_order.called)

	@patch("kucoin_futures.client.Trade")
	def test_futures_order_cancellation_with_error_handelled_internally(self, patch_trade):
		# Main program should not crash
		_kucoin_api_client 						= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.futures_trade 		= patch_trade
		patch_trade.cancel_order.return_value 	= True
		patch_trade.cancel_order.side_effect 	= Exception("Test throw error")

		try:
			_kucoin_api_client.cancel_futures_order(order_id = "0001")
		except Exception as ex:
			assert(False)
		return

	@patch("kucoin.client.Market")
	def test_spot_min_volume_throws_error_on_invalid_symbol(self, patch_client):
		_kucoin_api_client 				= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.spot_client 	= patch_client

		patch_client.get_symbol_list.return_value = [	
														{"symbol" : "BTC-USDT", "baseMinSize" : 1}, 
														{"symbol" : "ETH-USDT", "baseMinSize" : 10},
														{"symbol" : "XRP-USDT", "baseMinSize" : 5}
													]
		with pytest.raises(Exception):
			min_vol = _kucoin_api_client.get_spot_min_volume(symbol = "ADA-USDT")
		return

	@patch("kucoin_futures.client.Market")
	def test_futures_min_lot_size_throws_error_on_invalid_symbol(self, patch_client):
		_kucoin_api_client 						= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.futures_client 		= patch_client

		patch_client.get_contract_detail.side_effect 	= Exception({"code":"404000","msg":"Symbol not exists"})

		with pytest.raises(Exception):
			min_vol = _kucoin_api_client.get_futures_min_lot_size(symbol = "BTCUSDTM")
		return

	@patch("kucoin_futures.client.Market")
	def test_get_futures_funding_rates(self, patch_client):
		_kucoin_api_client 						= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.futures_client 		= patch_client

		patch_client.get_current_fund_rate.return_value = {"value" : 0.01, "predictedValue" : -0.01}
		(funding_rate, estimated_funding_rate) = _kucoin_api_client.get_futures_funding_rate(symbol = "ETHUSDT")
		assert (funding_rate == 0.01 and estimated_funding_rate == -0.01)
		return

	@freeze_time("2022-01-01 03:55:00")
	def test_funding_rate_is_valid_interval(self):
		_kucoin_api_client 	= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.kucoin_funding_rate_snapshot_times = ["04:00"]
		assert(_kucoin_api_client.funding_rate_valid_interval(seconds_before = 300))
		return

	@freeze_time("2022-01-01 03:50:00")
	def test_funding_rate_is_not_valid_interval_A(self):
		_kucoin_api_client 	= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.kucoin_funding_rate_snapshot_times = ["04:00"]
		assert(not _kucoin_api_client.funding_rate_valid_interval(seconds_before = 300))
		return

	@freeze_time("2022-01-01 04:00:01")
	def test_funding_rate_is_not_valid_interval_B(self):
		_kucoin_api_client 	= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.kucoin_funding_rate_snapshot_times = ["04:00"]
		assert(not _kucoin_api_client.funding_rate_valid_interval(seconds_before = 300))
		return

	def test_effective_funding_rate_is_zero_when_flag_is_disabled(self):
		_kucoin_api_client 	= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.funding_rate_enable = False

		with patch.object(_kucoin_api_client, "funding_rate_valid_interval") as mock_funding_rate_valid_interval:
			mock_funding_rate_valid_interval.return_value = True
			assert _kucoin_api_client.get_futures_effective_funding_rate(symbol = "ETHUSDT", seconds_before = 300) == (0, 0)
		return

	def test_effective_funding_rate_is_zero_when_invalid_interval(self):
		_kucoin_api_client 	= copy.deepcopy(self.kucoin_api_client)

		with patch.object(_kucoin_api_client, "funding_rate_valid_interval") as mock_funding_rate_valid_interval, \
			 patch.object(_kucoin_api_client, "get_futures_funding_rate") as mock_get_futures_funding_rate:
			mock_funding_rate_valid_interval.return_value 	= False
			mock_get_futures_funding_rate.return_value 		= (0.01, -0.01)
			assert _kucoin_api_client.get_futures_effective_funding_rate(symbol = "ETHUSDT", seconds_before = 300) == (0.01, 0)
		return

	@patch("kucoin_futures.client.Market")
	def test_effective_funding_rate_is_non_zero(self, patch_client):
		_kucoin_api_client 						= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.futures_client 		= patch_client

		patch_client.get_current_fund_rate.return_value = {"value" : 0.01, "predictedValue" : -0.01}

		with patch.object(_kucoin_api_client, "funding_rate_valid_interval") as mock_funding_rate_valid_interval:
			mock_funding_rate_valid_interval.return_value = True
			assert _kucoin_api_client.get_futures_effective_funding_rate(symbol = "ETHUSDT", seconds_before = 300) == (0.01, -0.01)
		return