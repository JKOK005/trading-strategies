import copy
import ftx
import sys
import pytest
from clients.FtxApiClient import FtxApiClient
from unittest import TestCase
from unittest.mock import patch

class TestOkxApiClient(TestCase):
	def setUp(self):
		self.ftx_client = FtxApiClient(api_key = None, api_secret_key = None, funding_rate_enable = True)

	@patch("ftx.FtxClient")
	def test_get_perpetual_symbols_called(self, mock_ftx_client):
		ftx_api_client = copy.deepcopy(self.ftx_client)
		ftx_api_client.client = mock_ftx_client

		mock_ftx_client.get_markets.return_value = 	[	
														{"name": "BTC-PERP"}, 
														{"name": "ETH-USDT"}, 
														{"name": "SOL-PERP"}, 
														{"name": "SOL-BTC"}
													]
		result = ftx_api_client.get_perpetual_symbols()
		
		mock_ftx_client.get_markets.assert_called() 
		assert(result == ["BTC-PERP", "SOL-PERP"])
		return

	# @patch("okx.Account_api.AccountAPI")
	# def test_compute_correct_perpetual_amt(self, patch_account):
	# 	_okx_api_client 				= copy.deepcopy(self.okx_api_client)
	# 	_okx_api_client.account_client 	= patch_account
	# 	patch_account.get_positions.return_value = {"code": "0",
	# 												 "msg": "",
	# 												 "data": [
	# 												    {"availPos":"1", "ccy":"ETH-USDT-SWAP", "posSide":"long"},
	# 												    {"availPos":"1", "ccy":"ETH-USDT-SWAP", "posSide":"short"},
	# 												    {"availPos":"3", "ccy":"ETH-USDT-SWAP", "posSide":"short"},
	# 												    {"availPos":"3", "ccy":"ETH-USDT-SWAP", "posSide":"long"},
	# 												    {"availPos":"5", "ccy":"ETH-USDT-SWAP", "posSide":"long"},
	# 												  ]
	# 												}
	# 	perpetual_position 	= _okx_api_client.get_perpetual_trading_account_details(currency = "ETH-USDT-SWAP")
	# 	assert(perpetual_position == 5)

	# @patch("okx.Market_api.MarketAPI")
	# def test_perpetual_trading_price_api_call(self, patch_market):
	# 	_okx_api_client 				= copy.deepcopy(self.okx_api_client)
	# 	_okx_api_client.market_client 	= patch_market
	# 	_okx_api_client.get_perpetual_trading_price(symbol = "ETH-USDT-SWAP")
	# 	assert(patch_market.get_ticker.called)

	# @patch("okx.Public_api.PublicAPI")
	# def test_perpetual_min_volume_api_call(self, patch_public):
	# 	_okx_api_client 				= copy.deepcopy(self.okx_api_client)
	# 	_okx_api_client.public_client 	= patch_public
	# 	_okx_api_client.get_perpetual_min_lot_size(symbol = "ETH-USDT-SWAP")
	# 	assert(patch_public.get_instruments.called)

	# def test_average_margin_purchase_price_computation_exact_order(self):
	# 	price_qty_pairs_ordered = [[100, 100], [200, 100], [300, 50]]
	# 	size = 250
	# 	assert(self.okx_api_client._compute_average_margin_purchase_price(price_qty_pairs_ordered = price_qty_pairs_ordered, size = size) == 180)

	# def test_bid_price_default_for_no_bids(self):
	# 	bids 	= []
	# 	size 	= 100
	# 	assert(self.okx_api_client._compute_average_bid_price(bids = bids, size = size) == 0)

	# def test_prioritization_of_single_highest_bids(self):
	# 	bids 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
	# 	size 	= 50
	# 	assert(self.okx_api_client._compute_average_bid_price(bids = bids, size = size) == 500)

	# def test_prioritization_of_two_most_highest_bids(self):
	# 	bids 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
	# 	size 	= 100
	# 	assert(self.okx_api_client._compute_average_bid_price(bids = bids, size = size) == 400)

	# def test_ask_price_default_for_no_asks(self):
	# 	asks 	= []
	# 	size 	= 100
	# 	assert(self.okx_api_client._compute_average_ask_price(asks = asks, size = size) == sys.maxsize)

	# def test_prioritization_of_single_lowest_asks(self):
	# 	asks 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
	# 	size 	= 50
	# 	assert(self.okx_api_client._compute_average_ask_price(asks = asks, size = size) == 100)

	# def test_prioritization_of_two_most_lowest_asks(self):
	# 	asks 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
	# 	size 	= 200
	# 	assert(self.okx_api_client._compute_average_ask_price(asks = asks, size = size) == 125)

	# @patch("okx.Trade_api.TradeAPI")
	# def test_open_perpetual_orders_api_call(self, patch_trade):
	# 	_okx_api_client 				= copy.deepcopy(self.okx_api_client)
	# 	_okx_api_client.trade_client 	= patch_trade
	# 	_okx_api_client.get_perpetual_open_orders(symbol = "ETH-USDT-SWAP")
	# 	assert(patch_trade.get_order_list.called)

	# def test_most_recent_open_perpetual_order_retrieved(self):
	# 	_okx_api_client = copy.deepcopy(self.okx_api_client)

	# 	with patch.object(_okx_api_client, "get_perpetual_open_orders") as mock_get_perpetual_open_orders:
	# 		mock_get_perpetual_open_orders.return_value = [ {"symbol" : "ETH-USDT-SWAP", "orderId" : 1, "uTime" : 1},
	# 														{"symbol" : "ETH-USDT-SWAP", "orderId" : 2, "uTime" : 5},
	# 														{"symbol" : "ETH-USDT-SWAP", "orderId" : 3, "uTime" : 3}]
	# 		assert(_okx_api_client.get_perpetual_most_recent_open_order(symbol = "ETH-USDT-SWAP")["orderId"] == 2)
	
	# def test_no_open_perpetual_orders(self):
	# 	_okx_api_client = copy.deepcopy(self.okx_api_client)

	# 	with patch.object(_okx_api_client, "get_perpetual_open_orders") as mock_get_perpetual_open_orders:
	# 		mock_get_perpetual_open_orders.return_value = []
	# 		assert(_okx_api_client.get_perpetual_most_recent_open_order(symbol = "ETH-USDT-SWAP") == [])

	# @patch("okx.Trade_api.TradeAPI")
	# def test_fulfilled_perpetual_orders_api_call(self, patch_trade):
	# 	_okx_api_client 				= copy.deepcopy(self.okx_api_client)
	# 	_okx_api_client.trade_client 	= patch_trade
	# 	_okx_api_client.get_perpetual_fulfilled_orders(symbol = "ETH-USDT-SWAP")
	# 	assert(patch_trade.get_orders_history.called)

	# def test_fulfilled_perpetual_order_retrieved(self):
	# 	_okx_api_client = copy.deepcopy(self.okx_api_client)

	# 	with patch.object(_okx_api_client, "get_perpetual_fulfilled_orders") as mock_get_spot_open_orders:
	# 		mock_get_spot_open_orders.return_value 	=	[{"symbol" : "ETH-USDT-SWAP", "orderId" : 1, "uTime" : 1},
	# 													 {"symbol" : "ETH-USDT-SWAP", "orderId" : 2, "uTime" : 5},
	# 													 {"symbol" : "ETH-USDT-SWAP", "orderId" : 3, "uTime" : 3}]

	# 		assert(_okx_api_client.get_perpetual_most_recent_fulfilled_order(symbol = "ETH-USDT")["orderId"] == 2)

	# def test_no_fulfilled_perpetual_orders(self):
	# 	_okx_api_client = copy.deepcopy(self.okx_api_client)

	# 	with patch.object(_okx_api_client, "get_perpetual_fulfilled_orders") as mock_get_perpetual_fulfilled_orders:
	# 		mock_get_perpetual_fulfilled_orders.return_value = []
	# 		assert(_okx_api_client.get_perpetual_most_recent_fulfilled_order(symbol = "ETH-USDT-SWAP") == [])

	# @patch("okx.Public_api.PublicAPI")
	# def test_get_perpetual_funding_rates(self, patch_public):
	# 	_okx_api_client 				= copy.deepcopy(self.okx_api_client)
	# 	_okx_api_client.public_client 	= patch_public

	# 	patch_public.get_funding_rate.return_value = {"data" : [{"fundingRate" : 0.01, "nextFundingRate" : -0.01}]}
	# 	(funding_rate, estimated_funding_rate) = _okx_api_client.get_perpetual_funding_rate(symbol = "ETHUSDT")
	# 	assert (funding_rate == 0.01 and estimated_funding_rate == -0.01)

	# def test_effective_funding_rate_is_zero_when_flag_is_disabled(self):
	# 	_okx_api_client 	= copy.deepcopy(self.okx_api_client)
	# 	_okx_api_client.funding_rate_enable = False

	# 	with patch.object(_okx_api_client, "funding_rate_valid_interval") as mock_funding_rate_valid_interval, \
	# 		 patch.object(_okx_api_client, "get_perpetual_funding_rate") as mock_get_futures_funding_rate:
	# 		mock_funding_rate_valid_interval.return_value = True
	# 		mock_get_futures_funding_rate.return_value 	  = (0.01, -0.01)
	# 		assert _okx_api_client.get_perpetual_effective_funding_rate(symbol = "ETH-USDT", seconds_before_current = 300, seconds_before_estimated = 300) == (0, 0)
	# 	return

	# def test_effective_funding_rate_is_zero_when_invalid_interval(self):
	# 	_okx_api_client 	= copy.deepcopy(self.okx_api_client)

	# 	with patch.object(_okx_api_client, "funding_rate_valid_interval") as mock_funding_rate_valid_interval, \
	# 		 patch.object(_okx_api_client, "get_perpetual_funding_rate") as mock_get_futures_funding_rate:
	# 		mock_funding_rate_valid_interval.return_value 	= False
	# 		mock_get_futures_funding_rate.return_value 		= (0.01, -0.01)
	# 		assert _okx_api_client.get_perpetual_effective_funding_rate(symbol = "ETH-USDT", seconds_before_current = 300, seconds_before_estimated = 300) == (0, 0)
	# 	return

	# @patch("okx.Public_api.PublicAPI")
	# def test_effective_funding_rate_is_non_zero(self, patch_public):
	# 	_okx_api_client 				= copy.deepcopy(self.okx_api_client)
	# 	_okx_api_client.public_client 	= patch_public
	# 	patch_public.get_funding_rate.return_value = {"data" : [{"fundingRate" : 0.01, "nextFundingRate" : -0.01}]}

	# 	with patch.object(_okx_api_client, "funding_rate_valid_interval") as mock_funding_rate_valid_interval:
	# 		mock_funding_rate_valid_interval.return_value = True
	# 		assert _okx_api_client.get_perpetual_effective_funding_rate(symbol = "ETH-USDT", seconds_before_current = 300, seconds_before_estimated = 300) == (0.01, -0.01)
	# 	return

	# @patch("okx.Account_api.AccountAPI")
	# def test_perpetual_leverage_set(self, patch_account):
	# 	_okx_api_client 				= copy.deepcopy(self.okx_api_client)
	# 	_okx_api_client.account_client 	= patch_account
	# 	_okx_api_client.set_perpetual_leverage(symbol = "ETH-USDT", leverage = 5)
	# 	assert patch_account.set_leverage.called