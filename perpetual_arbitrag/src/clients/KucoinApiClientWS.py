import asyncio
import base64
import json
import hashlib
import hmac
import logging
import websockets
from datetime import datetime
from clients.KucoinApiClient import KucoinApiClient

class KucoinApiClientWS(KucoinApiClient):
	logger 				= logging.getLogger('KucoinApiClientWS')

	def __init__(self, feed_client, *args, **kwargs):
		super(KucoinApiClientWS, self).__init__(*args, **kwargs)
		self.feed_client = feed_client
		return

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

	def get_futures_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the perpetual asset, assuming that we intend to trade at a given lot size. 
		"""
		order_book 			= self.feed_client.sorted_order_book(exchange = "OKX", symbol = symbol)
		bids 				= order_book["bids"]
		average_bid_price 	= self._compute_average_bid_price(bids = bids, size = size)
		asks 				= order_book["asks"]
		average_ask_price 	= self._compute_average_ask_price(asks = asks, size = size)
		return (average_bid_price, average_ask_price)