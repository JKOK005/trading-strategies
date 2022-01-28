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

	assert 	args.spot_entry_vol >= client.get_spot_min_volume(symbol = args.spot_trading_pair) and \
			args.futures_entry_lot_size >= client.get_futures_min_lot_size(symbol = args.futures_trading_pair), \
			"Minimum entry size not satisfied."

	if args.db_url is not None:
		logging.info(f"State management at {args.db_url}")
		db_client 	= SqlClient(url = args.db_url, spot_symbol = args.spot_trading_pair, futures_symbol = args.futures_trading_pair).start_session()
		db_client.create_entry() if not db_client.is_exists() else None
		db_client.set_position(spot_volume = 0, futures_lot_size = 0) if args.db_reset else None
		(current_spot_vol, current_futures_lot_size) = db_client.get_position()
	else:
		logging.warning(f"Zero state execution as no db_url detected")
		(current_spot_vol, current_futures_lot_size) = (0, 0)

	trade_strategy 	= SingleTradeArbitrag(	spot_symbol 				= args.spot_trading_pair,
											current_spot_vol 			= current_spot_vol,
											max_spot_vol 				= args.max_spot_vol,
											futures_symbol 				= args.futures_trading_pair,
											current_futures_lot_size 	= current_futures_lot_size,
											max_futures_lot_size		= args.max_futures_lot_size,
										)

	bot_executor 	= BotSimulatedExecution(api_client = client) if args.fake_orders else BotExecution(api_client = client)

	while True:
		try:
			if 	args.order_type == "limit":
				spot_price 		= client.get_spot_trading_price(symbol = args.spot_trading_pair)
				futures_price 	= client.get_futures_trading_price(symbol = args.futures_trading_pair)
				(futures_funding_rate, futures_estimated_funding_rate) = client.get_futures_effective_funding_rate(	symbol = args.futures_trading_pair, 
																													seconds_before = args.funding_interval_s)
				decision 		= trade_strategy.trade_decision(spot_price 				= spot_price, 
																futures_price 			= futures_price,
																futures_funding_rate 	= futures_funding_rate,
																futures_estimated_funding_rate = futures_estimated_funding_rate,
																entry_threshold 		= args.entry_gap_frac,
																take_profit_threshold 	= args.profit_taking_frac
															)
				logging.info(f"Spot price: {spot_price}, Futures price: {futures_price}")			

			elif args.order_type == "market":
				(avg_spot_bid, avg_spot_ask) 		= client.get_spot_average_bid_ask_price(symbol = args.spot_trading_pair, size = args.spot_entry_vol)
				(avg_futures_bid, avg_futures_ask) 	= client.get_futures_average_bid_ask_price(symbol = args.futures_trading_pair, size = args.futures_entry_lot_size)
				(futures_funding_rate, futures_estimated_funding_rate) = client.get_futures_effective_funding_rate(	symbol = args.futures_trading_pair,
																													seconds_before = args.funding_interval_s)

				decision 							= trade_strategy.bid_ask_trade_decision(spot_bid_price 			= avg_spot_bid,
																							spot_ask_price 			= avg_spot_ask,
																							futures_bid_price 		= avg_futures_bid,
																							futures_ask_price 		= avg_futures_ask,
																							futures_funding_rate 	= futures_funding_rate,
																							futures_estimated_funding_rate = futures_estimated_funding_rate,
																							entry_threshold 		= args.entry_gap_frac,
																							take_profit_threshold 	= args.profit_taking_frac
																						)
				logging.info(f"Avg spot bid: {avg_spot_bid}, asks: {avg_spot_ask} / Perpetuals bid: {avg_futures_bid}, asks: {avg_futures_ask}")
			logging.info(f"Executing trade decision: {decision}")

			# Execute orders
			new_order_execution = False

			if 	(decision == ExecutionDecision.GO_LONG_SPOT_SHORT_FUTURE) \
				or (decision == ExecutionDecision.TAKE_PROFIT_LONG_FUTURE_SHORT_SPOT):
				new_order_execution = bot_executor.long_spot_short_futures( spot_symbol 		= args.spot_trading_pair,
																			spot_order_type 	= args.order_type,
																			spot_price 			= spot_price if args.order_type == "limit" else 1,
																			spot_size 			= args.spot_entry_vol,
																			futures_symbol 		= args.futures_trading_pair,
																			futures_order_type 	= args.order_type,
																			futures_price 		= futures_price if args.order_type == "limit" else 1,
																			futures_size 		= args.futures_entry_lot_size,
																			futures_lever 		= args.futures_entry_leverage
																		)
				trade_strategy.change_asset_holdings(delta_spot = args.spot_entry_vol, delta_futures = -1 * args.futures_entry_lot_size) \
				if new_order_execution else None

			elif (decision == ExecutionDecision.GO_LONG_FUTURE_SHORT_SPOT) \
				 or (decision == ExecutionDecision.TAKE_PROFIT_LONG_SPOT_SHORT_FUTURE):
				new_order_execution = bot_executor.short_spot_long_futures( spot_symbol 		= args.spot_trading_pair,
																			spot_order_type 	= args.order_type,
																			spot_price 			= spot_price if args.order_type == "limit" else 1,
																			spot_size 			= args.spot_entry_vol,
																			futures_symbol 		= args.futures_trading_pair,
																			futures_order_type 	= args.order_type,
																			futures_price 		= futures_price if args.order_type == "limit" else 1,
																			futures_size 		= args.futures_entry_lot_size,
																			futures_lever 		= args.futures_entry_leverage
																		)
				trade_strategy.change_asset_holdings(delta_spot = -1 * args.spot_entry_vol, delta_futures = args.futures_entry_lot_size) \
				if new_order_execution else None

			if new_order_execution and args.db_url is not None:
				(current_spot_vol, current_futures_lot_size) = trade_strategy.get_asset_holdings()
				db_client.set_position(spot_volume = current_spot_vol, futures_lot_size = current_futures_lot_size)
			
			sleep(args.poll_interval_s)

		except Exception as ex:
			logging.error(ex)
			sleep(args.retry_timeout_s)

	import IPython
	IPython.embed()