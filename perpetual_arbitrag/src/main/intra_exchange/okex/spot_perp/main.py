import argparse
import os
import logging
from time import sleep
from clients.OkexApiClient import OkexApiClient
from clients.SqlClient import SqlClient
from execution.BotExecution import BotExecution
from execution.BotSimulatedExecution import BotSimulatedExecution
from strategies.SingleTradeArbitrag import SingleTradeArbitrag, ExecutionDecision

"""
python3 main/intra_exchange/okex/spot_perp/main.py \
--spot_trading_pair BTC-USDT \
--perpetual_trading_pair XBTUSDTM \
--api_key xxx \
--api_secret_key xxx \
--api_passphrase xxx \
--order_type market \
--spot_entry_vol 0.01 \
--max_spot_vol 0.1 \
--perpetual_entry_lot_size 10 \
--max_perpetual_lot_size 100 \
--entry_gap_frac 0.01 \
--profit_taking_frac 0.005 \
--poll_interval_s 60 \
--funding_interval_s 1800 \
--retry_timeout_s 30 \
--db_url xxx \
--fake_orders
"""

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Spot - Futures arbitrag trading')
	parser.add_argument('--spot_trading_pair', type=str, nargs='?', default=os.environ.get("SPOT_TRADING_PAIR"), help='Spot trading pair symbol as defined by exchange')
	parser.add_argument('--perpetual_trading_pair', type=str, nargs='?', default=os.environ.get("PERPETUAL_TRADING_PAIR"), help='Perpetual trading pair symbol as defined by exchange')
	parser.add_argument('--order_type', type=str, nargs='?', default=os.environ.get("ORDER_TYPE"), help='Either limit or market orders')
	parser.add_argument('--poll_interval_s', type=int, nargs='?', default=os.environ.get("POLL_INTERVAL_S"), help='Poll interval in seconds')
	parser.add_argument('--spot_entry_vol', type=float, nargs='?', default=os.environ.get("SPOT_ENTRY_VOL"), help='Volume of spot assets for each entry')
	parser.add_argument('--max_spot_vol', type=float, nargs='?', default=os.environ.get("MAX_SPOT_VOL"), help='Max volume of spot assets to long / short')
	parser.add_argument('--perpetual_entry_lot_size', type=int, nargs='?', default=os.environ.get("PERPETUAL_ENTRY_LOT_SIZE"), help='Lot size for each entry for perpetual')
	parser.add_argument('--max_perpetual_lot_size', type=int, nargs='?', default=os.environ.get("MAX_PERPETUAL_LOT_SIZE"), help='Max lot size to long / short perpetual')
	parser.add_argument('--entry_gap_frac', type=float, nargs='?', default=os.environ.get("ENTRY_GAP_FRAC"), help='Fraction of price difference which we can consider making an entry')
	parser.add_argument('--profit_taking_frac', type=float, nargs='?', default=os.environ.get("PROFIT_TAKING_FRAC"), help='Fraction of price difference which we can consider taking profit. Recommended to set this value lower than entry_gap_frac')
	parser.add_argument('--api_key', type=str, nargs='?', default=os.environ.get("API_KEY"), help='Exchange api key')
	parser.add_argument('--api_secret_key', type=str, nargs='?', default=os.environ.get("API_SECRET_KEY"), help='Exchange secret api key')
	parser.add_argument('--api_passphrase', type=str, nargs='?', default=os.environ.get("API_PASSPHRASE"), help='Exchange api passphrase')
	parser.add_argument('--funding_interval_s', type=int, nargs='?', default=os.environ.get("FUNDING_INTERVAL_S"), help='Seconds before funding snapshot timings which we consider valid to account for estimated funding rate P/L')
	parser.add_argument('--retry_timeout_s', type=int, nargs='?', default=os.environ.get("RETRY_TIMEOUT_S"), help='Retry main loop after specified seconds')
	parser.add_argument('--db_url', type=str, nargs='?', default=os.environ.get("DB_URL"), help="URL pointing to the database. If None, the program will not connect to a DB and zero-state execution is assumed")
	parser.add_argument('--db_reset', action='store_true', help='Resets the state in the database to zero-state. This means all spot / futures lot sizes are set to 0')
	parser.add_argument('--fake_orders', action='store_true', help='If present, we fake order placements. This is used for simulation purposes only')
	parser.add_argument('--funding_rate_disable', action='store_true', help='If present, disable the effects of funding rate in the trade decision')
	args 	= parser.parse_args()

	logging.basicConfig(level = logging.INFO)
	logging.info(f"Starting Okex arbitrag bot with the following params: {args}")

	client 	= OkexApiClient(api_key 			= args.api_key, 
							api_secret_key 		= args.api_secret_key, 
							passphrase 			= args.api_passphrase, 
							funding_rate_enable = not args.funding_rate_disable
						)

	import IPython
	IPython.embed()