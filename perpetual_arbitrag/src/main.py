import argparse
import os
import logging
from time import sleep
from clients.KucoinApiClient import KucoinApiClient
from strategies.SingleTradeArbitrag import SingleTradeArbitrag

"""
python3 main.py \
--spot_trading_pair BTC-USDT \
--futures_trading_pair XBTUSDM \
--poll_interval_s 60 \
--spot_api_key xxx \
--spot_api_secret_key xxx \
--spot_api_passphrase xxx
--futures_api_key xxx \
--futures_api_secret_key xxx \
--futures_api_passphrase xxx \
--use_sandbox
"""

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Spot - Futures arbitrag trading')
	parser.add_argument('--spot_trading_pair', type=str, nargs='?', default="BTC-USDT", help='Spot trading pair symbol as defined by exchange')
	parser.add_argument('--futures_trading_pair', type=str, nargs='?', default="XBTUSDM", help='Futures trading pair symbol as defined by exchange')
	parser.add_argument('--use_sandbox', action='store_true', help='If present, trades in Sandbox env. Else, trades in REAL env.')
	parser.add_argument('--trade_threshold', type=float, nargs='?', default=0.1, help='% threshold beyond which we consider it an arbitrag opportunity')
	parser.add_argument('--poll_interval_s', type=int, nargs='?', default=60, help='Poll interval in seconds')
	parser.add_argument('--trading_lot_size', type=int, nargs='?', default=100, help='Lot size for each transaction')
	parser.add_argument('--entry_gap_frac', type=float, nargs='?', default=0.1, help='Fraction of price difference which we can consider making an entry')
	parser.add_argument('--spot_api_key', type=str, nargs='?', help='Spot exchange api key')
	parser.add_argument('--spot_api_secret_key', type=str, nargs='?', default="????", help='Spot exchange secret api key')
	parser.add_argument('--spot_api_passphrase', type=str, nargs='?', default="????", help='Spot exchange api passphrase')
	parser.add_argument('--futures_api_key', type=str, nargs='?', help='Futures exchange api key')
	parser.add_argument('--futures_api_secret_key', type=str, nargs='?', default="????", help='Futures exchange secret api key')
	parser.add_argument('--futures_api_passphrase', type=str, nargs='?', default="????", help='Futures exchange api passphrase')
	args 	= parser.parse_args()

	logging.basicConfig(level = logging.INFO)

	client 	= KucoinApiClient(	spot_client_api_key 			= args.spot_api_key, 
								spot_client_api_secret_key 		= args.spot_api_secret_key, 
								spot_client_pass_phrase 		= args.spot_api_passphrase, 
								futures_client_api_key 			= args.futures_api_key, 
								futures_client_api_secret_key 	= args.futures_api_secret_key, 
								futures_client_pass_phrase 		= args.futures_api_passphrase,
								sandbox 						= args.use_sandbox
							)

	trade_strategy 		= SingleTradeArbitrag(	spot_symbol 		= args.spot_trading_pair,
												futures_symbol 		= args.futures_trading_pair,
												lot_size_entry 		= args.trading_lot_size,
												entry_percent_gap 	= args.entry_gap_frac * 100,
												api_client 			= client
											)

	import IPython
	IPython.embed()

	while True:
		spot_price 		= client.get_spot_trading_price(symbol = args.spot_trading_pair)
		futures_price 	= client.get_futures_trading_price(symbol = args.futures_trading_pair)
		logging.info(f"Spot price: {spot_price}, Futures price: {futures_price}, Ratio: {spot_price / futures_price * 100}%")
		sleep(args.poll_interval_s)