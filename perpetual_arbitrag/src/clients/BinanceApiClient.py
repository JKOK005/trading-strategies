import asyncio
import datetime
import logging
import sys
import time
from binance.client import Client
from binance.um_futures import UMFutures
from datetime import timedelta
from clients.ExchangePerpetualClients import ExchangePerpetualClients
from clients.ExchangeMarginClients import ExchangeMarginClients

class BinanceApiClient(ExchangeMarginClients, ExchangePerpetualClients):
	client 	= None
	logger 	= logging.getLogger('BinanceApiClient')

	def __init__(self, 	api_key: str, 
						api_secret_key: str,
						funding_rate_enable: bool,
				):
		self.client 				= Client(api_key = api_key, api_secret = api_secret_key)	# For spot / margin
		self.futures_client 		= UMFutures(key = api_key, secret = api_secret_key) 		# For perpetual
		self.api_key 				= api_key
		self.api_secret_key 		= api_secret_key
		self.funding_rate_enable 	= funding_rate_enable
		self.logger.info(f"Enable for funding rate computation set to {funding_rate_enable}")
		return

	def _compute_average_margin_purchase_price(self, price_qty_pairs_ordered: [float, float], size: float):
		"""
		We will read pricing - qty data from the first entry of the list. 

		This logic will differ, depending on whether we want to go long / short on the asset. 
		As such, the ordering of the price-qty pairs in the list has to be handled properly by the user. 
		"""
		all_trade_qty 		= size
		trade_amt 			= 0
		executed_trade_qty 	= 0
		for each_price_qty_pairs in price_qty_pairs_ordered:
			if all_trade_qty < 0:
				break
			else:
				[price, qty] 	=  each_price_qty_pairs
				trade_qty 		=  min(all_trade_qty, qty)
				trade_amt 	 	+= price * trade_qty
				all_trade_qty 	-= trade_qty
				executed_trade_qty += trade_qty
		return trade_amt / executed_trade_qty

	def _compute_average_bid_price(self, bids: [[float, float]], size: float):
		# Sell into bids starting from the highest to the lowest.
		_bids 	= sorted(bids, key = lambda x: x[0], reverse = True)
		if len(_bids) > 0:
			return self._compute_average_margin_purchase_price(price_qty_pairs_ordered = _bids, size = size)
		return 0

	def _compute_average_ask_price(self, asks: [[float, float]], size: float):
		# Buy into asks starting from the lowest to the highest.
		_asks 	= sorted(asks, key = lambda x: x[0], reverse = False)
		if len(_asks) > 0:
			return self._compute_average_margin_purchase_price(price_qty_pairs_ordered = _asks, size = size)
		return sys.maxsize

	def set_perpetual_leverage(self, symbol: str, leverage: int):
		self.logger.debug(f"Set leverage of {symbol} to {leverage}")
		self.futures_client.change_leverage(symbol = symbol, leverage = leverage)
		return

	def get_perpetual_symbols(self):
		"""
		Fetches all perpetual instrument symbols
		"""
		resp 	= self.futures_client.exchange_info()
		perps 	= filter(lambda x: x["contractType"] == "PERPETUAL", resp["symbols"])
		return list(map(lambda x: x["symbol"], perps))

	def get_perpetual_trading_account_details(self, symbol: str):
		"""
		Retrieves perpetual trading account details
		"""
		resp = self.futures_client.account()
		relevant_asset_position = next(filter(lambda x: x["symbol"] == symbol, resp["positions"]))
		return relevant_asset_position

	def get_perpetual_trading_price(self, symbol: str):
		"""
		Retrieves current perpetual price for trading symbol
		"""
		resp = self.futures_client.ticker_price(symbol = symbol)
		return float(resp["price"])

	def get_perpetual_min_lot_size(self, symbol: str):
		"""
		Retrieves minimum order lot size for perpetual trading symbol
		"""
		resp 					= self.futures_client.exchange_info()
		relevant_asset_position = next(filter(lambda x: x["contractType"] == "PERPETUAL" and x["symbol"] == symbol, resp["symbols"]))
		min_qty_details 		= next(filter(lambda x: x["filterType"] == "LOT_SIZE", relevant_asset_position["filters"]))
		return int(min_qty_details["minQty"])

	def get_perpetual_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the perpetual asset, assuming that we intend to trade at a given lot size. 
		"""
		bid_ask_resp 		= self.futures_client.depth(market = symbol, limit = 50)
		
		bids 				= bid_ask_orders["bids"]
		average_bid_price 	= self._compute_average_bid_price(bids = bids, size = size)

		asks 				= bid_ask_orders["asks"]
		average_sell_price 	= self._compute_average_ask_price(asks = asks, size = size)		
		return (average_bid_price, average_sell_price)

	def get_perpetual_open_orders(self, symbol: str):
		"""
		Gets information of all open perpetual orders by the user
		"""
		open_orders = self.futures_client.get_orders(symbol = symbol)
		return open_orders

	def get_perpetual_most_recent_open_order(self, symbol: str):
		"""
		Gets the most recent open orders for perpetual
		"""
		open_orders 			= self.get_perpetual_open_orders(market = symbol)
		sorted_orders 			= sorted(open_orders, key = lambda d: d['time'], reverse = True)
		most_recent_open_order 	= sorted_orders[0] if len(sorted_orders) > 0 else sorted_orders
		return most_recent_open_order

	def get_perpetual_fulfilled_orders(self, symbol: str):
		"""
		Gets information of all fulfilled perpetual orders by the user
		"""
		return self.futures_client.get_all_orders(symbol = symbol)

	def get_perpetual_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent perpetual trade that have been fulfilled
		"""
		fulfilled_orders 			= self.get_perpetual_fulfilled_orders(symbol = symbol)
		sorted_orders 				= sorted(fulfilled_orders, key = lambda d: d['time'], reverse = True)
		most_recent_fulfilled_order = sorted_orders[0] if len(sorted_orders) > 0 else sorted_orders
		return most_recent_fulfilled_order

	def get_perpetual_funding_rate(self, symbol: str):
		"""
		Gets the immediate and predicted funding rate for futures contract
		"""
		funding_rate_resp = self.futures_client.mark_price(symbol = symbol)
		return float(funding_rate_resp["lastFundingRate"]), funding_rate_resp["nextFundingTime"]

	def get_perpetual_effective_funding_rate(self, symbol: str, seconds_before_current: int):
		"""
		Gets the effective funding rate for perpetual contract.

		Effective funding rate takes into account a variety of factors to decide on the funding rate.

		1) If we are not within a valid funding interval, then the funding rates are 0.
		2) If we are within the valid funding interval, then the funding rate is non-zero.
		3) If funding rate computation has been disabled, then all rates are 0.
		"""
		current_time 					= datetime.datetime.utcnow()
		funding_rate, next_funding_time = self.get_perpetual_funding_rate(symbol = symbol)
		next_funding_time 				= datetime.datetime.utcfromtimestamp(next_funding_time / 1000)
		return funding_rate if (next_funding_time - timedelta(seconds = seconds_before_current) <= current_time) and \
								self.funding_rate_enable \
							else 0

	def place_perpetual_order(self, *args, **kwargs):
		# Unimplemented as we will be using WS client for trades
		raise Exception("Function <place_perpetual_order> should not be invoked on REST client")

	def revert_perpetual_order(self, order_resp, *args, **kwargs):
		# Unimplemented as we will be using WS client for trades
		raise Exception("Function <revert_perpetual_order> should not be invoked on REST client")

	def assert_perpetual_resp_error(self, order_resp):
		resp  			= order_resp["resp"]
		order_resp_code = resp.status
		if order_resp_code != "200":
			raise Exception(f"Perpetual order failed: {resp}")
		return

	def set_margin_leverage(self, symbol: str, leverage: int):
		self.logger.debug(f"Set leverage of {symbol} to {leverage}")
		self.client.futures_change_leverage(symbol = symbol, leverage = leverage, timestamp = time.time())
		return

	def get_margin_symbols(self):
		resp 	= self.client.get_margin_all_pairs()
		return list(map(lambda x: x["symbol"], resp))

	def get_margin_trading_account_details(self, currency: str):
		resp 	= self.client.get_margin_account()
		relevant_asset_position = next(filter(lambda x: x["asset"] == currency, resp["userAssets"]))
		return float(relevant_asset_position["netAsset"])

	def get_margin_trading_price(self, symbol: str):
		resp = self.client.get_avg_price(symbol = symbol)
		return float(resp["price"])

	def get_margin_min_volume(self, currency: str):
		# TODO: Check if this is the correct way to get min borrow amount, because most results are 0.
		resp = self.client.get_margin_all_assets()
		relevant_asset = next(filter(lambda x: x["assetName"] == currency, resp))
		return relevant_asset["userMinBorrow"]

	def get_margin_average_bid_ask_price(self, symbol: str, size: float):
		bid_ask_resp 		= self.client.get_order_book(symbol = symbol, limit = 50)
		
		bids 				= bid_ask_orders["bids"]
		average_bid_price 	= self._compute_average_bid_price(bids = bids, size = size)

		asks 				= bid_ask_orders["asks"]
		average_sell_price 	= self._compute_average_ask_price(asks = asks, size = size)		
		return (average_bid_price, average_sell_price)

	def get_margin_open_orders(self, symbol: str):
		open_orders = self.client.get_open_margin_orders(symbol = symbol)
		return open_orders

	def get_margin_most_recent_open_order(self, symbol: str):
		open_orders 	= self.get_margin_open_orders(symbol = symbol)
		sorted_orders 	= sorted(open_orders, key = lambda d: d['time'], reverse = True) 
		most_recent_open_order = sorted_orders[0] if len(sorted_orders) > 0 else sorted_orders
		return most_recent_open_order

	def get_margin_fulfilled_orders(self, symbol: str):
		order_history 		= self.client.get_all_margin_orders(market = symbol)
		fulfilled_orders 	= list(filter(lambda x: x["status"] == "FILLED", order_history))
		return fulfilled_orders

	def get_margin_most_recent_fulfilled_order(self, symbol: str):
		fulfilled_orders 			= self.get_margin_fulfilled_orders(symbol = symbol)
		sorted_orders 				= sorted(fulfilled_orders, key = lambda d: d['time'], reverse = True)
		most_recent_fulfilled_order = sorted_orders[0] if len(sorted_orders) > 0 else sorted_orders
		return most_recent_fulfilled_order

	def _compounded_interest_rate(self, interest: float, cycles: int):
		return (1 + interest) ** cycles - 1

	def get_margin_effective_funding_rate(self, ccy: str, loan_period_hrs: int):
		funding_rate = 0
		if self.funding_rate_enable:
			interest_rate_resp 	= self.client.get_cross_margin_data(coin = ccy)[0]
			hourly_interest 	= interest_rate_resp["dailyInterest"] / 24
			funding_rate 		= self._compounded_interest_rate(interest = hourly_interest, cycles = loan_period_hrs)
		return funding_rate

	def place_margin_order(self, *args, **kwargs):
		# Unimplemented as we will be using WS client for trades
		raise Exception("Function <place_margin_order> should not be invoked on REST client")

	def revert_margin_order(self, order_resp, *args, **kwargs):
		# Unimplemented as we will be using WS client for trades
		raise Exception("Function <revert_margin_order> should not be invoked on REST client")

	def assert_margin_resp_error(self, order_resp):
		resp  			= order_resp["resp"]
		order_resp_code = resp.status
		if order_resp_code != "200":
			raise Exception(f"Margin order failed: {resp}")
		return