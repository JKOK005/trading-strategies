import asyncio
import json
import hmac
import logging
import time
import websockets
from clients.FtxApiClient import FtxApiClient
from deprecated import deprecated

@deprecated("Deprecate class as FTX WS does not support placing trades via WS")
class FtxApiClientWS(FtxApiClient):
	ws_private_client 	= None
	ws_private_url 		= "wss://ftx.com/ws/"
	logger 				= logging.getLogger("FtxApiClientWS")

	def __init__(self, feed_client, *args, **kwargs):
		super(FtxApiClientWS, self).__init__(*args, **kwargs)
		self.feed_client = feed_client
		return

	def _create_sign(self, timestamp: int, key_secret: str):
		sign = hmac.new(key_secret.encode(), f'{timestamp}websocket_login'.encode(), digestmod='sha256').hexdigest()
		return sign

	async def _connect(self):
		self.ws_private_client = await self._login(api_key = self.api_key, api_secret_key = self.api_secret_key)
		return

	def _login(self, api_key: str, api_secret_key: str):
		epoch_ts 		= 	int(time.time() * 1000)
		login_payload 	= 	{	
								"op" 	: 	"login",
								"args" 	: 	{
										      "key": api_key,
										      "sign": self._create_sign(timestamp = epoch_ts, key_secret = api_secret_key),
										      "time": epoch_ts,
										    }
							}

		ws_private_client = await websockets.connect(self.ws_private_url)
		await ws_private_client.send(json.dumps(login_payload))
		signed_resp = await ws_private_client.recv()

		if json.loads(signed_resp)["event"] == "error":
			raise Exception(signed_resp)
		else:
			return ws_private_client

	def make_connection(self):
		asyncio.get_event_loop().run_until_complete(self._connect())
		return

	def get_spot_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the spot asset, assuming that we intend to trade at a given volume. 
		"""
		order_book 			= self.feed_client.sorted_order_book(exchange = "FTX", symbol = symbol)
		bids 				= order_book["bids"]
		average_bid_price 	= self._compute_average_bid_price(bids = bids, size = size)
		asks 				= order_book["asks"]
		average_ask_price 	= self._compute_average_ask_price(asks = asks, size = size)
		updated_ts 			= order_book["updated"]
		return (average_bid_price, average_ask_price, updated_ts)

	def _frame_spot_order(self, symbol: str, 
								order_type: str, 
								order_side: str, 
								price: float,
								size: float,
								target_currency: str):
		args = {
			"instId" 	: symbol,
			"tdMode" 	: "cash",
			"side" 		: order_side,
			"ordType" 	: order_type,
			"sz" 		: size,
			"tgtCcy" 	: target_currency
		}

		args["px"] = price if order_type == "limit" else None

		order = {
			"id" 	: f"SPOT{order_side}",
			"op" 	: "order",
			"args" 	: [args]
		}

		return order