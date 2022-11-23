import binance
import copy
import datetime
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

	@patch("binance.client")
	@patch("binance.um_futures")
	def test_perpetual_trading_price_api_call(self, mock_client, mock_futures_client):
		binance_api_client 					= copy.deepcopy(self.binance_client)
		binance_api_client.client 			= mock_client
		binance_api_client.futures_client	= mock_futures_client
		mock_futures_client.ticker_price.return_value = {
														  "symbol": "BTCUSDT",
														  "price": "6000.01",
														  "time": 1589437530011
														}

		result = binance_api_client.get_perpetual_trading_price(symbol = "BTCUSDT")
		mock_futures_client.ticker_price.assert_called_with(symbol = "BTCUSDT")
		assert(result == 6000.01)

	@patch("binance.client")
	@patch("binance.um_futures")
	def test_perpetual_min_lot_size_api_call(self, mock_client, mock_futures_client):
		binance_api_client 					= copy.deepcopy(self.binance_client)
		binance_api_client.client 			= mock_client
		binance_api_client.futures_client	= mock_futures_client
		mock_futures_client.exchange_info.return_value 	= {
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
														            "filters": [{
													                    "filterType": "PRICE_FILTER",
													                    "maxPrice": "300",
													                    "minPrice": "0.0001", 
													                    "tickSize": "0.0001"
													                },
													                {
													                    "filterType": "LOT_SIZE", 
													                    "maxQty": "10000000",
													                    "minQty": "1010",
													                    "stepSize": "1"
													                },
													                {
													                    "filterType": "MARKET_LOT_SIZE",
													                    "maxQty": "590119",
													                    "minQty": "1",
													                    "stepSize": "1"
													                },
													                {
													                    "filterType": "MAX_NUM_ORDERS",
													                    "limit": 200
													                },
													                {
													                    "filterType": "MAX_NUM_ALGO_ORDERS",
													                    "limit": 100
													                },
													                {
													                    "filterType": "MIN_NOTIONAL",
													                    "notional": "1", 
													                },
													                {
													                    "filterType": "PERCENT_PRICE",
													                    "multiplierUp": "1.1500",
													                    "multiplierDown": "0.8500",
													                    "multiplierDecimal": 4
													                }],
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

		result = binance_api_client.get_perpetual_min_lot_size(symbol = "BLZUSDT")
		assert(result == 1010)

	def test_average_margin_purchase_price_computation_exact_order(self):
		price_qty_pairs_ordered = [[100, 100], [200, 100], [300, 50]]
		size = 250
		assert(self.binance_client._compute_average_margin_purchase_price(price_qty_pairs_ordered = price_qty_pairs_ordered, size = size) == 180)

	def test_bid_price_default_for_no_bids(self):
		bids 	= []
		size 	= 100
		assert(self.binance_client._compute_average_bid_price(bids = bids, size = size) == 0)

	def test_prioritization_of_single_highest_bids(self):
		bids 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 50
		assert(self.binance_client._compute_average_bid_price(bids = bids, size = size) == 500)

	def test_prioritization_of_two_most_highest_bids(self):
		bids 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 100
		assert(self.binance_client._compute_average_bid_price(bids = bids, size = size) == 400)

	def test_ask_price_default_for_no_asks(self):
		asks 	= []
		size 	= 100
		assert(self.binance_client._compute_average_ask_price(asks = asks, size = size) == sys.maxsize)

	def test_prioritization_of_single_lowest_asks(self):
		asks 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 50
		assert(self.binance_client._compute_average_ask_price(asks = asks, size = size) == 100)

	def test_prioritization_of_two_most_lowest_asks(self):
		asks 	= [[300, 100], [200, 50], [100, 150], [500, 50]]
		size 	= 200
		assert(self.binance_client._compute_average_ask_price(asks = asks, size = size) == 125)

	@patch("binance.client")
	@patch("binance.um_futures")
	def test_open_perpetual_orders_api_call(self, mock_client, mock_futures_client):
		binance_api_client 					= copy.deepcopy(self.binance_client)
		binance_api_client.client 			= mock_client
		binance_api_client.futures_client	= mock_futures_client

		binance_api_client.get_perpetual_open_orders(symbol = "XRPPERP")
		mock_futures_client.get_orders.assert_called_with(symbol = "XRPPERP")

	def test_most_recent_open_perpetual_order_retrieved(self):
		binance_api_client 		= copy.deepcopy(self.binance_client)
		expected_resp 			= 	[
									  {
									    "avgPrice": "0.00000",
									    "clientOrderId": "abc",
									    "cumQuote": "0",
									    "executedQty": "0",
									    "orderId": 1917641,
									    "origQty": "0.40",
									    "origType": "TRAILING_STOP_MARKET",
									    "price": "0",
									    "reduceOnly": False,
									    "side": "BUY",
									    "positionSide": "SHORT",
									    "status": "NEW",
									    "stopPrice": "9300",                
									    "closePosition": False,   
									    "symbol": "BTCUSDT",
									    "time": 1579276756075,              
									    "timeInForce": "GTC",
									    "type": "TRAILING_STOP_MARKET",
									    "activatePrice": "9020",            
									    "priceRate": "0.3",                 
									    "updateTime": 1579276756075,        
									    "workingType": "CONTRACT_PRICE",
									    "priceProtect": False            
									  },
									  {
									    "avgPrice": "0.00000",
									    "clientOrderId": "abc",
									    "cumQuote": "0",
									    "executedQty": "0",
									    "orderId": 1917641,
									    "origQty": "0.40",
									    "origType": "TRAILING_STOP_MARKET",
									    "price": "0",
									    "reduceOnly": False,
									    "side": "BUY",
									    "positionSide": "SHORT",
									    "status": "NEW",
									    "stopPrice": "9300",                
									    "closePosition": False,   
									    "symbol": "BTCUSDT",
									    "time": 2579276756075,              
									    "timeInForce": "GTC",
									    "type": "TRAILING_STOP_MARKET",
									    "activatePrice": "9020",            
									    "priceRate": "0.3",                 
									    "updateTime": 1579276756075,        
									    "workingType": "CONTRACT_PRICE",
									    "priceProtect": False            
									  }
									]

		with patch.object(binance_api_client, "get_perpetual_open_orders") as mock_get_perpetual_open_orders:
			mock_get_perpetual_open_orders.return_value = expected_resp
			result	= binance_api_client.get_perpetual_most_recent_open_order(symbol = "BTCUSDT")
			assert(result == expected_resp[-1])
	
	def test_no_open_perpetual_orders(self):
		binance_api_client 		= copy.deepcopy(self.binance_client)

		with patch.object(binance_api_client, "get_perpetual_open_orders") as mock_get_perpetual_open_orders:
			mock_get_perpetual_open_orders.return_value = []
			result	= binance_api_client.get_perpetual_most_recent_open_order(symbol = "XRPPERP")
			assert(result == [])

	@patch("binance.client")
	@patch("binance.um_futures")
	def test_fulfilled_perpetual_orders_api_call(self, mock_client, mock_futures_client):
		binance_api_client 					= copy.deepcopy(self.binance_client)
		binance_api_client.client 			= mock_client
		binance_api_client.futures_client	= mock_futures_client

		binance_api_client.get_perpetual_fulfilled_orders(symbol = "XRP-PERP")
		mock_futures_client.get_all_orders.assert_called()

	def test_fulfilled_perpetual_order_retrieved(self):
		binance_api_client 	= copy.deepcopy(self.binance_client)
		mock_orders 		= [
							  	{
								    "avgPrice": "0.00000",
								    "clientOrderId": "abc",
								    "cumQuote": "0",
								    "executedQty": "0",
								    "orderId": 1917641,
								    "origQty": "0.40",
								    "origType": "TRAILING_STOP_MARKET",
								    "price": "0",
								    "reduceOnly": False,
								    "side": "BUY",
								    "positionSide": "SHORT",
								    "status": "NEW",
								    "stopPrice": "9300",               
								    "closePosition": False,  
								    "symbol": "BTCUSDT",
								    "time": 1579276756075,             
								    "timeInForce": "GTC",
								    "type": "TRAILING_STOP_MARKET",
								    "activatePrice": "9020",           
								    "priceRate": "0.3",                
								    "updateTime": 1579276756075,       
								    "workingType": "CONTRACT_PRICE",
								    "priceProtect": False           
							  	},
							  	{
								    "avgPrice": "0.00000",
								    "clientOrderId": "abc",
								    "cumQuote": "0",
								    "executedQty": "0",
								    "orderId": 1917641,
								    "origQty": "0.40",
								    "origType": "TRAILING_STOP_MARKET",
								    "price": "0",
								    "reduceOnly": False,
								    "side": "BUY",
								    "positionSide": "SHORT",
								    "status": "NEW",
								    "stopPrice": "9300",               
								    "closePosition": False,  
								    "symbol": "BTCUSDT",
								    "time": 1679276756075,             
								    "timeInForce": "GTC",
								    "type": "TRAILING_STOP_MARKET",
								    "activatePrice": "9020",           
								    "priceRate": "0.3",                
								    "updateTime": 1579276756075,       
								    "workingType": "CONTRACT_PRICE",
								    "priceProtect": False           
							  	},
							]

		with patch.object(binance_api_client, "get_perpetual_fulfilled_orders") as mock_get_perpetual_fulfilled_orders:
			mock_get_perpetual_fulfilled_orders.return_value = mock_orders
			result = binance_api_client.get_perpetual_most_recent_fulfilled_order(symbol = "XRP-USDT")
			assert(result["time"] == 1679276756075)

	def test_no_fulfilled_perpetual_orders(self):
		binance_api_client 	= copy.deepcopy(self.binance_client)
		with patch.object(binance_api_client, "get_perpetual_fulfilled_orders") as mock_get_perpetual_fulfilled_orders:
			mock_get_perpetual_fulfilled_orders.return_value = []
			result = binance_api_client.get_perpetual_most_recent_fulfilled_order(symbol = "XRP-USDT")
			assert(result == [])

	@patch("binance.client")
	@patch("binance.um_futures")
	def test_get_perpetual_funding_rates(self, mock_client, mock_futures_client):
		binance_api_client 					= copy.deepcopy(self.binance_client)
		binance_api_client.client 			= mock_client
		binance_api_client.futures_client	= mock_futures_client

		mock_futures_client.mark_price.return_value = {
													    "symbol": "BTCUSDT",
													    "markPrice": "11793.63104562",  
													    "indexPrice": "11781.80495970", 
													    "estimatedSettlePrice": "11781.16138815", 
													    "lastFundingRate": "0.00038246",  
													    "nextFundingTime": 1597392000000,
													    "interestRate": "0.00010000",
													    "time": 1597370495002
													}

		(funding_rate, funding_time) = binance_api_client.get_perpetual_funding_rate(symbol = "BTCUSDT")
		assert((funding_rate == 0.00038246) & (funding_time == 1597392000000))

	def test_effective_funding_rate_is_zero_when_flag_is_disabled(self):
		binance_api_client 	= copy.deepcopy(self.binance_client)
		binance_api_client.funding_rate_enable = False

		with patch.object(binance_api_client, "get_perpetual_funding_rate") as mock_get_perpetual_funding_rate:
			mock_get_perpetual_funding_rate.return_value 	= (-0.02, 1597392000000)
			result 	= binance_api_client.get_perpetual_effective_funding_rate(symbol = "BTCUSDT", seconds_before_current = 300)
			assert result == 0

	@freeze_time(datetime.datetime(2020, 8, 14, 7, 50, 0))
	def test_effective_funding_rate_is_zero_when_invalid_interval(self):
		binance_api_client 	= copy.deepcopy(self.binance_client)
		binance_api_client.funding_rate_enable = True

		with patch.object(binance_api_client, "get_perpetual_funding_rate") as mock_get_perpetual_funding_rate:
			mock_get_perpetual_funding_rate.return_value 	= (-0.02, 1597392000000)
			result 	= binance_api_client.get_perpetual_effective_funding_rate(symbol = "BTCUSDT", seconds_before_current = 300)
			assert result == 0

	@freeze_time(datetime.datetime(2020, 8, 14, 7, 50, 0))
	def test_effective_funding_rate_is_non_zero(self):
		binance_api_client 	= copy.deepcopy(self.binance_client)
		binance_api_client.funding_rate_enable = True

		with patch.object(binance_api_client, "get_perpetual_funding_rate") as mock_get_perpetual_funding_rate:
			mock_get_perpetual_funding_rate.return_value 	= (-0.02, 1597392000000)
			result 	= binance_api_client.get_perpetual_effective_funding_rate(symbol = "ETH-PERP", seconds_before_current = 7200)
			assert result == -0.02

	@patch("binance.client")
	@patch("binance.um_futures")
	def test_get_margin_symbols_called(self, mock_client, mock_futures_client):
		binance_api_client 					= copy.deepcopy(self.binance_client)
		binance_api_client.client 			= mock_client
		binance_api_client.futures_client	= mock_futures_client

		mock_client.get_margin_all_pairs.return_value =	[
														    {
														        "base": "BNB",
														        "id": 351637150141315861,
														        "isBuyAllowed": True,
														        "isMarginTrade": True,
														        "isSellAllowed": True,
														        "quote": "BTC",
														        "symbol": "BNBBTC"
														    },
														    {
														        "base": "TRX",
														        "id": 351637923235429141,
														        "isBuyAllowed": True,
														        "isMarginTrade": True,
														        "isSellAllowed": True,
														        "quote": "BTC",
														        "symbol": "TRXBTC"
														    },
														    {
														        "base": "XRP",
														        "id": 351638112213990165,
														        "isBuyAllowed": True,
														        "isMarginTrade": True,
														        "isSellAllowed": True,
														        "quote": "BTC",
														        "symbol": "XRPBTC"
														    },
														]
		result = binance_api_client.get_margin_symbols()
		mock_client.get_margin_all_pairs.assert_called() 
		assert(result == ["BNBBTC", "TRXBTC", "XRPBTC"])

	@patch("binance.client")
	@patch("binance.um_futures")
	def test_get_margin_trading_account_details(self, mock_client, mock_futures_client):
		binance_api_client 					= copy.deepcopy(self.binance_client)
		binance_api_client.client 			= mock_client
		binance_api_client.futures_client	= mock_futures_client

		mock_client.get_margin_account.return_value = 	{
													      "borrowEnabled": True,
													      "marginLevel": "11.64405625",
													      "totalAssetOfBtc": "6.82728457",
													      "totalLiabilityOfBtc": "0.58633215",
													      "totalNetAssetOfBtc": "6.24095242",
													      "tradeEnabled": True,
													      "transferEnabled": True,
													      "userAssets": [
													          {
													              "asset": "BTC",
													              "borrowed": "0.00000000",
													              "free": "0.00499500",
													              "interest": "0.00000000",
													              "locked": "0.00000000",
													              "netAsset": "0.00499500"
													          },
													          {
													              "asset": "BNB",
													              "borrowed": "201.66666672",
													              "free": "2346.50000000",
													              "interest": "0.00000000",
													              "locked": "0.00000000",
													              "netAsset": "2144.83333328"
													          },
													          {
													              "asset": "ETH",
													              "borrowed": "0.00000000",
													              "free": "0.00000000",
													              "interest": "0.00000000",
													              "locked": "0.00000000",
													              "netAsset": "0.00000000"
													          },
													          {
													              "asset": "USDT",
													              "borrowed": "0.00000000",
													              "free": "0.00000000",
													              "interest": "0.00000000",
													              "locked": "0.00000000",
													              "netAsset": "0.00000000"
													          }
													      	]
														}

		result 	= binance_api_client.get_margin_trading_account_details(currency = "BNB")
		mock_client.get_margin_account.assert_called()
		assert(result == 2144.83333328)

	@patch("binance.client")
	@patch("binance.um_futures")
	def test_get_margin_trading_price(self, mock_client, mock_futures_client):
		binance_api_client 					= copy.deepcopy(self.binance_client)
		binance_api_client.client 			= mock_client
		binance_api_client.futures_client	= mock_futures_client
		binance_api_client.get_margin_trading_price(symbol = "BTCUSDT")
		mock_client.get_avg_price.assert_called_with(symbol = "BTCUSDT")