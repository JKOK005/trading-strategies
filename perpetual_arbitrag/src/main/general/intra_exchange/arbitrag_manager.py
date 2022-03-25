import argparse
import docker
import json
import os
import re
import redis
import logging
from db.DockerImageClient import DockerImageClient
from db.JobRankerClient import JobRankerClient
from db.JobConfigClient import JobConfigClient
from db.SecretsClient import SecretsClient
from datetime import datetime, timedelta
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
	logging.info(f"Starting {container_name}, args: {container_args}")
	return docker_client.containers.run(image = container_name, environment = container_args, labels = labels, 
										detach = True, network = "host")

def kill(container):
	logging.info(f"Killing container {container}")
	return container.kill()

def get_containers_with_no_position(all_containers):
	containers_with_no_position = []
	for each_container in all_containers:
		each_container_logs = each_container.logs(tail = 1000).decode("utf-8")
		position_history 	= re.findall("TradePosition.[a-zA-Z_]+", each_container_logs)

		if position_history:
			last_held_position 	= position_history[-1]
			if "no_position_taken" in last_held_position.lower():
				containers_with_no_position.append(each_container)
	return containers_with_no_position

def get_containers_to_kill(jobs, all_containers):
	to_kill = []
	for each_container in all_containers:
		_is_kill = True
		for each_job in jobs:
			if 	each_container.labels["first_asset"] == each_job.first_asset and \
				each_container.labels["second_asset"] == each_job.second_asset:
				_is_kill = False
				break
		
		to_kill.append(each_container) if _is_kill else None
	return to_kill

def get_jobs_to_create(jobs, all_containers):
	to_create = []
	for each_job in jobs:
		_to_create = True
		for each_container in all_containers:
			if 	each_container.labels["first_asset"] == each_job.first_asset and \
				each_container.labels["second_asset"] == each_job.second_asset:
				_to_create = False
				break
		
		to_create.append(each_job) if _to_create else None
	return to_create

"""
python3 ./main/general/intra_exchange/arbitrag_manager.py \
--user_id 1 \
--exchange test-okx \
--asset_type spot-perp \
--jobs 1 \
--job_interval_s 10 \
--arb_score_min 0.002 \
--db_url postgresql://arbitrag_bot:arbitrag@localhost:5432/arbitrag \
--message_url localhost \
--message_port 6379
"""

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Arbitrag manager')
	parser.add_argument('--user_id', type=str, nargs='?', default=os.environ.get("USER_ID"), help="User ID")
	parser.add_argument('--exchange', type=str, nargs='?', default=os.environ.get("EXCHANGE"), help="Exchange for trading")
	parser.add_argument('--asset_type', type=str, nargs='?', default=os.environ.get("ASSET_TYPE"), help="spot-perp / spot-future / future-perp")
	parser.add_argument('--jobs', type=int, nargs='?', default=os.environ.get('JOBS'), help="Number of currency pairs to trade")
	parser.add_argument('--job_interval_s', type=int, nargs='?', default=os.environ.get("JOB_INTERVAL_S"), help="Interval between launch sequences in seconds")
	parser.add_argument('--arb_score_min', type=float, nargs='?', default=os.environ.get("ARB_SCORE_MIN"), help="If arb score exists above this threshold, we will consider it for running.")
	parser.add_argument('--db_url', type=str, nargs='?', default=os.environ.get("DB_URL"), help="URL pointing to the database")
	parser.add_argument('--message_url', type=str, nargs='?', default=os.environ.get("MESSAGE_URL"), help="URL pointing to the messaging queue, such as redis")
	parser.add_argument('--message_port', type=str, nargs='?', default=os.environ.get("MESSAGE_PORT"), help="Port of the messaging queue app")
	args 	= parser.parse_args()

	logging.info(f"Starting arbitrag manager with the following params: {args}")

	docker_image_client = DockerImageClient(db_url = args.db_url).create_session()
	job_ranker_client 	= JobRankerClient(db_url = args.db_url).create_session()
	job_config_client 	= JobConfigClient(db_url = args.db_url).create_session()
	secrets_client 		= SecretsClient(db_url = args.db_url).create_session()

	message_client 		= redis.Redis(host = args.message_url, port = args.message_port, charset="utf-8", decode_responses=True)
	message_pubsub 		= message_client.pubsub()
	messaging_channel 	= f'arb/{args.exchange}/{args.asset_type}'
	message_pubsub.subscribe(messaging_channel)

	current_time 		= datetime.now()
	first_run 			= True

	for _ in message_pubsub.listen():
		logging.info("Scanning jobs")

		if datetime.now() - current_time >= timedelta(seconds = args.job_interval_s) or first_run:
			jobs_to_run 		= job_ranker_client.fetch_jobs_ranked(exchange = args.exchange, asset_type = args.asset_type, top_N = args.jobs)
			jobs_to_run 		= list(filter(lambda each_job: each_job.effective_arb >= args.arb_score_min, jobs_to_run))

			active_containers	= docker_client.containers.list(filters = {"label" : [	f"user_id={args.user_id}",
																						f"exchange={args.exchange}",
																						f"asset_type={args.asset_type}"]})

			containers_with_no_position 	= get_containers_with_no_position(all_containers = active_containers)
			containers_to_kill 				= get_containers_to_kill(jobs = jobs_to_run, all_containers = containers_with_no_position)
			jobs_to_create 					= get_jobs_to_create(jobs = jobs_to_run, all_containers = active_containers)
			
			containers_with_position_count 					= len(active_containers) - len(containers_with_no_position)
			containers_with_no_position_and_active_count 	= len(containers_with_no_position) - len(containers_to_kill)
			new_containers_to_create_count 					= args.jobs - containers_with_position_count - containers_with_no_position_and_active_count

			for each_container_to_kill in containers_to_kill:
				kill(each_container_to_kill)

			while len(jobs_to_create) > 0 and new_containers_to_create_count > 0:
				next_job_to_run 	= jobs_to_create.pop(0)
				docker_image_name 	= docker_image_client.get_img_name(exchange = args.exchange, asset_pair = args.asset_type)
				
				docker_args 		= job_config_client.get_job_config(user_id = args.user_id, exchange = args.exchange, asset_type = args.asset_type, 
																	   first_asset = next_job_to_run.first_asset, second_asset = next_job_to_run.second_asset)

				client_secrets 		= secrets_client.get_secrets(user_id = args.user_id, exchange = args.exchange)
				
				labels = {	"user_id" : args.user_id, "exchange" : args.exchange, "asset_type" : args.asset_type, 
							"first_asset" : next_job_to_run.first_asset, "second_asset" : next_job_to_run.second_asset}
				
				run(container_name = docker_image_name, container_args = {**docker_args, **client_secrets}, labels = labels)
				new_containers_to_create_count -= 1
				current_time = datetime.now()
				
			first_run = False