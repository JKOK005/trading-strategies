import argparse
import os
import logging
from time import sleep
from clients.KucoinApiClient import KucoinApiClient
from strategies.SingleTradeArbitrag import SingleTradeArbitrag, ExecutionDecision

"""
python3 main.py \
--spot_trading_pair BTC-USDT \
--futures_trading_pair XBTUSDTM \
--spot_api_key xxx \
--spot_api_secret_key xxx \
--spot_api_passphrase xxx \
--futures_api_key xxx \
--futures_api_secret_key xxx \
--futures_api_passphrase xxx \
--spot_entry_vol 0.01 \
--futures_entry_lot_size 10 \
--use_sandbox
"""

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Spot - Futures arbitrag trading')
	parser.add_argument('--spot_trading_pair', type=str, nargs='?', default="BTC-USDT", help='Spot trading pair symbol as defined by exchange')
	parser.add_argument('--futures_trading_pair', type=str, nargs='?', default="XBTUSDM", help='Futures trading pair symbol as defined by exchange')
	parser.add_argument('--use_sandbox', action='store_true', help='If present, trades in Sandbox env. Else, trades in REAL env.')
	parser.add_argument('--trade_threshold', type=float, nargs='?', default=0.1, help='% threshold beyond which we consider it an arbitrag opportunity')
	parser.add_argument('--poll_interval_s', type=int, nargs='?', default=60, help='Poll interval in seconds')
	parser.add_argument('--spot_entry_vol', type=float, nargs='?', default=0.001, help='Volume of spot assets for each entry')
	parser.add_argument('--futures_entry_lot_size', type=int, nargs='?', default=100, help='Lot size for each entry for futures')
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

	trade_strategy 	= SingleTradeArbitrag(	spot_symbol 		= args.spot_trading_pair,
											futures_symbol 		= args.futures_trading_pair,
											entry_percent_gap 	= args.entry_gap_frac * 100,
											api_client 			= client
										)

	while True:
		spot_price 		= client.get_spot_trading_price(symbol = args.spot_trading_pair)
		futures_price 	= client.get_futures_trading_price(symbol = args.futures_trading_pair)
		logging.info(f"Spot price: {spot_price}, Futures price: {futures_price}, Ratio: {spot_price / futures_price * 100}%")
		
		decision 		= trade_strategy.trade_decision(spot_price = spot_price, futures_price = futures_price, threshold = args.entry_gap_frac)
		logging.info(f"Executing trade decision: {decision}")

		# Execute orders
		if decision == ExecutionDecision.GO_LONG_SPOT_SHORT_FUTURE:
			client.place_spot_order(symbol 		= args.spot_trading_pair,
									order_type 	= "buy",
									order_side 	= "limit",
									price 		= spot_price,
									size 		= args.spot_entry_vol
								)

			client.place_futures_order(	symbol 		= args.futures_trading_pair,
										order_type 	= "sell",
										order_side 	= "limit",
										price 		= futures_price,
										size 		= args.futures_entry_lot_size,
										lever 		= 1
									)

		elif decision == ExecutionDecision.GO_LONG_FUTURE_SHORT_SPOT:
			client.place_spot_order(symbol 		= args.spot_trading_pair,
									order_type 	= "sell",
									order_side 	= "limit",
									price 		= spot_price,
									size 		= args.spot_entry_vol
								)

			client.place_futures_order(	symbol 		= args.futures_trading_pair,
										order_type 	= "buy",
										order_side 	= "limit",
										price 		= futures_price,
										size 		= args.futures_entry_lot_size,
										lever 		= 1
									)


		sleep(args.poll_interval_s)