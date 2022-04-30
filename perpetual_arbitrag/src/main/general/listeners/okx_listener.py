import argparse
import logging
import os
from clients.OkxApiClient import OkxApiClient
from db.TradeLogsClient import TradeLogsClient

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Log listener')
	parser.add_argument('--splits', type=int, nargs='?', default=os.environ.get("SPLITS"), help="Total number of splits on user IDs")
	parser.add_argument('--split_frac', type=int, nargs='?', default=os.environ.get("SPLIT_FRAC"), help="Fraction of splits that this script handles. Used for sharding and scaling")
	parser.add_argument('--db_url', type=str, nargs='?', default=os.environ.get("DB_URL"), help="URL pointing to the database")
	args 	= parser.parse_args()
	
	client = OkxApiClient(	api_key = "eddce8fd-fd44-4084-ab82-74a3b9ccfc9e", 
							api_secret_key = "9D849D285068F24BB9FCDD5F9A3F2354", 
							passphrase = "Mldkk1982", 
							funding_rate_enable = False
						)

	recent_transactions = client.get_all_filled_transactions_days(before = 0)
	db_client = TradeLogsClient(db_url = "postgresql://arbitrag_bot:arbitrag@localhost:5432/arbitrag").create_session()

	for each_transactions in recent_transactions:
		print(each_transactions)
		db_client.insert(params = {	
									"exchange"  	: "okx",
									"client_id" 	: "123",
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