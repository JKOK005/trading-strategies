import argparse
import os
from clients.KucoinApiClient import KucoinApiClient

"""
python3 main.py \
--spot_trading_symbol BTC-USDT \
--futures_trading_symbol XBTCUSDM \
--use_sandbox 1 \
--api_key xxx \
--api_secret_key xxx \
--api_passphrase xxx
"""

if __name__ == "__main__":
	parser 		= argparse.ArgumentParser(description='Spot - Futures arbitrag trading')
	parser.add_argument('--spot_trading_symbol', type=str, nargs='?', default="BTC-USDT", help='Spot trading pair symbol as defined by exchange')
	parser.add_argument('--futures_trading_symbol', type=str, nargs='?', default="XBTCUSDM", help='Futures trading pair symbol as defined by exchange')
	parser.add_argument('--use_sandbox', type=bool, nargs='?', default=1, help='1 - Trade in sandbox env. 0 - Trade in REAL env')
	parser.add_argument('--api_key', type=str, nargs='?', help='Exchange api key')
	parser.add_argument('--api_secret_key', type=str, nargs='?', default="????", help='Exchange secret api key')
	parser.add_argument('--api_passphrase', type=str, nargs='?', default="????", help='Exchange api passphrase')
	args 		= parser.parse_args()


	client 		= KucoinApiClient(	client_api_key = args.api_key, 
									client_api_secret_key = args.api_secret_key, 
									client_pass_phrase = args.api_passphrase,
									sandbox = args.use_sandbox
								)

	import IPython
	IPython.embed()