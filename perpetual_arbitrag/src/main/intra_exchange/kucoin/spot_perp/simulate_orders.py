import argparse
import logging
import os
from clients.KucoinApiClient import KucoinApiClient
from execution.SpotFutureBotExecution import SpotFutureBotExecution
from time import sleep

"""
python3 main/intra_exchange/kucoin/spot_perp/simulate_orders.py \
--spot_trading_pair ONE-USDT \
--futures_trading_pair ONEUSDTM \
--spot_api_key xxx \
--spot_api_secret_key xxx \
--spot_api_passphrase xxx \
--futures_api_key xxx \
--futures_api_secret_key xxx \
--futures_api_passphrase xxx \
--order_type market \
--spot_entry_vol 10 \
--futures_entry_lot_size 1
"""

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Spot - Futures arbitrag trading')
	parser.add_argument('--spot_trading_pair', type=str, nargs='?', default=os.environ.get("SPOT_TRADING_PAIR"), help='Spot trading pair symbol as defined by exchange')
	parser.add_argument('--futures_trading_pair', type=str, nargs='?', default=os.environ.get("FUTURES_TRADING_PAIR"), help='Futures trading pair symbol as defined by exchange')
	parser.add_argument('--order_type', type=str, nargs='?', default=os.environ.get("ORDER_TYPE"), help='Either limit or market orders')
	parser.add_argument('--spot_entry_vol', type=float, nargs='?', default=os.environ.get("SPOT_ENTRY_VOL"), help='Volume of spot assets for each entry')
	parser.add_argument('--futures_entry_lot_size', type=int, nargs='?', default=os.environ.get("FUTURES_ENTRY_LOT_SIZE"), help='Lot size for each entry for futures')
	parser.add_argument('--spot_api_key', type=str, nargs='?', default=os.environ.get("SPOT_API_KEY"), help='Spot exchange api key')
	parser.add_argument('--spot_api_secret_key', type=str, nargs='?', default=os.environ.get("SPOT_API_SECRET_KEY"), help='Spot exchange secret api key')
	parser.add_argument('--spot_api_passphrase', type=str, nargs='?', default=os.environ.get("SPOT_API_PASSPHRASE"), help='Spot exchange api passphrase')
	parser.add_argument('--futures_api_key', type=str, nargs='?', default=os.environ.get("FUTURES_API_KEY"), help='Futures exchange api key')
	parser.add_argument('--futures_api_secret_key', type=str, nargs='?', default=os.environ.get("FUTURES_API_SECRET_KEY"), help='Futures exchange secret api key')
	parser.add_argument('--futures_api_passphrase', type=str, nargs='?', default=os.environ.get("FUTURES_API_PASSPHRASE"), help='Futures exchange api passphrase')
	args 	= parser.parse_args()

	logging.basicConfig(level = logging.INFO)
	logging.info(f"Simulating orders on Kucoin with the following params: {args}")

	client 			= KucoinApiClient(	spot_client_api_key 			= args.spot_api_key, 
										spot_client_api_secret_key 		= args.spot_api_secret_key, 
										spot_client_pass_phrase 		= args.spot_api_passphrase, 
										futures_client_api_key 			= args.futures_api_key, 
										futures_client_api_secret_key 	= args.futures_api_secret_key, 
										futures_client_pass_phrase 		= args.futures_api_passphrase,
										sandbox 						= False,
										funding_rate_enable 			= False
									)

	bot_executor 	= SpotFutureBotExecution(api_client = client)

	logging.info(f"Going Long Spot, Short Perpetual")
	bot_executor.long_spot_short_futures(	spot_params 	= { "symbol" 		: args.spot_trading_pair, 
																"order_type" 	: args.order_type,
																"price" 		: spot_price if args.order_type == "limit" else 1,
																"size" 			: args.spot_entry_vol,
															},

											future_params 	= {	"symbol" 		: args.futures_trading_pair, 
																"order_type" 	: args.order_type, 
																"price" 		: futures_price if args.order_type == "limit" else 1,
																"size" 			: args.futures_entry_lot_size,
																"lever" 		: 1,
															},
										)
	sleep(5)

	logging.info(f"Take profits on Long Spot, Short Perpetual")
	bot_executor.short_spot_long_futures(	spot_params 	= {	"symbol" 		: args.spot_trading_pair, 
																"order_type" 	: args.order_type,
																"price" 		: spot_price if args.order_type == "limit" else 1,
																"size" 			: args.spot_entry_vol,
															},

											future_params 	= {	"symbol" 		: args.futures_trading_pair, 
																"order_type" 	: args.order_type, 
																"price" 		: futures_price if args.order_type == "limit" else 1,
																"size" 			: args.futures_entry_lot_size,
																"lever" 		: 1,
															},
										)
	sleep(5)

	logging.info(f"Going Long Perpetual, Short Spot")
	bot_executor.short_spot_long_futures(	spot_params 	= {	"symbol" 		: args.spot_trading_pair, 
																"order_type" 	: args.order_type,
																"price" 		: spot_price if args.order_type == "limit" else 1,
																"size" 			: args.spot_entry_vol,
															},

											future_params 	= {	"symbol" 		: args.futures_trading_pair, 
																"order_type" 	: args.order_type, 
																"price" 		: futures_price if args.order_type == "limit" else 1,
																"size" 			: args.futures_entry_lot_size,
																"lever" 		: 1,
															},
										)
	sleep(5)

	logging.info(f"Take profits on Long Perpetual, Short Spot")
	bot_executor.long_spot_short_futures(	spot_params 	= { "symbol" 		: args.spot_trading_pair, 
																"order_type" 	: args.order_type,
																"price" 		: spot_price if args.order_type == "limit" else 1,
																"size" 			: args.spot_entry_vol,
															},

											future_params 	= {	"symbol" 		: args.futures_trading_pair, 
																"order_type" 	: args.order_type, 
																"price" 		: futures_price if args.order_type == "limit" else 1,
																"size" 			: args.futures_entry_lot_size,
																"lever" 		: 1,
															},
										)