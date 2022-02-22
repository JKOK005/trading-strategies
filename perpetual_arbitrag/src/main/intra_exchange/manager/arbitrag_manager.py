import argparse
import docker
import json
import os
import logging
from db.BotManagerClients import BotManagerClients

docker_client = docker.from_env()
logging.basicConfig(level = logging.INFO)

def pull(image_name: str):
	logging.info(f"Pulling {image}")
	docker_client.image.pull(image_name)

def run(container_name: str, container_args, labels):
	logging.info(f"Starting {container_name}")
	return docker_client.containers.run(image = container_name, environment = container_args, labels = labels, detach = True)

def kill(container):
	logging.info(f"Killing container {container}")
	return container.kill()

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Arbitrag manager')
	parser.add_argument('--exchange', type=str, nargs='?', default=os.environ.get("EXCHANGE"), help='Exchange name')
	parser.add_argument('--client_id', type=str, nargs='?', default=os.environ.get("CLIENT_ID"), help='Exchange client ID')
	parser.add_argument('--product_type', type=str, nargs='?', default=os.environ.get("ASSET_PAIR"), help='Type of product, such as spot-perp')
	parser.add_argument('--poll_interval_s', type=int, nargs='?', default=os.environ.get("POLL_INTERVAL_S"), help='Poll interval in seconds')
	parser.add_argument('--db_url', type=str, nargs='?', default=os.environ.get("DB_URL"), help="URL pointing to the database")
	args 	= parser.parse_args()

	logging.info(f"Starting arbitrag manager with the following params: {args}")

	bot_manager_client 	= BotManagerClients(url = args.db_url, exchange = args.exchange, asset_pair = args.product_type)

	# Kill all running containers
	running_containers 	= docker_client.containers.filter({"label" : [f"exchange={args.exchange}", f"client_id={args.client_id}", f"product_type={args.product_type}"]})
	for each_container in running_containers:
		kill(container = each_container)

	active_trades = bot_manager_client.get_trades(is_active = True)
	for each_trade in active_trades:
		pull(image_name = each_trade.docker_img)

	# Enter trades
	trades_to_enter = bot_manager_client.get_trades(is_active = True, to_close = False)
	for each_trade_to_enter in trades_to_enter:
		container_name 	= each_trade_to_enter.docker_img
		default_args 	= json.loads(each_trade_to_enter.default_args)
		entry_args 		= json.loads(each_trade_to_enter.entry_args)
		container_args	= {**default_args, **entry_args}
		labels 			= {"exchange" : args.exchange, "client_id" : args.client_id, "product_type" : args.product_type}
		run(container_name = container_name, container_args = container_args, labels = labels)

	# Exit trades
	trades_to_exit = bot_manager_client.get_trades(is_active = True, to_close = True)
	for each_trade_to_exit in trades_to_exit:
		container_name 	= each_trade_to_exit.docker_img
		default_args 	= json.loads(each_trade_to_exit.default_args)
		exit_args 		= json.loads(each_trade_to_exit.exit_args)
		container_args	= {**default_args, **exit_args}
		labels 			= {"exchange" : args.exchange, "client_id" : args.client_id, "product_type" : args.product_type}
		run(container_name = container_name, container_args = container_args, labels = labels)
		bot_manager_client.set_status(id = each_trade_to_exit.ID, is_active = False)