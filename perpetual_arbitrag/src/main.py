from kucoin.client import Client
from kucoin_futures.client import Market

api_key 		= '619caa7d39f3850001fc821f'
api_secret 		= '3043479a-492d-40ae-93a5-e532ff70115f'
api_passphrase 	= 'kucointrading'

if __name__ == "__main__":
	spot_client 	= Client(
						api_key 	= api_key,
						api_secret 	= api_secret,
						passphrase 	= api_passphrase,
						sandbox 	= False
					)

	futures_client 	= Market(url='https://api-futures.kucoin.com')

	# Get Fiat prices
	last_traded_asset_price 	= spot_client.get_ticker(symbol = "BTC-USDT")["price"]
	last_traded_futures_price 	= futures_client.get_ticker("XBTUSDM")["price"]

	import IPython
	IPython.embed()