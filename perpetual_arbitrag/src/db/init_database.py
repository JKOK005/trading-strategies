import argparse
from AssetNamesClient import AssetNames
from SpotClients import SpotInfoTable
from FutureClients import FutureInfoTable
from PerpetualClients import PerpetualInfoTable
from MarginClients import MarginInfoTable
from DockerImageClient import ArbitragDockerImages
from JobConfigClient import JobConfig
from JobRankerClient import JobRanking
from UsersClient import Users
from TradeLogsClient import TradeLogs
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
	MarginInfoTable.__table__.create(engine, checkfirst=True)

	AssetNames.__table__.create(engine, checkfirst=True)
	Users.__table__.create(engine, checkfirst=True)
	SecretKeys.__table__.create(engine, checkfirst=True)
	ArbitragDockerImages.__table__.create(engine, checkfirst=True)
	JobConfig.__table__.create(engine, checkfirst=True)
	JobRanking.__table__.create(engine, checkfirst=True)
	TradeLogs.__table__.create(engine, checkfirst=True)