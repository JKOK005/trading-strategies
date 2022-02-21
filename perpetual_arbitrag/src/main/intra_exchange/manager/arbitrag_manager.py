import argparse
import docker
import os
import logging
from db.BotManagerClients import BotManagerClients

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Arbitrag manager')
	parser.add_argument('--exchange', type=str, nargs='?', default=os.environ.get("EXCHANGE"), help='Exchange name')
	parser.add_argument('--client_id', type=str, nargs='?', default=os.environ.get("CLIENT_ID"), help='Exchange client ID')
	parser.add_argument('--product_type', type=str, nargs='?', default=os.environ.get("ASSET_PAIR"), help='Type of product, such as spot-perp')
	parser.add_argument('--docker_img_name', type=str, nargs='?', default=os.environ.get("DOCKER-IMG-NAME"), help='Docker image name for trading asset pair on exchange')
	parser.add_argument('--default_args', type=str, nargs='?', default=os.environ.get("DEFAULT_ARGS"), help='Arguments to be passed to docker container on launch')
	parser.add_argument('--entry_args', type=str, nargs='?', default=os.environ.get("ENTRY_ARGS"), help='Combined with default args. These arguments should contain information on how to enter a trade, such as entry / take profit threshold')
	parser.add_argument('--exit_args', type=str, nargs='?', default=os.environ.get("EXIT_ARGS"), help='Combined with default args. These arguments should contain information on how to exit a trade, such as entry / take profit threshold')
	parser.add_argument('--poll_interval_s', type=int, nargs='?', default=os.environ.get("POLL_INTERVAL_S"), help='Poll interval in seconds')
	parser.add_argument('--db_url', type=str, nargs='?', default=os.environ.get("DB_URL"), help="URL pointing to the database")
	args 	= parser.parse_args()

	logging.basicConfig(level = logging.INFO)
	logging.info(f"Starting arbitrag manager with the following params: {args}")

	bot_manager_client 	= BotManagerClients(url = args.db_url, exchange = args.exchange, asset_pair = args.product_type)
	docker_client 		= docker.from_env()

	# Get recommended asset pairs to trade
	to_trade_pairs 		= bot_manager_client.get_trade_pairs()
	
	# Get running containers for asset pair
	running_containers 	= docker_client.containers.filter({"label" : [f"exchange={args.exchange}", f"client_id={args.client_id}", f"product_type={args.product_type}"]})

	# Filter containers to kill, create or undo a kill
	pairs_to_create		= []

	for each_trade_pairs in to_trade_pairs:
		pass

	# Create containers

	# Kill containers

