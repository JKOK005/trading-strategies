import asyncio
import json
import hmac
import logging
import time
import websockets
from clients.FtxApiClient import FtxApiClient

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
		epoch_ts 		= int(time.time() * 1000)
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