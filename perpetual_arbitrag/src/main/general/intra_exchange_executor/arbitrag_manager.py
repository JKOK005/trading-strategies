import argparse
import docker
import json
import os
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
- status = "entry" or "exit"
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

def get_jobs_for_entry(all_jobs_to_run):
	"""
	Returns JobRank objects for new entry
	"""
	return list(filter each_job_to_run: not docker_client.containers.list(filters = {"label" : [f"user_id={args.user_id}",
																								f"exchange={each_job_to_run.exchange}",
																								f"asset_type={each_job_to_run.asset_type}",
																								f"first_asset={each_job_to_run.first_asset}",
																								f"second_asset={each_job_to_run.second_asset}",
																								"status=entry"]}), 
				all_jobs_to_run)

def get_containers_to_exit(all_jobs_to_run):
	"""
	Returns docker containers to exit
	"""
	containers_on_entry = docker_client.containers.list(filters = {"label" : [	f"user_id={args.user_id}", 
																				f"exchange={args.exchange}", 
																				f"asset_type={args.asset_type}",
																				"status=entry"]})
	
	containers_on_exit 	= []
	for each_container in containers_on_entry:
		to_exit = True
		for each_job_to_run in all_jobs_to_run:
			if each_container.labels["first_asset"] == each_job_to_run.first_asset and each_container.labels["second_asset"] == each_job_to_run.second_asset:
				to_exit = False
				break
		containers_to_exit.append(each_container) if to_exit else None
	return containers_on_exit

def get_containers_to_kill():
	"""
	Returns docker containers to kill

	Containers to be killed are those that are already marked as exit
	"""
	return docker_client.containers.list(filters = 	{"label" : [f"user_id={args.user_id}",
																f"exchange={args.exchange}",
																f"asset_type={args.asset_type}",
																"status=exit"]})

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

	containers_to_kill 	= get_containers_to_kill()
	for each_container_to_kill in containers_to_kill:
		kill(container = each_container_to_kill)

	containers_to_exit 	= get_containers_to_exit(all_jobs_to_run = jobs_to_run)
	for each_container_to_exit in containers_to_exit:
		docker_image_name 	= docker_image_client.get_img_name(exchange = args.exchange, asset_pair = args.asset_type)
		docker_args 		= job_config_client.get_exit_config(user_id = args.user_id, exchange = args.exchange, asset_type = args.asset_type, 
																first_asset = each_container_to_exit.labels["first_asset"], second_asset = each_container_to_exit.labels["second_asset"])
		labels 	= each_container_to_exit.labels
		labels["status"] = "exit"

		run(container_name = docker_image_name, container_args = docker_args, labels = labels)
		kill(container = each_container_to_exit)

	jobs_for_entry  = get_jobs_for_entry(all_jobs_to_run = jobs_to_run)
	for each_job_for_entry in jobs_for_entry:
		docker_image_name 	= docker_image_client.get_img_name(exchange = args.exchange, asset_pair = args.asset_type)
		docker_args 		= job_config_client.get_exit_config(user_id = args.user_id, exchange = args.exchange, asset_type = args.asset_type, 
																first_asset = each_job_for_entry.first_asset, second_asset = each_job_for_entry.second_asset)
		labels = {
			"user_id" 		: args.user_id,
			"exchange" 		: args.exchange,
			"asset_type" 	: args.asset_type,
			"first_asset" 	: each_job_for_entry.first_asset,
			"second_asset" 	: each_job_for_entry.second_asset,
			"status" 		: "entry"
		}

		run(container_name = docker_image_name, container_args = docker_args, labels = labels)