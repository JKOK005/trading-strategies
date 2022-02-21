import argparse
import os
import logging

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Spot - perpetual arbitrag manager')
	parser.add_argument('--exchange', type=str, nargs='?', default=os.environ.get("EXCHANGE"), help='Exchange name')
	parser.add_argument('--exchange_id', type=str, nargs='?', default=os.environ.get("EXCHANGE_ID"), help='Exchange client ID')
	parser.add_argument('--asset_pair', type=str, nargs='?', default=os.environ.get("ASSET_PAIR"), help='Asset pairing')
	parser.add_argument('--docker_img_name', type=str, nargs='?', default=os.environ.get("DOCKER-IMG-NAME"), help='Docker image name for trading asset pair on exchange')
	parser.add_argument('--default_args', type=str, nargs='?', default=os.environ.get("DEFAULT_ARGS"), help='Arguments to be passed to docker container on launch')
	parser.add_argument('--entry_args', type=str, nargs='?', default=os.environ.get("ENTRY_ARGS"), help='Combined with default args. These arguments should contain information on how to enter a trade, such as entry / take profit threshold')
	parser.add_argument('--exit_args', type=str, nargs='?', default=os.environ.get("EXIT_ARGS"), help='Combined with default args. These arguments should contain information on how to exit a trade, such as entry / take profit threshold')
	parser.add_argument('--poll_interval_s', type=int, nargs='?', default=os.environ.get("POLL_INTERVAL_S"), help='Poll interval in seconds')
	parser.add_argument('--db_url', type=str, nargs='?', default=os.environ.get("DB_URL"), help="URL pointing to the database")
