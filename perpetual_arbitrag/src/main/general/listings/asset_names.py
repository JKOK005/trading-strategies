import argparse
import logging
import os
import time
from clients.OkxApiClient import OkxApiClient
from clients.KucoinApiClient import KucoinApiClient
from db.AssetNamesClient import AssetNamesClient

def get_exchange_client(exchange):
	if exchange == "okx":
		client 	= OkxApiClient(	
					api_key 			= "", 
					api_secret_key 		= "", 
					passphrase 			= "", 
					funding_rate_enable = False
				)
		support_asset_types = ("SPOT", "PERPETUAL")

	elif exchange == "kucoin":
		client 	= KucoinApiClient(	
					spot_client_api_key 			= "", 
					spot_client_api_secret_key 		= "", 
					spot_client_pass_phrase 		= "", 
					futures_client_api_key 			= "", 
					futures_client_api_secret_key 	= "", 
					futures_client_pass_phrase 		= "",
					sandbox 						= False,
					funding_rate_enable 			= False
				)
		support_asset_types = ("SPOT", "FUTURE")

	else:
		raise Exception(f"Exchange {exchange} not supported")

	return (client, support_asset_types)

"""
python3 main/general/listings/asset_names.py \
--exchange okx \
--db_url xxx \
--poll_interval_s 3600
"""

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Asset names')
	parser.add_argument('--exchange', type=str, nargs='?', default=os.environ.get("EXCHANGE"), help="Logs from exchange")
	parser.add_argument('--db_url', type=str, nargs='?', default=os.environ.get("DB_URL"), help="URL pointing to the database")
	parser.add_argument('--poll_interval_s', type=float, nargs='?', default=os.environ.get("POLL_INTERVAL_S"), help='Poll interval in seconds')
	args 	= parser.parse_args()

	logging.basicConfig(format='%(asctime)s %(levelname)-8s %(module)s.%(funcName)s %(lineno)d - %(message)s',
    					level=logging.INFO,
    					datefmt='%Y-%m-%d %H:%M:%S')

	logging.info(args)

	asset_names_client 	= AssetNamesClient(db_url = args.db_url).create_session()
	(exchange_client, support_asset_types) = get_exchange_client(exchange = args.exchange)

	while True:
		for each_supported_asset_types in support_asset_types:
			if each_supported_asset_types == "SPOT":
				assets = exchange_client.get_spot_symbols()

			elif each_supported_asset_types == "FUTURE":
				assets = exchange_client.get_futures_symbols()

			elif each_supported_asset_types == "PERPETUAL":
				assets = exchange_client.get_perpetual_symbols()

			else:
				raise Exception(f"Asset type {each_supported_asset_types} unsupported")

			insert_params = [	
								{	
									"exchange" 		: args.exchange, 
									"asset_type" 	: each_supported_asset_types, 
								  	"symbol" 		: each_asset[0], 
								  	"base" 			: each_asset[1],
					  			} for each_asset in assets
					  		]

			asset_names_client.delete(exchange = args.exchange, asset_type = each_supported_asset_types)
			asset_names_client.insert(params = insert_params)
		
		time.sleep(args.poll_interval_s)