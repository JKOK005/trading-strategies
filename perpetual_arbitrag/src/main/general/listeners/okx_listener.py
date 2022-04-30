import argparse
import logging

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Log listener')
	parser.add_argument('--splits', type=int, nargs='?', default=os.environ.get("SPLITS"), help="Total number of splits on user IDs")
	parser.add_argument('--split_frac', type=int, nargs='?', default=os.environ.get("SPLIT_FRAC"), help="Fraction of splits that this script handles. Used for sharding and scaling")
	parser.add_argument('--db_url', type=str, nargs='?', default=os.environ.get("DB_URL"), help="URL pointing to the database")
	args 	= parser.parse_args()

	EXCHANGE = "okx"
	