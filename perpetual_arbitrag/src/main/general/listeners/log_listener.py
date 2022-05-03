import argparse
import json
import logging
import os
import time
from clients.OkxApiClient import OkxApiClient
from clients.KucoinApiClient import KucoinApiClient
from db.TradeLogsClient import TradeLogsClient
from db.SecretsClient import SecretsClient

def dispatch(exchange: str, api_keys: {}):
	if exchange == "okx":
		client 	= OkxApiClient(	
					api_key 			= api_keys["API_KEY"], 
					api_secret_key 		= api_keys["API_SECRET_KEY"], 
					passphrase 			= api_keys["API_PASSPHRASE"], 
					funding_rate_enable = False
				)

	elif exchange == "kucoin":
		client 	= KucoinApiClient(	
					spot_client_api_key 			= api_keys["SPOT_API_KEY"], 
					spot_client_api_secret_key 		= api_keys["SPOT_API_SECRET_KEY"], 
					spot_client_pass_phrase 		= api_keys["SPOT_API_PASSPHRASE"], 
					futures_client_api_key 			= api_keys["FUTURES_API_KEY"], 
					futures_client_api_secret_key 	= api_keys["FUTURES_API_SECRET_KEY"], 
					futures_client_pass_phrase 		= api_keys["FUTURES_API_PASSPHRASE"],
					sandbox 						= False,
					funding_rate_enable 			= False
				)
	
	else:
		raise Exception(f"{exchange} not supported")
	
	return client

"""
python3 \
--splits 1 \
--split_frac 1 \
--exchange okx \
--db_url xxx \
--poll_interval_s 300 \
main/general/listeners/log_listener.py
"""

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Log listener')
	parser.add_argument('--splits', type=int, nargs='?', default=os.environ.get("SPLITS"), help="Total number of splits on user IDs")
	parser.add_argument('--split_frac', type=int, nargs='?', default=os.environ.get("SPLIT_FRAC"), help="Fraction of splits that this script handles. Used for sharding and scaling")
	parser.add_argument('--exchange', type=str, nargs='?', default=os.environ.get("EXCHANGE"), help="Logs from exchange")
	parser.add_argument('--db_url', type=str, nargs='?', default=os.environ.get("DB_URL"), help="URL pointing to the database")
	parser.add_argument('--poll_interval_s', type=float, nargs='?', default=os.environ.get("POLL_INTERVAL_S"), help='Poll interval in seconds')
	args 	= parser.parse_args()

	logging.basicConfig(format='%(asctime)s %(levelname)-8s %(module)s.%(funcName)s %(lineno)d - %(message)s',
    					level=logging.INFO,
    					datefmt='%Y-%m-%d %H:%M:%S')
	
	secrets_client 		= SecretsClient(db_url = args.db_url).create_session()
	trade_logs_client 	= TradeLogsClient(db_url = args.db_url).create_session()
	page_tracking 		= {}

	while True:
		for user_secret_obj in secrets_client.get_all_secrets(exchange = args.exchange):
			if user_secret_obj.ID % args.splits == args.split_frac:
				try:
					max_page = page_tracking[user_secret_obj.ID] if user_secret_obj.ID in page_tracking else 0
					api_keys = json.loads(user_secret_obj.api_keys)
					client 	 = dispatch(exchange = args.exchange, api_keys = api_keys)
					
					logging.info(f"Fetching transactions for user ID {user_secret_obj.ID} after bill ID {max_page}")
					recent_transactions = client.get_all_filled_transactions_days(before = max_page)
					
					for each_transactions in recent_transactions:
						trade_logs_client.insert(params = {	
													"exchange"  	: "okx",
													"client_id" 	: user_secret_obj.client_id,
													"page_id" 		: each_transactions["billId"],
													"order_id"  	: each_transactions["ordId"],
													"trade_id" 		: each_transactions["tradeId"],
													"symbol" 		: each_transactions["instId"],
													"fill_price" 	: each_transactions["fillPx"],
													"fill_size" 	: each_transactions["fillSz"],
													"order_side" 	: each_transactions["side"],
													"pos_side" 		: each_transactions["posSide"],
													"order_ts" 		: each_transactions["ts"],
												}
										)

						max_page = max(int(each_transactions["billId"]), max_page)
						page_tracking[user_secret_obj.ID] = max_page

				except Exception as ex:
					logging.error(f"Failed to load user {user_secret_obj} transactions with error: {ex}")

		time.sleep(args.poll_interval_s)