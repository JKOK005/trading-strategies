import argparse
import itertools
import json
import logging
import os
from db.JobRankerClient import JobRankerClient
from clients.OkxApiClient import OkxApiClient
from clients.KucoinApiClient import KucoinApiClient
from time import sleep

def get_exchange_client(exchange):
	if exchange.lower() == "okx":
		return OkxApiClient(api_key = None, api_secret_key = None, passphrase = None, funding_rate_enable = True)

	elif exchange.lower() == "kucoin":
		return KucoinApiClient(	spot_client_api_key = None, spot_client_api_secret_key = None, spot_client_pass_phrase = None, 
								futures_client_api_key = None, futures_client_api_secret_key = None, futures_client_pass_phrase = None,
								sandbox = False, funding_rate_enable = True
							)

	else:
		raise Exception(f"{exchange} does not exist")

def get_arb_score(asset_a_price, asset_b_price, current_funding_rate, estimated_funding_rate):
	return asset_a_price / asset_b_price

"""
python3 ./main/general/scanner/arbitrag_scanner.py \
--exchange kucoin \
--asset_type spot-perp \
--db_url postgresql://arbitrag_bot:arbitrag@localhost:5432/arbitrag \
--poll_interval_s 3600
"""

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Arbitrag Scanner')
	parser.add_argument('--exchange', type=str, nargs='?', default=os.environ.get("EXCHANGE"), help="Exchange for trading")
	parser.add_argument('--asset_type', type=str, nargs='?', default=os.environ.get("ASSET_TYPE"), help="spot-perp / spot-future / future-perp")
	parser.add_argument('--db_url', type=str, nargs='?', default=os.environ.get("DB_URL"), help="URL pointing to the database")
	parser.add_argument('--poll_interval_s', type=int, nargs='?', default=os.environ.get("POLL_INTERVAL_S"), help='Poll interval in seconds')
	args 	= parser.parse_args()

	db_client 		= JobRankerClient(db_url = args.db_url).create_session()
	exchange_client = get_exchange_client(exchange = args.exchange)
	
	collective_rank = []
	jobs_to_rank 	= db_client.fetch_jobs(exchange = args.exchange, asset_type = args.asset_type)

	for each_job in jobs_to_rank:
		(first_asset, second_asset) = (each_job.first_asset, each_job.second_asset)
		(current_funding_rate, estimated_funding_rate) = (0, 0)

		if args.asset_type.lower() == "spot-perp":
			asset_a_price = exchange_client.get_spot_trading_price(symbol = first_asset)

			if args.exchange.lower() == "kucoin":
				asset_b_price = exchange_client.get_futures_trading_price(symbol = second_asset)
				(current_funding_rate, estimated_funding_rate) = exchange_client.get_futures_effective_funding_rate(symbol = second_asset, 
																													seconds_before_current = 86400, 
																													seconds_before_estimated = 86400)
			else:
				asset_b_price = exchange_client.get_perpetual_trading_price(symbol = second_asset)
				(current_funding_rate, estimated_funding_rate) = exchange_client.get_perpetual_effective_funding_rate(	symbol = second_asset, 
																														seconds_before_current = 86400, 
																														seconds_before_estimated = 86400)

		collective_rank.append((each_job, get_arb_score(asset_a_price = asset_a_price, asset_b_price = asset_b_price, 
														current_funding_rate = current_funding_rate, estimated_funding_rate = estimated_funding_rate)))

	# Rank job scoring
	collective_rank.sort(key = lambda x: x[-1], reverse = True)

	# Write rank to db
	rank_counter = itertools.count()
	for (each_job, _) in collective_rank:
		db_client.set_rank(job_ranking_id = each_job.ID, new_rank = next(rank_counter))