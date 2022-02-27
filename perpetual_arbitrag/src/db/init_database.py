import argparse
from SpotClients import SpotInfoTable
from FutureClients import FutureInfoTable
from PerpetualClients import PerpetualInfoTable
from DockerImageClient import ArbitragDockerImages
from JobConfigClient import JobConfig
from UsersClient import Users
from SecretsClient import SecretKeys
from sqlalchemy import create_engine

"""
python3 db/init_database.py \
--db_url xxx
"""

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Initialize arbitrag trading databases')
	parser.add_argument('--db_url', type=str, nargs='?', default=None, help="URL pointing to the database.")
	args 	= parser.parse_args()
	engine 	= create_engine(url = args.db_url)
	
	SpotInfoTable.__table__.create(engine, checkfirst=True)
	FutureInfoTable.__table__.create(engine, checkfirst=True)
	PerpetualInfoTable.__table__.create(engine, checkfirst=True)

	Users.__table__.create(engine, checkfirst=True)
	SecretKeys.__table__.create(engine, checkfirst=True)
	ArbitragDockerImages.__table__.create(engine, checkfirst=True)
	JobConfig.__table__.create(engine, checkfirst=True)