import copy
import sys
import pytest
from clients.OkxApiClient import OkxApiClient
from freezegun import freeze_time
from unittest import TestCase
from unittest.mock import patch

class TestOkxApiClient(TestCase):
	
	def setUp(self):
		self.okx_api_client = OkxApiClient(	api_key 		= "123", 
											api_secret_key 	= "123", 
											passphrase 		= "fake_spot_passphrase",
											funding_rate_enable = True,
										)

	@patch("okx.Account_api.AccountAPI")
	def test_spot_account_api_call(self, patch_account):
		_okx_api_client 				= copy.deepcopy(self.okx_api_client)
		_okx_api_client.account_client 	= patch_account
		_okx_api_client.get_spot_trading_account_details(currency = "ETH")
		assert(patch_account.get_account.called)

	@patch("okx.Account_api.AccountAPI")
	def test_compute_correct_perpetual_amt(self, patch_account):
		_okx_api_client 				= copy.deepcopy(self.okx_api_client)
		_okx_api_client.account_client 	= patch_account
		patch_account.get_positions.return_value = {"code": "0",
													 "msg": "",
													 "data": [
													    {"availPos":"1", "ccy":"ETH-USDT-SWAP", "posSide":"long"},
													    {"availPos":"1", "ccy":"ETH-USDT-SWAP", "posSide":"short"},
													    {"availPos":"3", "ccy":"ETH-USDT-SWAP", "posSide":"short"},
													    {"availPos":"3", "ccy":"ETH-USDT-SWAP", "posSide":"long"},
													    {"availPos":"5", "ccy":"ETH-USDT-SWAP", "posSide":"long"},
													  ]
													}
		perpetual_position 	= _okx_api_client.get_perpetual_trading_account_details(currency = "ETH-USDT-SWAP")
		assert(perpetual_position == 5)

	@patch("okx.Market_api.MarketAPI")
	def test_spot_trading_price_api_call(self, patch_market):
		_okx_api_client 				= copy.deepcopy(self.okx_api_client)
		_okx_api_client.market_client 	= patch_market
		_okx_api_client.get_spot_trading_price(symbol = "ETH-USDT")
		assert(patch_market.get_ticker.called)

	@patch("okx.Market_api.MarketAPI")
	def test_perpetual_trading_price_api_call(self, patch_market):
		_okx_api_client 				= copy.deepcopy(self.okx_api_client)
		_okx_api_client.market_client 	= patch_market
		_okx_api_client.get_perpetual_trading_price(symbol = "ETH-USDT-SWAP")
		assert(patch_market.get_ticker.called)

	@patch("okx.Public_api.PublicAPI")
	def test_spot_min_volume_api_call(self, patch_public):
		_okx_api_client 				= copy.deepcopy(self.okx_api_client)
		_okx_api_client.public_client 	= patch_public
		_okx_api_client.get_spot_min_volume(symbol = "ETH-USDT")
		assert(patch_public.get_instruments.called)

	@patch("okx.Public_api.PublicAPI")
	def test_perpetual_min_volume_api_call(self, patch_public):
		_okx_api_client 				= copy.deepcopy(self.okx_api_client)
		_okx_api_client.public_client 	= patch_public
		_okx_api_client.get_perpetual_min_lot_size(symbol = "ETH-USDT-SWAP")
		assert(patch_public.get_instruments.called)

	def test_average_margin_purchase_price_computation_exact_order(self):
		price_qty_pairs_ordered = [[100, 100], [200, 100], [300, 50]]
		size = 250
		assert(self.okx_api_client._compute_average_margin_purchase_price(price_qty_pairs_ordered = price_qty_pairs_ordered, size = size) == 180)

	def test_average_margin_purchase_price_computation_partial_order(self):
		price_qty_pairs_ordered = [[150, 100], [300, 100], [500, 50]]
		size 					= 150
		assert(self.okx_api_client._compute_average_margin_purchase_price(price_qty_pairs_ordered = price_qty_pairs_ordered, size = size) == 200)

	def test_average_margin_purchase_price_computation_above_all_available_order(self):
		price_qty_pairs_ordered = [[100, 100], [200, 100], [300, 50]]
		size 					= 1000
		assert(self.okx_api_client._compute_average_margin_purchase_price(price_qty_pairs_ordered = price_qty_pairs_ordered, size = size) == 180)

	def test_average_margin_purchase_price_computation_single_order(self):
		price_qty_pairs_ordered = [[100, 100], [200, 100], [300, 50]]
		size 					= 1
		assert(self.okx_api_client._compute_average_margin_purchase_price(price_qty_pairs_ordered = price_qty_pairs_ordered, size = size) == 100)

	def test_bid_price_default_for_no_bids(self):
		bids 	= []
		size 	= 100
		assert(self.okx_api_client._compute_average_bid_price(bids = bids, size = size) == 0)

	def test_prioritization_of_single_highest_bids(self):
		bids 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 50
		assert(self.okx_api_client._compute_average_bid_price(bids = bids, size = size) == 500)

	def test_prioritization_of_two_most_highest_bids(self):
		bids 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 100
		assert(self.okx_api_client._compute_average_bid_price(bids = bids, size = size) == 400)

	def test_ask_price_default_for_no_asks(self):
		asks 	= []
		size 	= 100
		assert(self.okx_api_client._compute_average_ask_price(asks = asks, size = size) == sys.maxsize)

	def test_prioritization_of_single_lowest_asks(self):
		asks 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 50
		assert(self.okx_api_client._compute_average_ask_price(asks = asks, size = size) == 100)

	def test_prioritization_of_two_most_lowest_asks(self):
		asks 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 200
		assert(self.okx_api_client._compute_average_ask_price(asks = asks, size = size) == 125)

	@patch("okx.Trade_api.TradeAPI")
	def test_open_spot_orders_api_call(self, patch_trade):
		_okx_api_client 				= copy.deepcopy(self.okx_api_client)
		_okx_api_client.trade_client 	= patch_trade
		_okx_api_client.get_spot_open_orders(symbol = "ETH-USDT")
		assert(patch_trade.get_order_list.called)

	@patch("okx.Trade_api.TradeAPI")
	def test_open_perpetual_orders_api_call(self, patch_trade):
		_okx_api_client 				= copy.deepcopy(self.okx_api_client)
		_okx_api_client.trade_client 	= patch_trade
		_okx_api_client.get_perpetual_open_orders(symbol = "ETH-USDT-SWAP")
		assert(patch_trade.get_order_list.called)

	def test_most_recent_open_spot_order_retrieved(self):
		_okx_api_client = copy.deepcopy(self.okx_api_client)

		with patch.object(_okx_api_client, "get_spot_open_orders") as mock_get_spot_open_orders:
			mock_get_spot_open_orders.return_value 	= [	{"symbol" : "ETH-USDT", "orderId" : 1, "uTime" : 1200},
														{"symbol" : "ETH-USDT", "orderId" : 2, "uTime" : 2000},
														{"symbol" : "ETH-USDT", "orderId" : 3, "uTime" : 1600}]
			assert(_okx_api_client.get_spot_most_recent_open_order(symbol = "ETH-USDT")["orderId"] == 2)

	def test_most_recent_open_perpetual_order_retrieved(self):
		_okx_api_client = copy.deepcopy(self.okx_api_client)

		with patch.object(_okx_api_client, "get_perpetual_open_orders") as mock_get_perpetual_open_orders:
			mock_get_perpetual_open_orders.return_value = [ {"symbol" : "ETH-USDT-SWAP", "orderId" : 1, "uTime" : 1},
															{"symbol" : "ETH-USDT-SWAP", "orderId" : 2, "uTime" : 5},
															{"symbol" : "ETH-USDT-SWAP", "orderId" : 3, "uTime" : 3}]
			assert(_okx_api_client.get_perpetual_most_recent_open_order(symbol = "ETH-USDT-SWAP")["orderId"] == 2)
	
	def test_no_open_spot_orders(self):
		_okx_api_client = copy.deepcopy(self.okx_api_client)

		with patch.object(_okx_api_client, "get_spot_open_orders") as mock_get_spot_open_orders:
			mock_get_spot_open_orders.return_value 	= []
			assert(_okx_api_client.get_spot_most_recent_open_order(symbol = "ETH-USDT") == [])

	def test_no_open_perpetual_orders(self):
		_okx_api_client = copy.deepcopy(self.okx_api_client)

		with patch.object(_okx_api_client, "get_perpetual_open_orders") as mock_get_perpetual_open_orders:
			mock_get_perpetual_open_orders.return_value = []
			assert(_okx_api_client.get_perpetual_most_recent_open_order(symbol = "ETH-USDT-SWAP") == [])

	@patch("okx.Trade_api.TradeAPI")
	def test_fulfilled_spot_orders_api_call(self, patch_trade):
		_okx_api_client 				= copy.deepcopy(self.okx_api_client)
		_okx_api_client.trade_client 	= patch_trade
		_okx_api_client.get_spot_fulfilled_orders(symbol = "ETH-USDT")
		assert(patch_trade.get_orders_history.called)

	@patch("okx.Trade_api.TradeAPI")
	def test_fulfilled_perpetual_orders_api_call(self, patch_trade):
		_okx_api_client 				= copy.deepcopy(self.okx_api_client)
		_okx_api_client.trade_client 	= patch_trade
		_okx_api_client.get_perpetual_fulfilled_orders(symbol = "ETH-USDT-SWAP")
		assert(patch_trade.get_orders_history.called)

	def test_fulfilled_spot_order_retrieved(self):
		_okx_api_client = copy.deepcopy(self.okx_api_client)

		with patch.object(_okx_api_client, "get_spot_fulfilled_orders") as mock_get_spot_open_orders:
			mock_get_spot_open_orders.return_value 	=	[{"symbol" : "ETH-USDT", "orderId" : 1, "uTime" : 1200},
														 {"symbol" : "ETH-USDT", "orderId" : 2, "uTime" : 2000},
														 {"symbol" : "ETH-USDT", "orderId" : 3, "uTime" : 1600}]

			assert(_okx_api_client.get_spot_most_recent_fulfilled_order(symbol = "ETH-USDT")["orderId"] == 2)

	def test_fulfilled_perpetual_order_retrieved(self):
		_okx_api_client = copy.deepcopy(self.okx_api_client)

		with patch.object(_okx_api_client, "get_perpetual_fulfilled_orders") as mock_get_spot_open_orders:
			mock_get_spot_open_orders.return_value 	=	[{"symbol" : "ETH-USDT-SWAP", "orderId" : 1, "uTime" : 1},
														 {"symbol" : "ETH-USDT-SWAP", "orderId" : 2, "uTime" : 5},
														 {"symbol" : "ETH-USDT-SWAP", "orderId" : 3, "uTime" : 3}]

			assert(_okx_api_client.get_perpetual_most_recent_fulfilled_order(symbol = "ETH-USDT")["orderId"] == 2)

	def test_no_fulfilled_spot_orders(self):
		_okx_api_client = copy.deepcopy(self.okx_api_client)

		with patch.object(_okx_api_client, "get_spot_fulfilled_orders") as mock_get_spot_fulfilled_orders:
			mock_get_spot_fulfilled_orders.return_value 	= []
			assert(_okx_api_client.get_spot_most_recent_fulfilled_order(symbol = "ETH-USDT") == [])

	def test_no_fulfilled_perpetual_orders(self):
		_okx_api_client = copy.deepcopy(self.okx_api_client)

		with patch.object(_okx_api_client, "get_perpetual_fulfilled_orders") as mock_get_perpetual_fulfilled_orders:
			mock_get_perpetual_fulfilled_orders.return_value = []
			assert(_okx_api_client.get_perpetual_most_recent_fulfilled_order(symbol = "ETH-USDT-SWAP") == [])

	@patch("okx.Trade_api.TradeAPI")
	def test_spot_order_call_invoked(self, patch_trade):
		_okx_api_client 					 = copy.deepcopy(self.okx_api_client)
		_okx_api_client.trade_client 		 = patch_trade
		patch_trade.place_order.return_value = {"orderId" : "0001"}

		_okx_api_client.place_spot_order(symbol 		 = "BTC-USDT", 
										 order_type 	 = "market", 
										 order_side 	 = "sell", 
										 price 			 = 1,
										 size 			 = 1,
										 target_currency = "base_ccy"
										)
		assert(patch_trade.place_order.called)

	@patch("okx.Trade_api.TradeAPI")
	def test_futures_order_call_invoked(self, patch_trade):
		_okx_api_client 					  = copy.deepcopy(self.okx_api_client)
		_okx_api_client.trade_client 		  = patch_trade
		patch_trade.place_order.return_value  = {"orderId" : "0001"}

		_okx_api_client.place_perpetual_order(	symbol 			= "BTC-USDT-SWAP",
												position_side  	= "long",
												order_type 		= "market", 
												order_side 		= "buy", 
												price 			= 1,
												size 			= 1,
											)
		assert(patch_trade.place_order.called)

	def test_spot_order_revertion(self):
		_okx_api_client = copy.deepcopy(self.okx_api_client)
		with patch.object(_okx_api_client, "place_spot_order") as mock_place_spot_order:
			_okx_api_client.revert_spot_order(	order_resp = { 
																"data" : [
																		    {
																		      "ordId": "312269865356374016",
																		      "sCode": "0",
																		      "sMsg": ""
																	    	}
															  			]
												  			},
												revert_params = {}
							  				)
			assert(mock_place_spot_order.called)

	def test_perpetual_order_cancellation_without_error(self):
		_okx_api_client = copy.deepcopy(self.okx_api_client)
		with patch.object(_okx_api_client, "place_perpetual_order") as mock_place_perpetual_order:
			_okx_api_client.revert_perpetual_order(	order_resp = { 
																	"data" : [
																			    {
																			      "ordId": "312269865356374016",
																			      "sCode": "0",
																			      "sMsg": ""
																		    	}
																  			]
												  				},
													revert_params = {}
							  					)
			assert(mock_place_perpetual_order.called)

	@patch("okx.Public_api.PublicAPI")
	def test_get_perpetual_funding_rates(self, patch_public):
		_okx_api_client 				= copy.deepcopy(self.okx_api_client)
		_okx_api_client.public_client 	= patch_public

		patch_public.get_funding_rate.return_value = {"data" : [{"fundingRate" : 0.01, "nextFundingRate" : -0.01}]}
		(funding_rate, estimated_funding_rate) = _okx_api_client.get_perpetual_funding_rate(symbol = "ETHUSDT")
		assert (funding_rate == 0.01 and estimated_funding_rate == -0.01)

	@freeze_time("2022-01-01 03:55:00")
	def test_funding_rate_is_valid_interval(self):
		_okx_api_client 	= copy.deepcopy(self.okx_api_client)
		_okx_api_client.okx_funding_rate_snapshot_times = ["04:00"]
		assert(_okx_api_client.funding_rate_valid_interval(seconds_before = 300))

	@freeze_time("2022-01-01 03:50:00")
	def test_funding_rate_is_not_valid_interval_A(self):
		_okx_api_client 	= copy.deepcopy(self.okx_api_client)
		_okx_api_client.okx_funding_rate_snapshot_times = ["04:00"]
		assert(not _okx_api_client.funding_rate_valid_interval(seconds_before = 300))

	@freeze_time("2022-01-01 04:00:01")
	def test_funding_rate_is_not_valid_interval_B(self):
		_okx_api_client 	= copy.deepcopy(self.okx_api_client)
		_okx_api_client.okx_funding_rate_snapshot_times = ["04:00"]
		assert(not _okx_api_client.funding_rate_valid_interval(seconds_before = 300))
		return

	def test_effective_funding_rate_is_zero_when_flag_is_disabled(self):
		_okx_api_client 	= copy.deepcopy(self.okx_api_client)
		_okx_api_client.funding_rate_enable = False

		with patch.object(_okx_api_client, "funding_rate_valid_interval") as mock_funding_rate_valid_interval, \
			 patch.object(_okx_api_client, "get_perpetual_funding_rate") as mock_get_futures_funding_rate:
			mock_funding_rate_valid_interval.return_value = True
			mock_get_futures_funding_rate.return_value 	  = (0.01, -0.01)
			assert _okx_api_client.get_perpetual_effective_funding_rate(symbol = "ETH-USDT", seconds_before = 300) == (0, 0)
		return

	def test_effective_funding_rate_is_zero_when_invalid_interval(self):
		_okx_api_client 	= copy.deepcopy(self.okx_api_client)

		with patch.object(_okx_api_client, "funding_rate_valid_interval") as mock_funding_rate_valid_interval, \
			 patch.object(_okx_api_client, "get_perpetual_funding_rate") as mock_get_futures_funding_rate:
			mock_funding_rate_valid_interval.return_value 	= False
			mock_get_futures_funding_rate.return_value 		= (0.01, -0.01)
			assert _okx_api_client.get_perpetual_effective_funding_rate(symbol = "ETH-USDT", seconds_before = 300) == (0, 0)
		return

	@patch("okx.Public_api.PublicAPI")
	def test_effective_funding_rate_is_non_zero(self, patch_public):
		_okx_api_client 				= copy.deepcopy(self.okx_api_client)
		_okx_api_client.public_client 	= patch_public
		patch_public.get_funding_rate.return_value = {"data" : [{"fundingRate" : 0.01, "nextFundingRate" : -0.01}]}

		with patch.object(_okx_api_client, "funding_rate_valid_interval") as mock_funding_rate_valid_interval:
			mock_funding_rate_valid_interval.return_value = True
			assert _okx_api_client.get_perpetual_effective_funding_rate(symbol = "ETH-USDT", seconds_before = 300) == (0.01, 0)
		return

	@patch("okx.Account_api.AccountAPI")
	def test_perpetual_leverage_set(self, patch_account):
		_okx_api_client 				= copy.deepcopy(self.okx_api_client)
		_okx_api_client.account_client 	= patch_account
		_okx_api_client.set_perpetual_leverage(symbol = "ETH-USDT", leverage = 5)
		assert patch_account.set_leverage.called