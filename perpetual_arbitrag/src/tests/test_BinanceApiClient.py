import binance
import copy
import sys
import pytest
from clients.BinanceApiClient import BinanceApiClient
from freezegun import freeze_time
from unittest import TestCase
from unittest.mock import patch

class TestBinanceApiClient(TestCase):
	def setUp(self):
		self.binance_client = BinanceApiClient(api_key = None, api_secret_key = None, funding_rate_enable = True)

	@patch("binance.client")
	@patch("binance.um_futures")
	def test_perpetual_leverage_set(self, mock_client, mock_futures_client):
		binance_api_client 					= copy.deepcopy(self.binance_client)
		binance_api_client.client 			= mock_client
		binance_api_client.futures_client	= mock_futures_client
		binance_api_client.set_perpetual_leverage(symbol = "BTC-USDT-PERP", leverage = 5)
		mock_futures_client.change_leverage.assert_called_with(symbol = "BTC-USDT-PERP", leverage = 5)

	@patch("binance.client")
	@patch("binance.um_futures")
	def test_get_perpetual_symbols_called(self, mock_client, mock_futures_client):
		binance_api_client 					= copy.deepcopy(self.binance_client)
		binance_api_client.client 			= mock_client
		binance_api_client.futures_client	= mock_futures_client

		mock_futures_client.exchange_info.return_value = {
														    "exchangeFilters": [],
														    "rateLimits": [
														        {
														            "interval": "MINUTE",
														            "intervalNum": 1,
														            "limit": 2400,
														            "rateLimitType": "REQUEST_WEIGHT" 
														        },
														    ],
														    "serverTime": 1565613908500,
														    "assets": [ 
														        {
														            "asset": "BUSD",
														            "marginAvailable": True,
														            "autoAssetExchange" : 0
														        },
														    ],
														    "symbols": [
														        {
														            "symbol": "BLZUSDT",
														            "pair": "BLZUSDT",
														            "contractType": "PERPETUAL",
														            "deliveryDate": 4133404800000,
														            "onboardDate": 1598252400000,
														            "status": "TRADING",
														            "maintMarginPercent": "2.5000",  
														            "requiredMarginPercent": "5.0000",  
														            "baseAsset": "BLZ", 
														            "quoteAsset": "USDT",
														            "marginAsset": "USDT",
														            "pricePrecision": 5,    
														            "quantityPrecision": 0, 
														            "baseAssetPrecision": 8,
														            "quotePrecision": 8, 
														            "underlyingType": "COIN",
														            "underlyingSubType": ["STORAGE"],
														            "settlePlan": 0,
														            "triggerProtect": "0.15",
														            "filters": [],
														            "OrderType": [
														                "LIMIT",
														                "MARKET",
														                "STOP",
														                "STOP_MARKET",
														                "TAKE_PROFIT",
														                "TAKE_PROFIT_MARKET",
														                "TRAILING_STOP_MARKET" 
														            ],
														            "timeInForce": [
														                "GTC", 
														                "IOC", 
														                "FOK", 
														                "GTX" 
														            ],
														            "liquidationFee": "0.010000",  
														            "marketTakeBound": "0.30",
														        }
														    ],
														    "timezone": "UTC" 
														}

		result = binance_api_client.get_perpetual_symbols()
		mock_futures_client.exchange_info.assert_called() 
		assert(result == ["BLZUSDT"])

	@patch("binance.client")
	@patch("binance.um_futures")
	def test_compute_correct_perpetual_amt(self, mock_client, mock_futures_client):
		binance_api_client 					= copy.deepcopy(self.binance_client)
		binance_api_client.client 			= mock_client
		binance_api_client.futures_client	= mock_futures_client
		expected_resp 	= {   
						    "feeTier": 0,       
						    "canTrade": True,   
						    "canDeposit": True,     
						    "canWithdraw": True,    
						    "updateTime": 0,        
						    "totalInitialMargin": "0.00000000",    
						    "totalMaintMargin": "0.00000000",     
						    "totalWalletBalance": "23.72469206",     
						    "totalUnrealizedProfit": "0.00000000",   
						    "totalMarginBalance": "23.72469206",     
						    "totalPositionInitialMargin": "0.00000000",    
						    "totalOpenOrderInitialMargin": "0.00000000",   
						    "totalCrossWalletBalance": "23.72469206",      
						    "totalCrossUnPnl": "0.00000000",      
						    "availableBalance": "23.72469206",       
						    "maxWithdrawAmount": "23.72469206",     
						    "assets": [
						        {
						            "asset": "USDT",            
						            "walletBalance": "23.72469206",      
						            "unrealizedProfit": "0.00000000",    
						            "marginBalance": "23.72469206",      
						            "maintMargin": "0.00000000",        
						            "initialMargin": "0.00000000",    
						            "positionInitialMargin": "0.00000000",    
						            "openOrderInitialMargin": "0.00000000",   
						            "crossWalletBalance": "23.72469206",      
						            "crossUnPnl": "0.00000000",       
						            "availableBalance": "23.72469206",       
						            "maxWithdrawAmount": "23.72469206",     
						            "marginAvailable": True,    
						            "updateTime": 1625474304765 
						        },
						    ],
						    "positions": [  
						        {
						            "symbol": "BTCUSDT",    
						            "initialMargin": "0",   
						            "maintMargin": "0",     
						            "unrealizedProfit": "0.00000000",  
						            "positionInitialMargin": "0",      
						            "openOrderInitialMargin": "0",     
						            "leverage": "100",      
						            "isolated": True,       
						            "entryPrice": "0.00000",    
						            "maxNotional": "250000",    
						            "bidNotional": "0",  
						            "askNotional": "0",  
						            "positionSide": "BOTH",     
						            "positionAmt": "0",         
						            "updateTime": 0           
						        }
						    ]
						}

		mock_futures_client.account.return_value = expected_resp
		result = binance_api_client.get_perpetual_trading_account_details(symbol = "BTCUSDT")
		mock_futures_client.account.assert_called()
		assert(result == expected_resp["positions"][-1])

	@pytest.mark.skip(reason="Currently not implemented")
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

	@pytest.mark.skip(reason="Currently not implemented")
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

	@pytest.mark.skip(reason="Currently not implemented")
	def test_average_margin_purchase_price_computation_exact_order(self):
		price_qty_pairs_ordered = [[100, 100], [200, 100], [300, 50]]
		size = 250
		assert(self.ftx_client._compute_average_margin_purchase_price(price_qty_pairs_ordered = price_qty_pairs_ordered, size = size) == 180)

	@pytest.mark.skip(reason="Currently not implemented")
	def test_bid_price_default_for_no_bids(self):
		bids 	= []
		size 	= 100
		assert(self.ftx_client._compute_average_bid_price(bids = bids, size = size) == 0)

	@pytest.mark.skip(reason="Currently not implemented")
	def test_prioritization_of_single_highest_bids(self):
		bids 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 50
		assert(self.ftx_client._compute_average_bid_price(bids = bids, size = size) == 500)

	@pytest.mark.skip(reason="Currently not implemented")
	def test_prioritization_of_two_most_highest_bids(self):
		bids 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 100
		assert(self.ftx_client._compute_average_bid_price(bids = bids, size = size) == 400)

	@pytest.mark.skip(reason="Currently not implemented")
	def test_ask_price_default_for_no_asks(self):
		asks 	= []
		size 	= 100
		assert(self.ftx_client._compute_average_ask_price(asks = asks, size = size) == sys.maxsize)

	@pytest.mark.skip(reason="Currently not implemented")
	def test_prioritization_of_single_lowest_asks(self):
		asks 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 50
		assert(self.ftx_client._compute_average_ask_price(asks = asks, size = size) == 100)

	@pytest.mark.skip(reason="Currently not implemented")
	def test_prioritization_of_two_most_lowest_asks(self):
		asks 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 200
		assert(self.ftx_client._compute_average_ask_price(asks = asks, size = size) == 125)

	@pytest.mark.skip(reason="Currently not implemented")
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

	@pytest.mark.skip(reason="Currently not implemented")
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
	
	@pytest.mark.skip(reason="Currently not implemented")
	def test_no_open_perpetual_orders(self):
		ftx_api_client 			= copy.deepcopy(self.ftx_client)

		with patch.object(ftx_api_client, "get_perpetual_open_orders") as mock_get_perpetual_open_orders:
			mock_get_perpetual_open_orders.return_value = []
			result	= ftx_api_client.get_perpetual_most_recent_open_order(symbol = "XRP-PERP")
			assert(result == [])

	@pytest.mark.skip(reason="Currently not implemented")
	def test_fulfilled_perpetual_orders_api_call(self, mock_ftx_client):
		ftx_api_client 			= copy.deepcopy(self.ftx_client)
		ftx_api_client.client 	= mock_ftx_client
		ftx_api_client.get_perpetual_fulfilled_orders(symbol = "XRP-PERP")
		mock_ftx_client.get_order_history.assert_called()

	@pytest.mark.skip(reason="Currently not implemented")
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

	@pytest.mark.skip(reason="Currently not implemented")
	def test_no_fulfilled_perpetual_orders(self):
		ftx_api_client 			= copy.deepcopy(self.ftx_client)

		with patch.object(ftx_api_client, "get_perpetual_fulfilled_orders") as mock_get_perpetual_fulfilled_orders:
			mock_get_perpetual_fulfilled_orders.return_value = []
			result = ftx_api_client.get_perpetual_most_recent_fulfilled_order(symbol = "XRP-USDT")
			assert(result == [])

	@pytest.mark.skip(reason="Currently not implemented")
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

	@pytest.mark.skip(reason="Currently not implemented")
	def test_effective_funding_rate_is_zero_when_flag_is_disabled(self):
		ftx_api_client 			= copy.deepcopy(self.ftx_client)
		ftx_api_client.funding_rate_enable = False

		with patch.object(ftx_api_client, "get_perpetual_funding_rate") as mock_get_perpetual_funding_rate:
			mock_get_perpetual_funding_rate.return_value 	= (-0.02, "2019-03-29T10:00:00+00:00")
			result 	= ftx_api_client.get_perpetual_effective_funding_rate(symbol = "ETH-PERP", seconds_before_current = 300)
			assert result == 0

	@pytest.mark.skip(reason="Currently not implemented")
	@freeze_time("2019-03-29T09:00:00+00:00")
	def test_effective_funding_rate_is_zero_when_invalid_interval(self):
		ftx_api_client 			= copy.deepcopy(self.ftx_client)
		ftx_api_client.funding_rate_enable = True

		with patch.object(ftx_api_client, "get_perpetual_funding_rate") as mock_get_perpetual_funding_rate:
			mock_get_perpetual_funding_rate.return_value 	= (-0.02, "2019-03-29T10:00:00+00:00")
			result 	= ftx_api_client.get_perpetual_effective_funding_rate(symbol = "ETH-PERP", seconds_before_current = 300)
			assert result == 0

	@pytest.mark.skip(reason="Currently not implemented")
	@freeze_time("2019-03-29T09:00:00+00:00")
	def test_effective_funding_rate_is_non_zero(self):
		ftx_api_client 			= copy.deepcopy(self.ftx_client)
		ftx_api_client.funding_rate_enable = True

		with patch.object(ftx_api_client, "get_perpetual_funding_rate") as mock_get_perpetual_funding_rate:
			mock_get_perpetual_funding_rate.return_value 	= (-0.02, "2019-03-29T10:00:00+00:00")
			result 	= ftx_api_client.get_perpetual_effective_funding_rate(symbol = "ETH-PERP", seconds_before_current = 7200)
			assert result == -0.02

	@pytest.mark.skip(reason="Currently not implemented")
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

	@pytest.mark.skip(reason="Currently not implemented")
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

	@pytest.mark.skip(reason="Currently not implemented")
	@patch("ftx.FtxClient")
	def test_get_margin_trading_price(self, mock_ftx_client):
		ftx_api_client = copy.deepcopy(self.ftx_client)
		ftx_api_client.client = mock_ftx_client
		ftx_api_client.get_margin_trading_price(symbol = "BTC/USDT")
		mock_ftx_client.get_market.assert_called_with(market = "BTC/USDT")