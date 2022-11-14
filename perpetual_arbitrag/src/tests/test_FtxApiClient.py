import copy
import ftx
import sys
import pytest
from clients.FtxApiClient import FtxApiClient
from freezegun import freeze_time
from unittest import TestCase
from unittest.mock import patch

class TestOkxApiClient(TestCase):
	def setUp(self):
		self.ftx_client = FtxApiClient(api_key = None, api_secret_key = None, funding_rate_enable = True)

	@patch("ftx.FtxClient")
	def test_account_leverage_set(self, mock_ftx_client):
		ftx_api_client 			= copy.deepcopy(self.ftx_client)
		ftx_api_client.client 	= mock_ftx_client
		ftx_api_client.set_account_leverage(leverage = 5)
		mock_ftx_client.set_leverage.assert_called_with(leverage = 5)

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

	@patch("ftx.FtxClient")
	def test_compute_correct_perpetual_amt(self, mock_ftx_client):
		ftx_api_client = copy.deepcopy(self.ftx_client)
		ftx_api_client.client = mock_ftx_client
		mock_ftx_client.get_positions.return_value 	= [
													    {"future": "ETH-PERP", "netSize" : 0.1},
													    {"future": "BTC-PERP", "netSize" : 0.2},
													    {"future": "SOL-PERP", "netSize" : 0.3},
													]
		result = ftx_api_client.get_perpetual_trading_account_details(currency = "BTC-PERP")

		mock_ftx_client.get_positions.assert_called()
		assert(result == 0.2)

	@patch("ftx.FtxClient")
	def test_perpetual_trading_price_api_call(self, mock_ftx_client):
		ftx_api_client = copy.deepcopy(self.ftx_client)
		ftx_api_client.client = mock_ftx_client
		mock_ftx_client.get_market.return_value 	= {	
														"name": "BTC-PERP", 
														"type": "future", 
														"ask": 3949.25,
												      	"bid": 3949,
												      	"last": 10579.52,
												      	"postOnly": False,
												      	"price": 10579.52,
											      	}
		result = ftx_api_client.get_perpetual_trading_price(symbol = "BTC-PERP")
		mock_ftx_client.get_market.assert_called_with(market = "BTC-PERP")
		assert(result == 10579.52)

	@patch("ftx.FtxClient")
	def test_perpetual_min_lot_size_api_call(self, mock_ftx_client):
		ftx_api_client = copy.deepcopy(self.ftx_client)
		ftx_api_client.client = mock_ftx_client
		mock_ftx_client.get_market.return_value 	= {
														"ask": 4196,
														"bid": 4114.25,
														"change1h": 0,
														"change24h": 0,
														"description": "Bitcoin March 2019 Futures",
														"enabled": True,
														"expired": False,
														"expiry": "2019-03-29T03:00:00+00:00",
														"index": 3919.58841011,
														"last": 4196,
														"lowerBound": 3663.75,
														"mark": 3854.75,
														"name": "BTC-0329",
														"perpetual": False,
														"postOnly": False,
														"priceIncrement": 0.25,
														"sizeIncrement": 0.0001,
														"underlying": "BTC",
														"upperBound": 4112.2,
														"type": "future"
													}

		result = ftx_api_client.get_perpetual_min_lot_size(symbol = "BTC-0329")
		mock_ftx_client.get_market.assert_called_with(market = "BTC-0329")
		assert(result == 0.0001)

	def test_average_margin_purchase_price_computation_exact_order(self):
		price_qty_pairs_ordered = [[100, 100], [200, 100], [300, 50]]
		size = 250
		assert(self.ftx_client._compute_average_margin_purchase_price(price_qty_pairs_ordered = price_qty_pairs_ordered, size = size) == 180)

	def test_bid_price_default_for_no_bids(self):
		bids 	= []
		size 	= 100
		assert(self.ftx_client._compute_average_bid_price(bids = bids, size = size) == 0)

	def test_prioritization_of_single_highest_bids(self):
		bids 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 50
		assert(self.ftx_client._compute_average_bid_price(bids = bids, size = size) == 500)

	def test_prioritization_of_two_most_highest_bids(self):
		bids 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 100
		assert(self.ftx_client._compute_average_bid_price(bids = bids, size = size) == 400)

	def test_ask_price_default_for_no_asks(self):
		asks 	= []
		size 	= 100
		assert(self.ftx_client._compute_average_ask_price(asks = asks, size = size) == sys.maxsize)

	def test_prioritization_of_single_lowest_asks(self):
		asks 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 50
		assert(self.ftx_client._compute_average_ask_price(asks = asks, size = size) == 100)

	def test_prioritization_of_two_most_lowest_asks(self):
		asks 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 200
		assert(self.ftx_client._compute_average_ask_price(asks = asks, size = size) == 125)

	@patch("ftx.FtxClient")
	def test_open_perpetual_orders_api_call(self, mock_ftx_client):
		ftx_api_client 			= copy.deepcopy(self.ftx_client)
		ftx_api_client.client 	= mock_ftx_client
		expected_response 		= 	[
										{
											"createdAt": "2019-03-05T09:56:55.728933+00:00",
											"filledSize": 10,
											"future": "XRP-PERP",
											"price": 0.306525,
											"avgFillPrice": 0.306526,
											"remainingSize": 31421,
											"side": "sell",
										},
										{
											"createdAt": "2019-03-06T09:56:55.728933+00:00",
											"filledSize": 10,
											"future": "XRP-PERP",
											"price": 0.306525,
											"avgFillPrice": 0.306526,
											"remainingSize": 31421,
											"side": "sell",
										}
									]
		mock_ftx_client.get_open_orders.return_value = expected_response

		result = ftx_api_client.get_perpetual_open_orders(symbol = "XRP-PERP")
		mock_ftx_client.get_open_orders.assert_called_with(market = "XRP-PERP")
		assert(result == expected_response)

	def test_most_recent_open_perpetual_order_retrieved(self):
		ftx_api_client 			= copy.deepcopy(self.ftx_client)

		with patch.object(ftx_api_client, "get_perpetual_open_orders") as mock_get_perpetual_open_orders:
			mock_get_perpetual_open_orders.return_value = [
															{
																"createdAt": "2019-03-05T09:56:55.728933+00:00",
																"filledSize": 1,
																"future": "XRP-PERP",
																"price": 1,
																"avgFillPrice": 1,
																"remainingSize": 1,
																"side": "sell",
															},
															{
																"createdAt": "2019-03-06T09:56:55.728933+00:00",
																"filledSize": 2,
																"future": "XRP-PERP",
																"price": 2,
																"avgFillPrice": 2,
																"remainingSize": 2,
																"side": "sell",
															},
															{
																"createdAt": "2019-03-04T09:56:55.728933+00:00",
																"filledSize": 3,
																"future": "XRP-PERP",
																"price": 3,
																"avgFillPrice": 3,
																"remainingSize": 3,
																"side": "sell",
															}
														]

			result	= ftx_api_client.get_perpetual_most_recent_open_order(symbol = "XRP-PERP")
			assert(result["createdAt"] == "2019-03-06T09:56:55.728933+00:00")
	
	def test_no_open_perpetual_orders(self):
		ftx_api_client 			= copy.deepcopy(self.ftx_client)

		with patch.object(ftx_api_client, "get_perpetual_open_orders") as mock_get_perpetual_open_orders:
			mock_get_perpetual_open_orders.return_value = []
			result	= ftx_api_client.get_perpetual_most_recent_open_order(symbol = "XRP-PERP")
			assert(result == [])

	@patch("ftx.FtxClient")
	def test_fulfilled_perpetual_orders_api_call(self, mock_ftx_client):
		ftx_api_client 			= copy.deepcopy(self.ftx_client)
		ftx_api_client.client 	= mock_ftx_client
		ftx_api_client.get_perpetual_fulfilled_orders(symbol = "XRP-PERP")
		mock_ftx_client.get_order_history.assert_called()

	def test_fulfilled_perpetual_order_retrieved(self):
		ftx_api_client 			= copy.deepcopy(self.ftx_client)

		with patch.object(ftx_api_client, "get_perpetual_fulfilled_orders") as mock_get_perpetual_fulfilled_orders:
			mock_get_perpetual_fulfilled_orders.return_value = [	
																{
																	"id": 100,
																	"createdAt": "2019-03-04T09:56:55.728933+00:00",
																	"filledSize": 3,
																	"future": "XRP-PERP",
																	"price": 3,
																	"avgFillPrice": 3,
																	"remainingSize": 3,
																	"side": "sell",
																	"status": "closed",
																},
																{	
																	"id": 200,
																	"createdAt": "2019-03-04T09:56:55.728933+00:00",
																	"filledSize": 3,
																	"future": "XRP-PERP",
																	"price": 3,
																	"avgFillPrice": 3,
																	"remainingSize": 3,
																	"side": "sell",
																	"status": "open",
																},
																{
																	"id": 300,
																	"createdAt": "2019-03-04T09:56:55.728933+00:00",
																	"filledSize": 3,
																	"future": "XRP-PERP",
																	"price": 3,
																	"avgFillPrice": 3,
																	"remainingSize": 3,
																	"side": "sell",
																	"status": "new",
																}
															]
			
			result = ftx_api_client.get_perpetual_most_recent_fulfilled_order(symbol = "XRP-USDT")
			assert(result["id"] == 100)

	def test_no_fulfilled_perpetual_orders(self):
		ftx_api_client 			= copy.deepcopy(self.ftx_client)

		with patch.object(ftx_api_client, "get_perpetual_fulfilled_orders") as mock_get_perpetual_fulfilled_orders:
			mock_get_perpetual_fulfilled_orders.return_value = []
			result = ftx_api_client.get_perpetual_most_recent_fulfilled_order(symbol = "XRP-USDT")
			assert(result == [])

	@patch("ftx.FtxClient")
	def test_get_perpetual_funding_rates(self, mock_ftx_client):
		ftx_api_client 			= copy.deepcopy(self.ftx_client)
		ftx_api_client.client 	= mock_ftx_client
		mock_ftx_client.get_future_stats.return_value = {
														    "volume": 1000.23,
														    "nextFundingRate": 0.00025,
														    "nextFundingTime": "2019-03-29T03:00:00+00:00",
														    "expirationPrice": 3992.1,
														    "predictedExpirationPrice": 3993.6,
														    "strikePrice": 8182.35,
														    "openInterest": 21124.583
														}

		(funding_rate, funding_time) = ftx_api_client.get_perpetual_funding_rate(symbol = "XRP-PERP")
		assert((funding_rate == 0.00025) & (funding_time == "2019-03-29T03:00:00+00:00"))

	def test_effective_funding_rate_is_zero_when_flag_is_disabled(self):
		ftx_api_client 			= copy.deepcopy(self.ftx_client)
		ftx_api_client.funding_rate_enable = False

		with patch.object(ftx_api_client, "get_perpetual_funding_rate") as mock_get_perpetual_funding_rate:
			mock_get_perpetual_funding_rate.return_value 	= (-0.02, "2019-03-29T10:00:00+00:00")
			result 	= ftx_api_client.get_perpetual_effective_funding_rate(symbol = "ETH-PERP", seconds_before_current = 300)
			assert result == 0

	@freeze_time("2019-03-29T09:00:00+00:00")
	def test_effective_funding_rate_is_zero_when_invalid_interval(self):
		ftx_api_client 			= copy.deepcopy(self.ftx_client)
		ftx_api_client.funding_rate_enable = True

		with patch.object(ftx_api_client, "get_perpetual_funding_rate") as mock_get_perpetual_funding_rate:
			mock_get_perpetual_funding_rate.return_value 	= (-0.02, "2019-03-29T10:00:00+00:00")
			result 	= ftx_api_client.get_perpetual_effective_funding_rate(symbol = "ETH-PERP", seconds_before_current = 300)
			assert result == 0

	@freeze_time("2019-03-29T09:00:00+00:00")
	def test_effective_funding_rate_is_non_zero(self):
		ftx_api_client 			= copy.deepcopy(self.ftx_client)
		ftx_api_client.funding_rate_enable = True

		with patch.object(ftx_api_client, "get_perpetual_funding_rate") as mock_get_perpetual_funding_rate:
			mock_get_perpetual_funding_rate.return_value 	= (-0.02, "2019-03-29T10:00:00+00:00")
			result 	= ftx_api_client.get_perpetual_effective_funding_rate(symbol = "ETH-PERP", seconds_before_current = 7200)
			assert result == -0.02

	@patch("ftx.FtxClient")
	def test_get_margin_symbols_called(self, mock_ftx_client):
		ftx_api_client = copy.deepcopy(self.ftx_client)
		ftx_api_client.client = mock_ftx_client

		mock_ftx_client.get_markets.return_value = 	[	
														{"name": "BTC-PERP"}, 
														{"name": "ETH-USDT"}, 
														{"name": "SOL-PERP"}, 
														{"name": "SOL-BTC"}
													]
		result = ftx_api_client.get_margin_symbols()
		mock_ftx_client.get_markets.assert_called() 
		assert(result == ["ETH-USDT", "SOL-BTC"])

	@patch("ftx.FtxClient")
	def test_get_margin_trading_account_details(self, mock_ftx_client):
		ftx_api_client = copy.deepcopy(self.ftx_client)
		ftx_api_client.client = mock_ftx_client

		mock_ftx_client.get_balances.return_value = [	
														{"coin": "BTC",  "spotBorrow": 1}, 
														{"coin": "ETH",  "spotBorrow": 2}, 
														{"coin": "SOL",  "spotBorrow": 3}, 
														{"coin": "USDT", "spotBorrow": 4}
													]

		result 	= ftx_api_client.get_margin_trading_account_details(currency = "SOL")
		mock_ftx_client.get_balances.assert_called()
		assert(result == 3)

	@patch("ftx.FtxClient")
	def test_get_margin_trading_price(self, mock_ftx_client):
		ftx_api_client = copy.deepcopy(self.ftx_client)
		ftx_api_client.client = mock_ftx_client
		ftx_api_client.get_margin_trading_price(symbol = "BTC/USDT")
		mock_ftx_client.get_market.assert_called_with(market = "BTC/USDT")