import argparse
import docker
import json
import os
import logging
from db.BotManagerClient import BotManagerClient
from time import sleep

docker_client = docker.from_env()
docker_client.login(username = "jkok005")
logging.basicConfig(level = logging.INFO)

def pull(image_name: str):
	logging.info(f"Pulling {image_name}")
	docker_client.images.pull(image_name)

def run(container_name: str, container_args, labels):
	pull(image_name = container_name)
	logging.info(f"Starting {container_name}")
	return docker_client.containers.run(image = container_name, environment = container_args, labels = labels, 
										detach = True, network = "host")

def kill(container):
	logging.info(f"Killing container {container}")
	return container.kill()

"""
python3 main/intra_exchange/manager/arbitrag_manager.py \
--user_id 1 \
--db_url postgresql://arbitrag_bot:arbitrag@localhost:5432/arbitrag
"""

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Arbitrag manager')
	parser.add_argument('--user_id', type=str, nargs='?', default=os.environ.get("USER_ID"), help="User ID")
	parser.add_argument('--db_url', type=str, nargs='?', default=os.environ.get("DB_URL"), help="URL pointing to the database")
	parser.add_argument('--poll_interval_s', type=int, nargs='?', default=os.environ.get("POLL_INTERVAL_S"), help='Poll interval in seconds')
	args 	= parser.parse_args()

	logging.info(f"Starting arbitrag manager with the following params: {args}")

	bot_manager_client 	= BotManagerClient( url = args.db_url, 
											user_id = args.user_id).create_session()

	while(True):
		# Kill all running containers
		# Bug fix - We will kill containers that are meant to close the trade, even if the trade has not been fully closed yet.
		running_containers 	= docker_client.containers.list(filters = {"label" : [f"user_id={args.user_id}"]})
		for each_container in running_containers:
			kill(container = each_container)

		trades_to_enter = bot_manager_client.get_jobs(is_active = True, to_close = False)
		trades_to_exit 	= bot_manager_client.get_jobs(is_active = True, to_close = True)

		# Enter trades
		for each_trade_to_enter in trades_to_enter:
			container_name 	= bot_manager_client.get_image(image_id = each_trade_to_enter.arb_img_id)
			default_args 	= json.loads(each_trade_to_enter.default_args)
			entry_args 		= json.loads(each_trade_to_enter.entry_args)
			secret_args 	= json.loads(bot_manager_client.get_secret_keys(secret_id = each_trade_to_enter.secret_id))
			container_args	= {**default_args, **entry_args, **secret_args}
			labels 			= {"user_id" : args.user_id}
			run(container_name = container_name, container_args = container_args, labels = labels)

		# Exit trades
		for each_trade_to_exit in trades_to_exit:
			container_name 	= bot_manager_client.get_image(image_id = each_trade_to_exit.arb_img_id	)
			default_args 	= json.loads(each_trade_to_exit.default_args)
			exit_args 		= json.loads(each_trade_to_exit.exit_args)
			secret_args 	= json.loads(bot_manager_client.get_secret_keys(secret_id = each_trade_to_exit.secret_id))
			container_args	= {**default_args, **exit_args, **secret_args}
			labels 			= {"user_id" : args.user_id}
			run(container_name = container_name, container_args = container_args, labels = labels)

		sleep(args.poll_interval_s)