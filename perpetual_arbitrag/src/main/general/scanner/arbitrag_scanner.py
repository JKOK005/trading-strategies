import argparse
import json
import os
import sys
import logging
from db.JobRankerClient import JobRankerClient
from time import sleep

def get_exchange_client(exchange):
	if exchange.lower() == "okx":
		return ...

	elif exchange.lower() == "kucoin":
		return ...

	else:
		raise Exception(f"{exchange} does not exist")

def get_arb_score(asset_a_price, asset_b_price, current_funding_rate, estimated_funding_rate):
	return 0

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
			asset_b_price = exchange_client.get_perpetual_trading_price(symbol = second_asset)
			(current_funding_rate, estimated_funding_rate) = exchange_client.get_perpetual_effective_funding_rate(	symbol = second_asset, 
																													seconds_before_current = sys.maxint, 
																													seconds_before_estimated = sys.maxint)

		collective_rank.append((each_job, get_arb_score(asset_a_price = asset_a_price, asset_b_price = asset_b_price, 
														current_funding_rate = current_funding_rate, estimated_funding_rate = estimated_funding_rate)))

	# Rank job scoring

	# Write rank to db