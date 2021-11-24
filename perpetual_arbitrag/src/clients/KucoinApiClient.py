from kucoin.client import Client
from kucoin_futures.client import Market

class KucoinApiClient(object):
	spot_client 		= None
	futures_client 		= None
	is_sandbox 			= False
	kucoin_futures_url 	= "https://api-futures.kucoin.com"

	def __init__(self, 	client_api_key: str, 
						client_api_secret_key: str, 
						client_pass_phrase: str,
						sandbox: bool = False):

		self.spot_client 	= Client(
								api_key 	= client_api_key,
								api_secret 	= client_api_secret_key,
								passphrase 	= client_pass_phrase,
								sandbox 	= False
							)

		self.futures_client = Market(url = self.kucoin_futures_url)
		self.is_sandbox 	= sandbox

	def get_spot_trading_price(self, trading_symbol: str):
		"""
		Retrieves current spot pricing for trading symbol
		"""
		return self.spot_client.get_ticker(symbol = trading_symbol)["price"]

	def get_futures_trading_price(self, symbol: str):
		"""
		Retrieves current futures price for trading symbol
		"""
		return self.futures_client.get_ticker("XBTUSDM")["price"]