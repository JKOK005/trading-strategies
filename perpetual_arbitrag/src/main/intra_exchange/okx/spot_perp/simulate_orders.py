import argparse
import os
import logging
from time import sleep
from clients.OkxApiClient import OkxApiClient
from execution.SpotPerpetualBotExecution import SpotPerpetualBotExecution

"""
python3 main/intra_exchange/okx/spot_perp/main.py \
--spot_trading_pair BTC-USDT \
--perpetual_trading_pair XBTUSDTM \
--api_key xxx \
--api_secret_key xxx \
--api_passphrase xxx \
--spot_entry_vol 0.01 \
--perpetual_entry_lot_size 10 \
--order_type market
"""

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Spot - perpetual arbitrag trading')
	parser.add_argument('--spot_trading_pair', type=str, nargs='?', default=os.environ.get("SPOT_TRADING_PAIR"), help='Spot trading pair symbol as defined by exchange')
	parser.add_argument('--perpetual_trading_pair', type=str, nargs='?', default=os.environ.get("PERPETUAL_TRADING_PAIR"), help='Perpetual trading pair symbol as defined by exchange')
	parser.add_argument('--order_type', type=str, nargs='?', default=os.environ.get("ORDER_TYPE"), help='Either limit or market orders')
	parser.add_argument('--spot_entry_vol', type=float, nargs='?', default=os.environ.get("SPOT_ENTRY_VOL"), help='Volume of spot assets for each entry')
	parser.add_argument('--perpetual_entry_lot_size', type=int, nargs='?', default=os.environ.get("PERPETUAL_ENTRY_LOT_SIZE"), help='Lot size for each entry for perpetual')
	parser.add_argument('--api_key', type=str, nargs='?', default=os.environ.get("API_KEY"), help='Exchange api key')
	parser.add_argument('--api_secret_key', type=str, nargs='?', default=os.environ.get("API_SECRET_KEY"), help='Exchange secret api key')
	parser.add_argument('--api_passphrase', type=str, nargs='?', default=os.environ.get("API_PASSPHRASE"), help='Exchange api passphrase')
	args 	= parser.parse_args()

	logging.basicConfig(level = logging.INFO)
	logging.info(f"Simulating orders to Okx with the following params: {args}")

	client 	= 	OkxApiClient(api_key 			 = args.api_key, 
							 api_secret_key 	 = args.api_secret_key, 
							 passphrase 		 = args.api_passphrase, 
							 funding_rate_enable = False
							)

	bot_executor = SpotPerpetualBotExecution(api_client = client)

	logging.info(f"Going Long Spot, Short Perpetual")
	bot_executor.long_spot_short_perpetual(	spot_params = {
															"symbol" 	 	: args.spot_trading_pair, 
															"order_type" 	: args.order_type, 
															"price" 	 	: spot_price if args.order_type == "limit" else 0,
															"size" 		 	: args.spot_entry_vol,
														},
														perpetual_params = {
															"symbol" 	 	: args.perpetual_trading_pair,
															"position_side" : "short",
															"order_type" 	: args.order_type, 
															"price" 	 	: perpetual_price if args.order_type == "limit" else 10000,
															"size" 		 	: args.perpetual_entry_lot_size,
														}
													)
	sleep(5)

	logging.info(f"Take profits on Long Spot, Short Perpetual")
	bot_executor.short_spot_long_perpetual(	spot_params = {
															"symbol" 	 	: args.spot_trading_pair, 
															"order_type" 	: args.order_type, 
															"price" 	 	: spot_price if args.order_type == "limit" else 0,
															"size" 		 	: args.spot_entry_vol,
														},
														perpetual_params = {
															"symbol" 	 	: args.perpetual_trading_pair,
															"position_side" : "short",
															"order_type" 	: args.order_type, 
															"price" 	 	: perpetual_price if args.order_type == "limit" else 10000,
															"size" 		 	: args.perpetual_entry_lot_size,
														}
													)
	sleep(5)

	logging.info(f"Going Long Perpetual, Short Spot")
	bot_executor.short_spot_long_perpetual(	spot_params = {
															"symbol" 	 	: args.spot_trading_pair, 
															"order_type" 	: args.order_type, 
															"price" 	 	: spot_price if args.order_type == "limit" else 0,
															"size" 		 	: args.spot_entry_vol,
														},
														perpetual_params = {
															"symbol" 	 	: args.perpetual_trading_pair,
															"position_side" : "long",
															"order_type" 	: args.order_type, 
															"price" 	 	: perpetual_price if args.order_type == "limit" else 10000,
															"size" 		 	: args.perpetual_entry_lot_size,
														}
													)
	sleep(5)

	logging.info(f"Take profits on Long Perpetual, Short Spot")
	bot_executor.long_spot_short_perpetual(	spot_params = {
															"symbol" 	 	: args.spot_trading_pair, 
															"order_type" 	: args.order_type, 
															"price" 	 	: spot_price if args.order_type == "limit" else 0,
															"size" 		 	: args.spot_entry_vol,
														},
														perpetual_params = {
															"symbol" 	 	: args.perpetual_trading_pair,
															"position_side" : "long",
															"order_type" 	: args.order_type, 
															"price" 	 	: perpetual_price if args.order_type == "limit" else 10000,
															"size" 		 	: args.perpetual_entry_lot_size,
														}
													)