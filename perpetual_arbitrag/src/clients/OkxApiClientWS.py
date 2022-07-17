import asyncio
import base64
import json
import hashlib
import hmac
import logging
import websockets
from datetime import datetime
from clients.OkxApiClient import OkxApiClient

class OkxApiClientWS(OkxApiClient):
	ws_private_client 	= None
	ws_private_url 		= "wss://ws.okx.com:8443/ws/v5/private"
	logger 				= logging.getLogger('OkxApiClientV2')

	def __init__(self, feed_client, *args, **kwargs):
		super(OkxApiClientWS, self).__init__(*args, **kwargs)
		self.feed_client = feed_client
		return

	async def _connect(self):
		self.ws_private_client = await self._login(api_key = self.api_key, api_secret_key = self.api_secret_key, passphrase = self.passphrase)
		return

	async def _maintain(self):
		await self.ws_private_client.send("ping")
		resp = await self.ws_private_client.recv()
		self.logger.debug(f"Ping server with resp: {resp}")
		return
					
	async def _login(self, api_key: str, api_secret_key: str, passphrase: str):
		epoch_ts 		= int(datetime.now().timestamp())
		login_payload 	= 	{	
								"op" 	: "login",
								"args" 	: [
									{
								      "apiKey": api_key,
								      "passphrase": passphrase,
								      "timestamp": epoch_ts,
								      "sign": self._create_sign(timestamp = epoch_ts, key_secret = api_secret_key).decode("utf-8")
								    }
								]
							}

		ws_private_client = await websockets.connect(self.ws_private_url)
		await ws_private_client.send(json.dumps(login_payload))
		signed_resp = await ws_private_client.recv()
		
		if json.loads(signed_resp)["event"] == "error":
			raise Exception(signed_resp)
		else:
			return ws_private_client

	async def _place_order_async(self, order: dict):
		await self.ws_private_client.send(json.dumps(order))
		signed_resp = await self.ws_private_client.recv()
		return json.loads(signed_resp)

	def _create_sign(self, timestamp: int, key_secret: str):
		message = f"{timestamp}" + 'GET' + '/users/self/verify'
		mac = hmac.new(bytes(key_secret, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
		d 	= mac.digest()
		sign = base64.b64encode(d)
		return sign

	def make_connection(self):
		asyncio.get_event_loop().run_until_complete(self._connect())
		return

	def maintain_connection(self):
		asyncio.get_event_loop().run_until_complete(self._maintain())
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
			"id" 	: f"SPOT-{symbol}-{order_side}",
			"op" 	: "order",
			"args" 	: [args]
		}

		return order

	async def place_spot_order_async(self, 	symbol: str, 
											order_type: str, 
											order_side: str, 
											price: float,
											size: float,
											target_currency: str,
											*args, **kwargs):

		order = self._frame_spot_order(	symbol = symbol,
										order_type = order_type,
										order_side = order_side,
										price = price,
										size = size,
										target_currency = target_currency
									)
		await self.ws_private_client.send(json.dumps(order))
		return self.ws_private_client.recv()
		# return await self._place_order_async(order = order)


	def place_spot_order(self, 	symbol: str, 
								order_type: str, 
								order_side: str, 
								price: float,
								size: float,
								target_currency: str,
								*args, **kwargs):

		order = self._frame_spot_order(	symbol = symbol,
										order_type = order_type,
										order_side = order_side,
										price = price,
										size = size,
										target_currency = target_currency
									)
		return asyncio.get_event_loop().run_until_complete(self._place_order_async(order = order))

	def assert_spot_resp_error(self, order_resp):
		"""
		Function looks at an order response created after placing an order and decides if we should raise an error.

		A raised error indicates a failed order attempt.
		Websocket failed error codes can be referred to here: https://www.okex.com/docs-v5/en/#error-code-websocket-public
		"""
		order_resp_code = order_resp["code"]
		if order_resp_code != "0":
			raise Exception(f"Spot order failed: {order_resp}")
		return

	async def revert_spot_order_async(self, order_resp, revert_params):
		self.logger.debug(f"Reverting spot order")
		return await self.place_spot_order_async(**revert_params)

	def get_perpetual_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the perpetual asset, assuming that we intend to trade at a given lot size. 
		"""
		order_book 			= self.feed_client.sorted_order_book(exchange = "OKX", symbol = symbol)
		bids 				= order_book["bids"]
		average_bid_price 	= self._compute_average_bid_price(bids = bids, size = size)
		asks 				= order_book["asks"]
		average_ask_price 	= self._compute_average_ask_price(asks = asks, size = size)
		updated_ts 			= order_book["updated"]
		return (average_bid_price, average_ask_price, updated_ts)

	def _frame_perpetual_order(self, symbol: str, 
									 position_side: str, 
									 order_type: str, 
									 order_side: str,
									 price: float,
									 size: int):
		order 	= {
			"id" 	: f"PERP-{symbol}-{order_side}",
			"op" 	: "order",
			"args" 	: [
				{
					"instId" 	 : symbol,
					"tdMode" 	 : "cross",
					"posSide" 	 : position_side,
					"side" 		 : order_side,
					"ordType" 	 : order_type,
					"sz" 		 : size,
					"px" 		 : str(price),
					"reduceOnly" : True
				}
			]
		}
		return order

	async def place_perpetual_order_async(self, symbol: str, 
												position_side: str, 
												order_type: str, 
												order_side: str,
												price: float,
												size: int,
												*args, **kwargs):

		order 	= self._frame_perpetual_order(	symbol = symbol,
												position_side = position_side, 
												order_type = order_type,
												order_side = order_side,
												price = price, 
												size = size
											)
		await self.ws_private_client.send(json.dumps(order))
		return self.ws_private_client.recv()
		# return await self._place_order_async(order = order)

	def place_perpetual_order(self, symbol: str, 
									position_side: str, 
									order_type: str, 
									order_side: str,
									price: float,
									size: int,
									*args, **kwargs):

		order 	= self._frame_perpetual_order(	symbol = symbol,
												position_side = position_side, 
												order_type = order_type,
												order_side = order_side,
												price = price, 
												size = size
											)
		return asyncio.get_event_loop().run_until_complete(self._place_order_async(order = order))

	def assert_perpetual_resp_error(self, order_resp):
		"""
		Function looks at an order response created after placing an order and decides if we should raise an error.

		A raised error indicates a failed order attempt.
		Websocket failed error codes can be referred to here: https://www.okex.com/docs-v5/en/#error-code-websocket-public
		"""
		order_resp_code = order_resp["code"]
		if order_resp_code != "0":
			raise Exception(f"Perpetual order failed: {order_resp}")
		return

	async def revert_perpetual_order_async(self, order_resp, revert_params):
		self.logger.debug(f"Reverting perpetual order")
		return await self.place_perpetual_order_async(**revert_params)

	def get_margin_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the perpetual asset, assuming that we intend to trade at a given lot size. 
		"""
		return self.get_spot_average_bid_ask_price(symbol = symbol, size = size)

	def _frame_margin_order(self, symbol: str,
								  ccy: str,
								  trade_mode: str, 
								  order_type: str, 
								  order_side: str, 
								  price: int,
								  size: float):
		order 	= {
			"id" 	: f"MARGIN-{symbol}-{order_side}",
			"op" 	: "order",
			"args" 	: [
				{
					"instId" 	 : symbol,
					"ccy" 		 : ccy,
					"tdMode" 	 : trade_mode,
					"side" 		 : order_side,
					"ordType" 	 : order_type,
					"sz" 		 : size,
					"px" 		 : str(price),
					"reduceOnly" : False
				}
			]
		}
		return order

	async def place_margin_order_async(self, symbol: str,
											 ccy: str,
											 trade_mode: str, 
											 order_type: str, 
											 order_side: str, 
											 price: int,
											 size: float,
											 *args, **kwargs):

		order 	= self._frame_margin_order(	symbol = symbol,
											ccy = ccy,
											trade_mode = trade_mode,
											order_type = order_type,
											order_side = order_side,
											price = price,
											size = size
										)
		await self.ws_private_client.send(json.dumps(order))
		return self.ws_private_client.recv()

	def place_margin_order(self, symbol: str,
								 ccy: str,
								 trade_mode: str, 
								 order_type: str, 
								 order_side: str, 
								 price: int,
								 size: float,
								 *args, **kwargs):
		
		order 	= self._frame_margin_order(	symbol = symbol,
											ccy = ccy,
											trade_mode = trade_mode,
											order_type = order_type,
											order_side = order_side,
											price = price,
											size = size
										)
		return asyncio.get_event_loop().run_until_complete(self._place_order_async(order = order))

	def assert_margin_resp_error(self, order_resp):
		"""
		Function looks at an order response created after placing an order and decides if we should raise an error.

		A raised error indicates a failed order attempt.
		Websocket failed error codes can be referred to here: https://www.okex.com/docs-v5/en/#error-code-websocket-public
		"""
		order_resp_code = order_resp["code"]
		if order_resp_code != "0":
			raise Exception(f"Margin order failed: {order_resp}")
		return

	async def revert_margin_order_async(self, order_resp, revert_params):
		self.logger.debug(f"Reverting margin order")
		return await self.place_margin_order_async(**revert_params)