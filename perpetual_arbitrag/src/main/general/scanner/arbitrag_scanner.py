import argparse
import itertools
import json
import logging
import numpy as np
import os
import redis
from datetime import datetime
from db.JobRankerClient import JobRankerClient
from clients.OkxApiClient import OkxApiClient
from clients.KucoinApiClient import KucoinApiClient
from multiprocessing import Pool
from time import sleep

def get_exchange_client(exchange):
	if exchange.lower() == "okx" or exchange.lower() == "test-okx":
		return OkxApiClient(api_key = "None", api_secret_key = "None", passphrase = "None", funding_rate_enable = True)

	elif exchange.lower() == "kucoin":
		return KucoinApiClient(	spot_client_api_key = None, spot_client_api_secret_key = None, spot_client_pass_phrase = None, 
								futures_client_api_key = None, futures_client_api_secret_key = None, futures_client_pass_phrase = None,
								sandbox = False, funding_rate_enable = True
							)

	else:
		raise Exception(f"{exchange} does not exist")

def arb_score_formula(spot_price, perp_price, current_funding_rate, estimated_funding_rate):
	effective_perp_price = perp_price * (1 + current_funding_rate + estimated_funding_rate)
	return (effective_perp_price - spot_price) / (perp_price + spot_price)

def compute_arb_score(job_to_rank):
	(first_asset, second_asset) = (job_to_rank.first_asset, job_to_rank.second_asset)
	(current_funding_rate, estimated_funding_rate) = (0, 0)
	arb_scores 	= []

	for _ in range(args.samples):
		if args.asset_type.lower() == "spot-perp":
			(_, asset_a_ask_price) = exchange_client.get_spot_average_bid_ask_price(symbol = first_asset, size = 0.00001)

			if args.exchange.lower() == "kucoin":
				(asset_b_bid_price, _) = exchange_client.get_futures_average_bid_ask_price(symbol = second_asset, size = 1)
				(current_funding_rate, estimated_funding_rate) = exchange_client.get_futures_effective_funding_rate(symbol = second_asset, 
																													seconds_before_current = 86400, 
																													seconds_before_estimated = 86400)
			else:
				(asset_b_bid_price, _) = exchange_client.get_perpetual_average_bid_ask_price(symbol = second_asset, size = 1)
				(current_funding_rate, estimated_funding_rate) = exchange_client.get_perpetual_effective_funding_rate(	symbol = second_asset, 
																														seconds_before_current = 86400, 
																														seconds_before_estimated = 86400)
		arb_scores.append(arb_score_formula(spot_price = asset_a_ask_price, perp_price = asset_b_bid_price,
											current_funding_rate = current_funding_rate, estimated_funding_rate = estimated_funding_rate))
		sleep(1)

	mean_arb_score = np.mean(arb_scores)
	return (job_to_rank, mean_arb_score)

"""
python3 ./main/general/scanner/arbitrag_scanner.py \
--exchange okx \
--asset_type spot-perp \
--db_url postgresql://arbitrag_bot:arbitrag@localhost:5432/arbitrag \
--message_url localhost \
--message_port 6379 \
--poll_interval_s 3600 \
--processors 4 \
--samples 120
"""
if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Arbitrag Scanner')
	parser.add_argument('--exchange', type=str, nargs='?', default=os.environ.get("EXCHANGE"), help="Exchange for trading")
	parser.add_argument('--asset_type', type=str, nargs='?', default=os.environ.get("ASSET_TYPE"), help="spot-perp / spot-future / future-perp")
	parser.add_argument('--db_url', type=str, nargs='?', default=os.environ.get("DB_URL"), help="URL pointing to the database")
	parser.add_argument('--message_url', type=str, nargs='?', default=os.environ.get("MESSAGE_URL"), help="URL pointing to the messaging queue, such as redis")
	parser.add_argument('--message_port', type=str, nargs='?', default=os.environ.get("MESSAGE_PORT"), help="Port of the messaging queue app")
	parser.add_argument('--samples', type=int, nargs='?', default=os.environ.get("SAMPLES"), help="Samples to compute average arb score for an asset pair")
	parser.add_argument('--processors', type=int, nargs='?', default=os.environ.get("PROCESSORS"), help="Processors for parallel computation")
	parser.add_argument('--poll_interval_s', type=int, nargs='?', default=os.environ.get("POLL_INTERVAL_S"), help='Poll interval in seconds')
	args 	= parser.parse_args()

	logging.basicConfig(level = logging.INFO)

	db_client 			= JobRankerClient(db_url = args.db_url).create_session()
	messaging_client 	= redis.Redis(host = args.message_url, port = args.message_port, decode_responses=True, encoding="utf-8")
	messaging_channel 	= f'arb/{args.exchange}/{args.asset_type}'

	exchange_client 	= get_exchange_client(exchange = args.exchange)
	jobs_to_rank 		= db_client.fetch_jobs(exchange = args.exchange, asset_type = args.asset_type)

	while True:
		with Pool(processes = args.processors) as pool:
			collective_rank = pool.map(compute_arb_score, jobs_to_rank)

		logging.info(f"{collective_rank}")

		# Rank job scoring
		collective_rank.sort(key = lambda x: x[-1], reverse = True)

		# Write rank to db
		rank_counter = itertools.count()
		for (each_job, score) in collective_rank:
			db_client.set_rank(job_ranking_id = each_job.ID, new_rank = next(rank_counter))
			db_client.set_arb_score(job_ranking_id = each_job.ID, new_score = score)

		payload 	= {"update_time" : datetime.utcnow().timestamp()}
		messaging_client.publish(messaging_channel, json.dumps(payload))
		sleep(args.poll_interval_s)