import argparse
import docker
import json
import os
import re
import logging
from db.JobRankerClient import JobRankerClient
from db.JobConfigClient import JobConfigClient
from db.DockerImageClient import DockerImageClient
from time import sleep

"""
All docker jobs will have the following labels:
- user_id = user ID of user running on the exchange
- exchange = exchange for trading currency
- asset_type = spot_perp eg .
- first_asset = first asset symbol
- second_asset = second asset symbol
"""

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

def get_containers_with_no_position(all_containers):
	containers_with_no_position = []
	for each_container in all_containers:
		each_container_logs = each_container.logs(tail = 100).decode("utf-8")
		last_held_position 	= re.findall("TradePosition.[a-zA-Z_]+", each_container_logs)[-1]
		if "no_position_taken" in last_held_position.lower():
			containers_with_no_position.append(each_container)
	return containers_with_no_position

"""
python3 main/intra_exchange/manager/arbitrag_manager.py \
--user_id 1 \
--exchange kucoin \
--asset_type spot-perp \
--jobs 3 \
--db_url postgresql://arbitrag_bot:arbitrag@localhost:5432/arbitrag \
--poll_interval_s 86400
"""

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Arbitrag manager')
	parser.add_argument('--user_id', type=str, nargs='?', default=os.environ.get("USER_ID"), help="User ID")
	parser.add_argument('--exchange', type=str, nargs='?', default=os.environ.get("EXCHANGE"), help="Exchange for trading")
	parser.add_argument('--asset_type', type=str, nargs='?', default=os.environ.get("ASSET_TYPE"), help="spot-perp / spot-future / future-perp")
	parser.add_argument('--jobs', type=int, nargs='?', default=os.environ.get('JOBS'), help="Number of currency pairs to trade")
	parser.add_argument('--db_url', type=str, nargs='?', default=os.environ.get("DB_URL"), help="URL pointing to the database")
	parser.add_argument('--poll_interval_s', type=int, nargs='?', default=os.environ.get("POLL_INTERVAL_S"), help='Poll interval in seconds')
	args 	= parser.parse_args()

	logging.info(f"Starting arbitrag manager with the following params: {args}")

	job_ranker_client 	= JobRankerClient(db_url = args.db_url).create_session()
	job_config_client 	= JobConfigClient(db_url = args.db_url).create_session()
	docker_image_client = DockerImageClient(db_url = args.db_url).create_session()

	jobs_to_run 		= job_ranker_client.fetch_jobs_ranked(exchange = args.exchange, asset_type = args.asset_type, top_N = args.jobs)
	active_containers	= docker_client.containers.list(filters = {"label" : [	f"user_id={args.user_id}",
																				f"exchange={args.exchange}",
																				f"asset_type={args.asset_type}"]})

	containers_with_no_position 	= get_containers_with_no_position(all_containers = active_containers)
	containers_with_position_count 	= len(active_containers) - len(containers_with_no_position)
	new_containers_to_create_count 	= args.jobs - containers_with_position_count

	for each_conainer_with_no_position in containers_with_no_position:
		kill(each_conainer_with_no_position)

	while len(jobs_to_run) > 0 and new_containers_to_create_count > 0:
		next_job_to_run 	= jobs_to_run.pop(0)
		docker_image_name 	= docker_image_client.get_img_name(exchange = args.exchange, asset_pair = args.asset_type)
		docker_args 		= job_config_client.get_exit_config(user_id = args.user_id, exchange = args.exchange, asset_type = args.asset_type, 
																first_asset = next_job_to_run.first_asset, second_asset = next_job_to_run.second_asset)
		labels = {	"user_id" : args.user_id, "exchange" : args.exchange, "asset_type" : args.asset_type, 
					"first_asset" : each_job_for_entry.first_asset, "second_asset" : each_job_for_entry.second_asset}
		run(container_name = docker_image_name, container_args = docker_args, labels = labels)
		new_containers_to_create_count -= 1