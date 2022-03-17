import json
import logging
import redis
from datetime import datetime, timedelta
from feeds.PriceFeeds import PriceFeeds
from functools import wraps

def assert_latency(func):
	"""
	Asserts if response is within latency ms from current time.
	response needs an `updated` field denoting the latest time of the information.
	"""
	@wraps(func)
	def wrapper(*args, **kwargs):
		resp 	= func(*args, **kwargs)
		resp_df = datetime.utcfromtimestamp(resp["updated"])
		assert datetime.utcnow() - resp_df <= timedelta(milliseconds = args[0].permissible_latency_s * 1000), "latency too large"
		return resp
	return wrapper

class CryptoStoreRedisFeeds(PriceFeeds):
	"""
	Class reads real time feeds from Crypto Store (ref: https://github.com/bmoscon/cryptostore).
	Realtime feeds are expected to be stored in Redis.
	"""
	redis_cli = None
	permissible_latency_s = 0
	logger = logging.getLogger('CryptoStoreRedisFeeds')

	def __init__(self, 	redis_url: str, 
						redis_port: int,
						permissible_latency_s: float,
						*args, **kwargs):

		super(CryptoStoreRedisFeeds, self).__init__(*args, **kwargs)
		self.redis_url = redis_url
		self.redis_port = redis_port
		self.permissible_latency_s = permissible_latency_s
		return

	def connect(self):
		self.logger.debug(f"Connecting to redis at {self.redis_url}:{self.redis_port}")
		self.redis_cli = redis.Redis(host = self.redis_url, port = self.redis_port)
		return self

	def symbol_to_key_mapping(self, symbol: str, exchange: str):
		new_symbol = symbol
		if exchange.lower() == "okx" and "swap" in symbol.lower():
			# OKX symbols are denoted by SWAP but crypto store uses PERP
			new_symbol = new_symbol.replace("SWAP", "PERP").replace("swap", "PERP")
		return new_symbol
			
	@assert_latency
	def sorted_order_book(self, symbol: str, exchange: str, *args, **kwargs):
		new_symbol 	= self.symbol_to_key_mapping(symbol = symbol, exchange = exchange)
		redis_key 	= f"book-{exchange}-{new_symbol}" 		# Exchange and symbols are all UPPER case
		resp 		= self.redis_cli.zrange(redis_key, -1, -1)[0]
		resp_dict 	= json.loads(resp)
		bids 		= [(float(k), float(v)) for (k, v) in resp_dict["book"]["bid"].items()]
		asks 		= [(float(k), float(v)) for (k, v) in resp_dict["book"]["ask"].items()]
		timestamp 	= resp_dict["timestamp"]
		return {"bids" : bids, "asks" : asks, "updated" : timestamp}