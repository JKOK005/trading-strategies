import argparse
import logging
import os
from clients.KucoinApiClient import KucoinApiClient
from db.FutureClients import FutureClients
from db.SpotClients import SpotClients
from execution.SpotFutureBotExecution import SpotFutureBotExecution, SpotFutureSimulatedBotExecution
from strategies.SpotPerpArbitrag import SpotPerpArbitrag, SpotPerpTradePosition, SpotPerpExecutionDecision
from time import sleep

"""
python3 main/intra_exchange/kucoin/spot_perp/main.py \
--client_id 123asd \
--spot_trading_pair BTC-USDT \
--futures_trading_pair XBTUSDTM \
--spot_api_key xxx \
--spot_api_secret_key xxx \
--spot_api_passphrase xxx \
--futures_api_key xxx \
--futures_api_secret_key xxx \
--futures_api_passphrase xxx \
--order_type market \
--spot_entry_vol 0.01 \
--max_spot_vol 0.1 \
--futures_entry_lot_size 10 \
--max_futures_lot_size 100 \
--futures_entry_leverage 1 \
--entry_gap_frac 0.01 \
--profit_taking_frac 0.005 \
--poll_interval_s 60 \
--current_funding_interval_s 1800 \
--estimated_funding_interval_s 1800 \
--retry_timeout_s 30 \
--funding_rate_disable 0 \
--db_url xxx \
--use_sandbox \
--fake_orders
"""

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Spot - Futures arbitrag trading')
	parser.add_argument('--client_id', type=str, nargs='?', default=os.environ.get("CLIENT_ID"), help='Client ID registered on the exchange')
	parser.add_argument('--spot_trading_pair', type=str, nargs='?', default=os.environ.get("SPOT_TRADING_PAIR"), help='Spot trading pair symbol as defined by exchange')
	parser.add_argument('--futures_trading_pair', type=str, nargs='?', default=os.environ.get("FUTURES_TRADING_PAIR"), help='Futures trading pair symbol as defined by exchange')
	parser.add_argument('--order_type', type=str, nargs='?', default=os.environ.get("ORDER_TYPE"), help='Either limit or market orders')
	parser.add_argument('--poll_interval_s', type=int, nargs='?', default=os.environ.get("POLL_INTERVAL_S"), help='Poll interval in seconds')
	parser.add_argument('--spot_entry_vol', type=float, nargs='?', default=os.environ.get("SPOT_ENTRY_VOL"), help='Volume of spot assets for each entry')
	parser.add_argument('--max_spot_vol', type=float, nargs='?', default=os.environ.get("MAX_SPOT_VOL"), help='Max volume of spot assets to long / short')
	parser.add_argument('--futures_entry_lot_size', type=int, nargs='?', default=os.environ.get("FUTURES_ENTRY_LOT_SIZE"), help='Lot size for each entry for futures')
	parser.add_argument('--max_futures_lot_size', type=int, nargs='?', default=os.environ.get("MAX_FUTURES_LOT_SIZE"), help='Max lot size to long / short futures')
	parser.add_argument('--futures_entry_leverage', type=int, nargs='?', default=os.environ.get("FUTURES_ENTRY_LEVERAGE"), help='Leverage for each entry for futures')
	parser.add_argument('--entry_gap_frac', type=float, nargs='?', default=os.environ.get("ENTRY_GAP_FRAC"), help='Fraction of price difference which we can consider making an entry')
	parser.add_argument('--profit_taking_frac', type=float, nargs='?', default=os.environ.get("PROFIT_TAKING_FRAC"), help='Fraction of price difference which we can consider taking profit. Recommended to set this value lower than entry_gap_frac')
	parser.add_argument('--spot_api_key', type=str, nargs='?', default=os.environ.get("SPOT_API_KEY"), help='Spot exchange api key')
	parser.add_argument('--spot_api_secret_key', type=str, nargs='?', default=os.environ.get("SPOT_API_SECRET_KEY"), help='Spot exchange secret api key')
	parser.add_argument('--spot_api_passphrase', type=str, nargs='?', default=os.environ.get("SPOT_API_PASSPHRASE"), help='Spot exchange api passphrase')
	parser.add_argument('--futures_api_key', type=str, nargs='?', default=os.environ.get("FUTURES_API_KEY"), help='Futures exchange api key')
	parser.add_argument('--futures_api_secret_key', type=str, nargs='?', default=os.environ.get("FUTURES_API_SECRET_KEY"), help='Futures exchange secret api key')
	parser.add_argument('--futures_api_passphrase', type=str, nargs='?', default=os.environ.get("FUTURES_API_PASSPHRASE"), help='Futures exchange api passphrase')
	parser.add_argument('--current_funding_interval_s', type=int, nargs='?', default=os.environ.get("CURRENT_FUNDING_INTERVAL_S"), help='Seconds before funding snapshot timings which we consider valid to account for current funding rate P/L')
	parser.add_argument('--estimated_funding_interval_s', type=int, nargs='?', default=os.environ.get("ESTIMATED_FUNDING_INTERVAL_S"), help='Seconds before funding snapshot timings which we consider valid to account for estimated funding rate P/L')
	parser.add_argument('--retry_timeout_s', type=int, nargs='?', default=os.environ.get("RETRY_TIMEOUT_S"), help='Retry main loop after specified seconds')
	parser.add_argument('--db_url', type=str, nargs='?', default=os.environ.get("DB_URL"), help="URL pointing to the database. If None, the program will not connect to a DB and zero-state execution is assumed")
	parser.add_argument('--funding_rate_disable', type=int, nargs='?', choices={0, 1}, default=os.environ.get("FUNDING_RATE_DISABLE"), help='If 1, disable the effects of funding rate in the trade decision. If 0, otherwise')
	parser.add_argument('--db_reset', action='store_true', help='Resets the state in the database to zero-state. This means all spot / futures lot sizes are set to 0')
	parser.add_argument('--use_sandbox', action='store_true', help='If present, trades in Sandbox env. Else, trades in REAL env')
	parser.add_argument('--fake_orders', action='store_true', help='If present, we fake order placements. This is used for simulation purposes only')
	args 	= parser.parse_args()

	logging.basicConfig(level = logging.INFO)
	logging.info(f"Starting Arbitrag bot with the following params: {args}")

	client 			= KucoinApiClient(	spot_client_api_key 			= args.spot_api_key, 
										spot_client_api_secret_key 		= args.spot_api_secret_key, 
										spot_client_pass_phrase 		= args.spot_api_passphrase, 
										futures_client_api_key 			= args.futures_api_key, 
										futures_client_api_secret_key 	= args.futures_api_secret_key, 
										futures_client_pass_phrase 		= args.futures_api_passphrase,
										sandbox 						= args.use_sandbox,
										funding_rate_enable 			= args.funding_rate_disable == 0
									)

	assert 	args.spot_entry_vol >= client.get_spot_min_volume(symbol = args.spot_trading_pair), "Minimum spot entry size not satisfied."
	assert 	args.futures_entry_lot_size >= client.get_futures_min_lot_size(symbol = args.futures_trading_pair), "Minimum futures entry size not satisfied."

	if args.db_url is not None:
		logging.info(f"State management at {args.db_url}")

		strategy_id 		= SpotPerpArbitrag.get_strategy_id()
		client_id 			= args.client_id

		db_spot_client 		= SpotClients(url = args.db_url, strategy_id = strategy_id, client_id = client_id, exchange = "kucoin", symbol = args.spot_trading_pair, units = "vol").create_session()
		db_futures_client 	= FutureClients(url = args.db_url, strategy_id = strategy_id, client_id = client_id, exchange = "kucoin", symbol = args.futures_trading_pair, units = "lot").create_session()

		db_spot_client.create_entry() if not db_spot_client.is_exists() else None
		db_futures_client.create_entry() if not db_futures_client.is_exists() else None
		
		db_spot_client.set_position(size = 0) if args.db_reset else None
		db_futures_client.set_position(size = 0) if args.db_reset else None
		
		(current_spot_vol, current_futures_lot_size) = (db_spot_client.get_position(), db_futures_client.get_position())
	else:
		logging.warning(f"Zero state execution as no db_url detected")
		(current_spot_vol, current_futures_lot_size) = (0, 0)

	trade_strategy 	= SpotPerpArbitrag(	spot_symbol 			= args.spot_trading_pair,
										current_spot_vol 		= current_spot_vol,
										max_spot_vol 			= args.max_spot_vol,
										perp_symbol 			= args.futures_trading_pair,
										current_perp_lot_size 	= current_futures_lot_size,
										max_perp_lot_size		= args.max_futures_lot_size,
									)

	bot_executor 	= SpotFutureSimulatedBotExecution(api_client = client) if args.fake_orders else SpotFutureBotExecution(api_client = client)

	while True:
		try:
			if 	args.order_type == "limit":
				spot_price 		= client.get_spot_trading_price(symbol = args.spot_trading_pair)
				futures_price 	= client.get_futures_trading_price(symbol = args.futures_trading_pair)
				(futures_funding_rate, futures_estimated_funding_rate) = client.get_futures_effective_funding_rate(	symbol = args.futures_trading_pair, 
																													seconds_before_current = args.current_funding_interval_s,
																													seconds_before_estimated = args.estimated_funding_interval_s)
				
				decision 		= trade_strategy.trade_decision(spot_bid_price 				= spot_price, 
																spot_ask_price 				= spot_price,
																perp_bid_price 				= futures_price,
																perp_ask_price 				= futures_price,
																perp_funding_rate 			= futures_funding_rate,
																perp_estimated_funding_rate = futures_estimated_funding_rate,
																entry_threshold 			= args.entry_gap_frac,
																take_profit_threshold 		= args.profit_taking_frac
															)
				logging.info(f"Spot price: {spot_price}, Futures price: {futures_price}")			

			elif args.order_type == "market":
				(avg_spot_bid, avg_spot_ask) 		= client.get_spot_average_bid_ask_price(symbol = args.spot_trading_pair, size = args.spot_entry_vol)
				(avg_futures_bid, avg_futures_ask) 	= client.get_futures_average_bid_ask_price(symbol = args.futures_trading_pair, size = args.futures_entry_lot_size)
				(futures_funding_rate, futures_estimated_funding_rate) = client.get_futures_effective_funding_rate(	symbol = args.futures_trading_pair,
																													seconds_before_current = args.current_funding_interval_s,
																													seconds_before_estimated = args.estimated_funding_interval_s)

				decision 		= trade_strategy.trade_decision(spot_bid_price 				= avg_spot_bid,
																spot_ask_price 				= avg_spot_ask,
																perp_bid_price 				= avg_futures_bid,
																perp_ask_price 				= avg_futures_ask,
																perp_funding_rate 			= futures_funding_rate,
																perp_estimated_funding_rate = futures_estimated_funding_rate,
																entry_threshold 			= args.entry_gap_frac,
																take_profit_threshold 		= args.profit_taking_frac
															)
				logging.info(f"Avg spot bid: {avg_spot_bid}, asks: {avg_spot_ask} / Perpetuals bid: {avg_futures_bid}, asks: {avg_futures_ask}")
			logging.info(f"Executing trade decision: {decision}")

			# Execute orders
			new_order_execution = False

			if 	(decision == SpotPerpExecutionDecision.GO_LONG_SPOT_SHORT_PERP) \
				or (decision == SpotPerpExecutionDecision.TAKE_PROFIT_LONG_PERP_SHORT_SPOT):
				new_order_execution = bot_executor.long_spot_short_futures(	spot_params 	= { "symbol" 		: args.spot_trading_pair, 
																								"order_type" 	: args.order_type,
																								"price" 		: spot_price if args.order_type == "limit" else 1,
																								"size" 			: args.spot_entry_vol,
																							},

																			future_params 	= {	"symbol" 		: args.futures_trading_pair, 
																								"order_type" 	: args.order_type, 
																								"price" 		: futures_price if args.order_type == "limit" else 1,
																								"size" 			: args.futures_entry_lot_size,
																								"lever" 		: args.futures_entry_leverage,
																							},
																		)
				trade_strategy.change_asset_holdings(delta_spot = args.spot_entry_vol, delta_perp = -1 * args.futures_entry_lot_size) \
				if new_order_execution else None

			elif (decision == SpotPerpExecutionDecision.GO_LONG_PERP_SHORT_SPOT) \
				or (decision == SpotPerpExecutionDecision.TAKE_PROFIT_LONG_SPOT_SHORT_PERP):
				new_order_execution = bot_executor.short_spot_long_futures(	spot_params 	= {	"symbol" 		: args.spot_trading_pair, 
																								"order_type" 	: args.order_type,
																								"price" 		: spot_price if args.order_type == "limit" else 1,
																								"size" 			: args.spot_entry_vol,
																							},

																			future_params 	= {	"symbol" 		: args.futures_trading_pair, 
																								"order_type" 	: args.order_type, 
																								"price" 		: futures_price if args.order_type == "limit" else 1,
																								"size" 			: args.futures_entry_lot_size,
																								"lever" 		: args.futures_entry_leverage,
																							},
																		)
				trade_strategy.change_asset_holdings(delta_spot = -1 * args.spot_entry_vol, delta_perp = args.futures_entry_lot_size) \
				if new_order_execution else None

			if new_order_execution and args.db_url is not None:
				(current_spot_vol, current_futures_lot_size) = trade_strategy.get_asset_holdings()
				db_spot_client.set_position(size = current_spot_vol)
				db_futures_client.set_position(size = current_futures_lot_size)

			if 	(new_order_execution) or \
				(decision == SpotPerpExecutionDecision.NO_DECISION):
				sleep(args.poll_interval_s)
			
			else:
				raise Exception(f"Order execution failed - Status: {new_order_execution}, Decision: {decision}")

		except Exception as ex:
			logging.error(ex)
			sleep(args.retry_timeout_s)