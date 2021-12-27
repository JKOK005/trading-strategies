import argparse
from clients.DataAccessClients import BASE
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

"""
python3 init_database.py \
--db_url xxx
"""

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Spot - Futures arbitrag trading')
	parser.add_argument('--db_url', type=str, nargs='?', default=None, help="URL pointing to the database. If None, the program will not connect to a DB and zero-state execution is assumed.")
	args 	= parser.parse_args()

	engine 	= create_engine(url = args.db_url)
	BASE.metadata.create_all(engine)
