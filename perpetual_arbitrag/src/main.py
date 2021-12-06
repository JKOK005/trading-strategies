import argparse
import os
import logging
from time import sleep
from clients.KucoinApiClient import KucoinApiClient
from execution.BotExecution import BotExecution 
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
--order_type market \
--spot_entry_vol 0.01 \
--futures_entry_lot_size 10 \
--futures_entry_leverage 1 \
--entry_gap_frac 0.1 \
--poll_interval_s 60 \
--use_sandbox
"""

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Spot - Futures arbitrag trading')
	parser.add_argument('--spot_trading_pair', type=str, nargs='?', default="BTC-USDT", help='Spot trading pair symbol as defined by exchange')
	parser.add_argument('--futures_trading_pair', type=str, nargs='?', default="XBTUSDM", help='Futures trading pair symbol as defined by exchange')
	parser.add_argument('--use_sandbox', action='store_true', help='If present, trades in Sandbox env. Else, trades in REAL env.')
	parser.add_argument('--order_type', type=str, nargs='?', default="market", help='Either limit or market orders')
	parser.add_argument('--poll_interval_s', type=int, nargs='?', default=60, help='Poll interval in seconds')
	parser.add_argument('--spot_entry_vol', type=float, nargs='?', default=0.001, help='Volume of spot assets for each entry')
	parser.add_argument('--futures_entry_lot_size', type=int, nargs='?', default=100, help='Lot size for each entry for futures')
	parser.add_argument('--futures_entry_leverage', type=int, nargs='?', default=1, help='Leverage for each entry for futures')
	parser.add_argument('--entry_gap_frac', type=float, nargs='?', default=0.1, help='Fraction of price difference which we can consider making an entry')
	parser.add_argument('--spot_api_key', type=str, nargs='?', help='Spot exchange api key')
	parser.add_argument('--spot_api_secret_key', type=str, nargs='?', default="????", help='Spot exchange secret api key')
	parser.add_argument('--spot_api_passphrase', type=str, nargs='?', default="????", help='Spot exchange api passphrase')
	parser.add_argument('--futures_api_key', type=str, nargs='?', help='Futures exchange api key')
	parser.add_argument('--futures_api_secret_key', type=str, nargs='?', default="????", help='Futures exchange secret api key')
	parser.add_argument('--futures_api_passphrase', type=str, nargs='?', default="????", help='Futures exchange api passphrase')
	args 	= parser.parse_args()

	logging.basicConfig(level = logging.INFO)
	logging.info(f"Starting Arbitrag bot with the following params: {args}")

	client 			= KucoinApiClient(	spot_client_api_key 			= args.spot_api_key, 
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

	bot_executor 	= BotExecution(api_client = client)

	while True:
		if 	args.order_type == "limit":
			spot_price 		= client.get_spot_trading_price(symbol = args.spot_trading_pair)
			futures_price 	= client.get_futures_trading_price(symbol = args.futures_trading_pair)
			decision 		= trade_strategy.trade_decision(spot_price = spot_price, futures_price = futures_price, threshold = args.entry_gap_frac)
			logging.info(f"Spot price: {spot_price}, Futures price: {futures_price}")			

		elif args.order_type == "market":
			(avg_spot_bid, avg_spot_ask) 		= client.get_spot_average_bid_ask_price(symbol = args.spot_trading_pair, size = args.spot_entry_vol)
			(avg_futures_bid, avg_futures_ask) 	= client.get_futures_average_bid_ask_price(symbol = args.futures_trading_pair, size = args.futures_entry_lot_size)
			decision 							= trade_strategy.bid_ask_trade_decision(spot_bid_price 		= avg_spot_bid,
																						spot_ask_price 		= avg_spot_ask,
																						futures_bid_price 	= avg_futures_bid,
																						futures_ask_price 	= avg_futures_ask,
																						threshold 			= args.entry_gap_frac)
			logging.info(f"Avg spot bid: {avg_spot_bid}, asks: {avg_spot_ask} / Perpetuals bid: {avg_futures_bid}, asks: {avg_futures_ask}")
		
		logging.info(f"Executing trade decision: {decision}")		

		# Execute orders
		if decision == ExecutionDecision.GO_LONG_SPOT_SHORT_FUTURE:
			bot_executor.long_spot_short_futures(	spot_symbol 		= args.spot_trading_pair,
													spot_order_type 	= args.order_type,
													spot_price 			= spot_price if args.order_type == "limit" else 1,
													spot_size 			= args.spot_entry_vol,
													futures_symbol 		= args.futures_trading_pair,
													futures_order_type 	= args.order_type,
													futures_price 		= futures_price if args.order_type == "limit" else 1,
													futures_size 		= args.futures_entry_lot_size,
													futures_lever 		= args.futures_entry_leverage
												)

		elif decision == ExecutionDecision.GO_LONG_FUTURE_SHORT_SPOT:
			bot_executor.short_spot_long_futures(	spot_symbol 		= args.spot_trading_pair,
													spot_order_type 	= args.order_type,
													spot_price 			= spot_price if args.order_type == "limit" else 1,
													spot_size 			= args.spot_entry_vol,
													futures_symbol 		= args.futures_trading_pair,
													futures_order_type 	= args.order_type,
													futures_price 		= futures_price if args.order_type == "limit" else 1,
													futures_size 		= args.futures_entry_lot_size,
													futures_lever 		= args.futures_entry_leverage
												)

		sleep(args.poll_interval_s)