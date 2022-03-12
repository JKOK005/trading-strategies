import asyncio
import base64
import datetime
import json
import hashlib
import hmac
import logging
import sys
import websockets
from datetime import timedelta
from clients.ExchangeSpotClients import ExchangeSpotClients
from clients.ExchangePerpetualClients import ExchangePerpetualClients

class OkxApiClientV2(ExchangeSpotClients, ExchangePerpetualClients):

	ws_private_url 	= "wss://ws.okx.com:8443/ws/v5/private"
	logger 			= logging.getLogger('OkxApiClientV2')

	def __init__(self,	api_key: str,
						api_secret_key: str,
						passphrase: str,
						feed_client,
						funding_rate_enable: bool,
						is_simulated: bool = False,
				):
		self.feed_client = feed_client
		self.is_simulated = is_simulated
		self.funding_rate_enable = funding_rate_enable
		self.ws_private_client = self._login(api_key = api_key, passphrase = passphrase)
		return

	def __del__(self):
		self.ws_private_client.close()

	def _login(self, api_key: str, passphrase: str, api_secret_key: str):
		epoch_ts 		= datetime.datetime.utcnow().total_seconds()
		login_payload 	= 	{	
								"op" 	: "login",
								"args" 	: [
									{
								      "apiKey": api_key,
								      "passphrase": passphrase,
								      "timestamp": current_time,
								      "sign": self._create_sign(timestamp = epoch_ts, key_secret = api_secret_key).decode("utf-8")
								    }
								]
							}

		ws_private_client = websockets.connect(self.ws_private_url)
		await ws_private_client.send(json.dumps(login_payload))
		return ws_private_client

 	def _create_sign(self, timestamp: str, key_secret: str):
        message = timestamp + 'GET' + '/users/self/verify'
        mac = hmac.new(bytes(key_secret, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
        d 	= mac.digest()
        sign = base64.b64encode(d)
        return sign

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
		if len(bids) > 0:
			return self._compute_average_margin_purchase_price(price_qty_pairs_ordered = bids, size = size)
		return 0

	def _compute_average_ask_price(self, asks: [[float, float]], size: float):
		# Buy into asks starting from the lowest to the highest.
		if len(asks) > 0:
			return self._compute_average_margin_purchase_price(price_qty_pairs_ordered = asks, size = size)
		return sys.maxsize

	def get_spot_trading_account_details(self, currency: str):
		"""
		Retrieves spot trading details
		"""
		pass

	def get_spot_trading_price(self, symbol: str):
		"""
		Retrieves current spot pricing for trading symbol
		"""
		pass

	def get_spot_min_volume(self, symbol: str):
		"""
		Retrieves minimum order volume for spot trading symbol
		"""
		pass

	def get_spot_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the spot asset, assuming that we intend to trade at a given volume. 
		"""
		order_book 			= self.feed_client.sorted_order_book(exchange = "OKX", symbol = symbol)
		bids 				= order_book["bids"]
		average_bid_price 	= self._compute_average_bid_price(bids = bids, size = size)
		asks 				= order_book["asks"]
		average_ask_price 	= self._compute_average_ask_price(asks = asks, size = size)
		return (average_bid_price, average_ask_price)

	def get_spot_open_orders(self, symbol: str):
		"""
		Gets information of all open spot orders by the user
		"""
		pass

	def get_spot_most_recent_open_order(self, symbol: str):
		"""
		Gets the most recent open orders for spot
		"""
		pass

	def get_spot_fulfilled_orders(self, symbol: str):
		"""
		Gets information for all fulfilled spot orders by the user
		"""
		pass

	def get_spot_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent spot trade that have been fulfilled
		"""
		pass

	def place_spot_order(self, *args, **kwargs):
		pass

	def revert_spot_order(self, order_resp, *args, **kwargs):
		pass

	def assert_spot_resp_error(self, order_resp):
		"""
		Function looks at an order response created after placing an order and decides if we should raise an error.

		A raised error indicates a failed order attempt.
		"""
		pass

	def get_perpetual_trading_account_details(self, currency: str):
		"""
		Retrieves perpetual trading account details
		"""
		pass

	def get_perpetual_trading_price(self, symbol: str):
		"""
		Retrieves current perpetual price for trading symbol
		"""
		pass

	def get_perpetual_min_lot_size(self, symbol: str):
		"""
		Retrieves minimum order lot size for perpetual trading symbol
		"""
		pass

	def get_perpetual_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the perpetual asset, assuming that we intend to trade at a given lot size. 
		"""
		order_book 			= self.feed_client.sorted_order_book(exchange = "OKX", symbol = symbol)
		bids 				= order_book["bids"]
		average_bid_price 	= self._compute_average_bid_price(bids = bids, size = size)
		asks 				= order_book["asks"]
		average_ask_price 	= self._compute_average_ask_price(asks = asks, size = size)
		return (average_bid_price, average_ask_price)

	def get_perpetual_open_orders(self, symbol: str):
		"""
		Gets information of all open perpetual orders by the user
		"""
		pass

	def get_perpetual_most_recent_open_order(self, symbol: str):
		"""
		Gets the most recent open orders for perpetual
		"""
		pass

	def get_perpetual_fulfilled_orders(self, symbol: str):
		"""
		Gets information of all fulfilled perpetual orders by the user
		"""
		pass

	def get_perpetual_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent perpetual trade that have been fulfilled
		"""
		pass

	def get_perpetual_effective_funding_rate(self, symbol: str, seconds_before_current: int, seconds_before_estimated: int):
		"""
		Gets the effective funding rate for perpetual contract.

		Effective funding rate takes into account a variety of factors to decide on the funding rate.
		"""
		pass

	def place_perpetual_order(self, *args, **kwargs):
		pass

	def revert_perpetual_order(self, order_resp, *args, **kwargs):
		pass

	def assert_perpetual_resp_error(self, order_resp):
		"""
		Function looks at an order response created after placing an order and decides if we should raise an error.

		A raised error indicates a failed order attempt.
		"""
		pass