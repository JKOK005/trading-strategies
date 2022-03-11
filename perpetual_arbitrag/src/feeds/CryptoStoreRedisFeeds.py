import json
import redis
from datetime import datetime, timedelta, timezone
from feeds.PriceFeeds import PriceFeeds

class CryptoStoreRedisFeeds(PriceFeeds):
	"""
	Class reads real time feeds from Crypto Store (ref: https://github.com/bmoscon/cryptostore).
	Realtime feeds are expected to be stored in Redis.
	"""
	redis_cli 	= None

	def __init__(self, 	redis_url: str, 
						redis_port: int, 
						*args, **kwargs):
		super(self, CryptoStoreRedisFeeds).__init__(*args, **kwargs)
		self.redis_cli = redis.Redis(host = redis_url, port = redis_port)
		return

	def symbol_to_key_mapping(self, symbol: str, exchange: str):
		new_symbol = symbol
		if exchange.lower() == "okx" and "swap" in symbol.lower():
			# OKX symbols are denoted by SWAP but crypto store uses PERP
			new_symbol = new_symbol.replace("SWAP", "PERP").replace("swap", "PERP")
		return new_symbol

	def order_book_relevance(self, order_book, latency_s: int):
		"""
		Asserts if order_book is within latency ms from current time
		"""
		order_book_dt 	= datetime.utcfromtimestamp(order_book["updated"])
		now_dt 			= datetime.utcnow()
		return now_dt - order_book_dt <= timedelta(seconds = latency_s)

	def sorted_order_book(self, symbol: str, exchange: str, *args, **kwargs):
		new_symbol 	= self.symbol_to_key_mapping(symbol = symbol, exchange = exchange)
		redis_key 	= f"book-{exchange}-{new_symbol}" 		# Exchange and symbols are all UPPER case
		resp 		= self.redis_cli.zrange(redis_key, -1, -1)[0]
		resp_dict 	= json.loads(resp)
		bids 		= [(k, v) for (k, v) in resp_dict["book"]["bid"].items()]
		asks 		= [(k, v) for (k, v) in resp_dict["book"]["ask"].items()]
		timestamp 	= resp_dict["timestamp"]
		return {"bids" : bids, "asks" : asks, "updated" : timestamp}