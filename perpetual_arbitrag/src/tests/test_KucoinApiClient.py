import copy
import sys
from clients.KucoinApiClient import KucoinApiClient
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
													sandbox = True
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
	def test_no_open_spot_orders(self, patch_trade):
		_kucoin_api_client 					= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.futures_trade 	= patch_trade

		patch_trade.get_order_list.return_value = 	{
													 	"totalPage" : 1,
													 	"items" 	: []
													}
		assert(len(_kucoin_api_client.get_futures_open_orders(symbol = "XBTUSDTM")) == 0)

	def test_most_recent_spot_orders_with_correct_symbol_retrieved(self):
		_kucoin_api_client 					= copy.deepcopy(self.kucoin_api_client)

		with patch.object(_kucoin_api_client, "get_spot_open_orders") as mock_get_spot_open_orders:
			mock_get_spot_open_orders.return_value 	=	[{"symbol" : "ETH", "createdAt" : 1},
														 {"symbol" : "ETH", "createdAt" : 2},
														 {"symbol" : "ETH", "createdAt" : 4}]

			assert(_kucoin_api_client.get_spot_most_recent_open_order(symbol = "ETH")["createdAt"] == 4)

	def test_most_recent_futures_orders_with_correct_symbol_retrieved(self):
		_kucoin_api_client 					= copy.deepcopy(self.kucoin_api_client)

		with patch.object(_kucoin_api_client, "get_spot_open_orders") as mock_get_spot_open_orders:
			mock_get_spot_open_orders.return_value 	=	[ 	{"symbol" : "XBTUSDTM", "createdAt" : 1},
															{"symbol" : "XBTUSDTM", "createdAt" : 3}
														]

			assert(_kucoin_api_client.get_spot_most_recent_open_order(symbol = "XBTUSDTM")["createdAt"] == 3)
	