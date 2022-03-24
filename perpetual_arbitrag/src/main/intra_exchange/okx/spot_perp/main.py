import argparse
import os
import logging
from clients.OkxApiClientWS import OkxApiClientWS
from db.SpotClients import SpotClients
from db.PerpetualClients import PerpetualClients
from execution.SpotPerpetualBotExecution import SpotPerpetualBotExecution, SpotPerpetualSimulatedBotExecution
from feeds.CryptoStoreRedisFeeds import CryptoStoreRedisFeeds
from strategies.SingleTradeArbitrag import SingleTradeArbitrag, ExecutionDecision
from time import sleep

"""
python3 main/intra_exchange/okx/spot_perp/main.py \
--client_id 123asd \
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
--perpetual_leverage 1 \
--entry_gap_frac 0.01 \
--profit_taking_frac 0.005 \
--poll_interval_s 60 \
--current_funding_interval_s 1800 \
--estimated_funding_interval_s 1800 \
--funding_rate_disable 0 \
--retry_timeout_s 30 \
--db_url xxx \
--feed_url xxx \
--feed_port xxx \
--feed_latency_s 0.05 \
--fake_orders
"""

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='Spot - perpetual arbitrag trading')
	parser.add_argument('--client_id', type=str, nargs='?', default=os.environ.get("CLIENT_ID"), help='Client ID registered on the exchange')
	parser.add_argument('--spot_trading_pair', type=str, nargs='?', default=os.environ.get("SPOT_TRADING_PAIR"), help='Spot trading pair symbol as defined by exchange')
	parser.add_argument('--perpetual_trading_pair', type=str, nargs='?', default=os.environ.get("PERPETUAL_TRADING_PAIR"), help='Perpetual trading pair symbol as defined by exchange')
	parser.add_argument('--order_type', type=str, nargs='?', default=os.environ.get("ORDER_TYPE"), help='Either limit or market orders')
	parser.add_argument('--poll_interval_s', type=float, nargs='?', default=os.environ.get("POLL_INTERVAL_S"), help='Poll interval in seconds')
	parser.add_argument('--spot_entry_vol', type=float, nargs='?', default=os.environ.get("SPOT_ENTRY_VOL"), help='Volume of spot assets for each entry')
	parser.add_argument('--max_spot_vol', type=float, nargs='?', default=os.environ.get("MAX_SPOT_VOL"), help='Max volume of spot assets to long / short')
	parser.add_argument('--perpetual_entry_lot_size', type=int, nargs='?', default=os.environ.get("PERPETUAL_ENTRY_LOT_SIZE"), help='Lot size for each entry for perpetual')
	parser.add_argument('--max_perpetual_lot_size', type=int, nargs='?', default=os.environ.get("MAX_PERPETUAL_LOT_SIZE"), help='Max lot size to long / short perpetual')
	parser.add_argument('--perpetual_leverage', type=int, nargs='?', default=os.environ.get("PERPETUAL_LEVERAGE"), help='Leverage for each entry for perpetual')
	parser.add_argument('--entry_gap_frac', type=float, nargs='?', default=os.environ.get("ENTRY_GAP_FRAC"), help='Fraction of price difference which we can consider making an entry')
	parser.add_argument('--profit_taking_frac', type=float, nargs='?', default=os.environ.get("PROFIT_TAKING_FRAC"), help='Fraction of price difference which we can consider taking profit. Recommended to set this value lower than entry_gap_frac')
	parser.add_argument('--api_key', type=str, nargs='?', default=os.environ.get("API_KEY"), help='Exchange api key')
	parser.add_argument('--api_secret_key', type=str, nargs='?', default=os.environ.get("API_SECRET_KEY"), help='Exchange secret api key')
	parser.add_argument('--api_passphrase', type=str, nargs='?', default=os.environ.get("API_PASSPHRASE"), help='Exchange api passphrase')
	parser.add_argument('--current_funding_interval_s', type=int, nargs='?', default=os.environ.get("CURRENT_FUNDING_INTERVAL_S"), help='Seconds before funding snapshot timings which we consider valid to account for current funding rate P/L')
	parser.add_argument('--estimated_funding_interval_s', type=int, nargs='?', default=os.environ.get("ESTIMATED_FUNDING_INTERVAL_S"), help='Seconds before funding snapshot timings which we consider valid to account for estimated funding rate P/L')
	parser.add_argument('--retry_timeout_s', type=float, nargs='?', default=os.environ.get("RETRY_TIMEOUT_S"), help='Retry main loop after specified seconds')
	parser.add_argument('--funding_rate_disable', type=int, nargs='?', choices={0, 1}, default=os.environ.get("FUNDING_RATE_DISABLE"), help='If 1, disable the effects of funding rate in the trade decision. If 0, otherwise')
	parser.add_argument('--db_url', type=str, nargs='?', default=os.environ.get("DB_URL"), help="URL pointing to the database. If None, the program will not connect to a DB and zero-state execution is assumed")
	parser.add_argument('--db_reset', action='store_true', help='Resets the state in the database to zero-state. This means all spot / perpetual lot sizes are set to 0')
	parser.add_argument('--feed_url', type=str, nargs='?', default=os.environ.get("FEED_URL"), help="URL pointing to price feed channel")
	parser.add_argument('--feed_port', type=str, nargs='?', default=os.environ.get("FEED_PORT"), help="Port pointing to price feed channel")
	parser.add_argument('--feed_latency_s', type=float, nargs='?', default=os.environ.get("FEED_LATENCY_S"), help="Permissible latency between fetches of data from price feed")
	parser.add_argument('--fake_orders', action='store_true', help='If present, we fake order placements. This is used for simulation purposes only')
	args 	= parser.parse_args()

	logging.basicConfig(format='%(asctime)s %(levelname)-8s %(module)s.%(funcName)s %(lineno)d - %(message)s',
    					level=logging.INFO,
    					datefmt='%Y-%m-%d %H:%M:%S')

	logging.info(f"Starting Okx arbitrag bot with the following params: {args}")

	feed_client = CryptoStoreRedisFeeds(redis_url 	= args.feed_url,
										redis_port 	= args.feed_port,
										permissible_latency_s = args.feed_latency_s
									).connect()

	client 	= OkxApiClientWS(api_key 				= args.api_key, 
							 api_secret_key 		= args.api_secret_key, 
							 passphrase 			= args.api_passphrase,
							 feed_client 			= feed_client,
							 funding_rate_enable 	= args.funding_rate_disable == 0
							)

	client.make_connection()
	client.set_perpetual_leverage(symbol = args.perpetual_trading_pair, leverage = args.perpetual_leverage)

	assert 	args.spot_entry_vol >= client.get_spot_min_volume(symbol = args.spot_trading_pair), "Minimum spot entry size not satisfied."
	assert 	args.perpetual_entry_lot_size >= client.get_perpetual_min_lot_size(symbol = args.perpetual_trading_pair), "Minimum perpetual entry size not satisfied."

	if args.db_url is not None:
		logging.info(f"State management at {args.db_url}")

		strategy_id = SingleTradeArbitrag.get_strategy_id()
		client_id 	= args.client_id

		db_spot_client 			= SpotClients(url = args.db_url, strategy_id = strategy_id, client_id = client_id, exchange = "okx", symbol = args.spot_trading_pair, units = "vol").create_session()
		db_perpetual_clients 	= PerpetualClients(url = args.db_url, strategy_id = strategy_id, client_id = client_id, exchange = "okx", symbol = args.perpetual_trading_pair, units = "lot").create_session()
		
		db_spot_client.create_entry() if not db_spot_client.is_exists() else None
		db_perpetual_clients.create_entry() if not db_perpetual_clients.is_exists() else None
		
		db_spot_client.set_position(size = 0) if args.db_reset else None
		db_perpetual_clients.set_position(size = 0) if args.db_reset else None

		(current_spot_vol, current_perpetual_lot_size) = (db_spot_client.get_position(), db_perpetual_clients.get_position())
	else:
		logging.warning(f"Zero state execution as no db_url detected")
		(current_spot_vol, current_perpetual_lot_size) = (0, 0)

	trade_strategy 	= SingleTradeArbitrag(	spot_symbol 				= args.spot_trading_pair,
											current_spot_vol 			= current_spot_vol,
											max_spot_vol 				= args.max_spot_vol,
											futures_symbol 				= args.perpetual_trading_pair,
											current_futures_lot_size 	= current_perpetual_lot_size,
											max_futures_lot_size		= args.max_perpetual_lot_size,
										)

	bot_executor 	= SpotPerpetualSimulatedBotExecution(api_client = client) if args.fake_orders else SpotPerpetualBotExecution(api_client = client)

	while True:
		try:
			if 	args.order_type == "limit":
				(perpetual_funding_rate, perpetual_estimated_funding_rate) = client.get_perpetual_effective_funding_rate(	symbol = args.perpetual_trading_pair, 
																															seconds_before_current = args.current_funding_interval_s,
																															seconds_before_estimated = args.estimated_funding_interval_s)
				spot_price 		= client.get_spot_trading_price(symbol = args.spot_trading_pair)
				perpetual_price = client.get_perpetual_trading_price(symbol = args.perpetual_trading_pair)
				
				decision 		= trade_strategy.trade_decision(spot_price 						= spot_price, 
																futures_price 					= perpetual_price,
																futures_funding_rate 			= perpetual_funding_rate,
																futures_estimated_funding_rate 	= perpetual_estimated_funding_rate,
																entry_threshold 				= args.entry_gap_frac,
																take_profit_threshold 			= args.profit_taking_frac
															)
				price_str 		= f"Spot price: {spot_price}, perpetual price: {perpetual_price}"		

			elif args.order_type == "market":
				(perpetual_funding_rate, perpetual_estimated_funding_rate) = client.get_perpetual_effective_funding_rate(	symbol = args.perpetual_trading_pair,
																															seconds_before_current = args.current_funding_interval_s,
																															seconds_before_estimated = args.estimated_funding_interval_s)
				(avg_spot_bid, avg_spot_ask) = client.get_spot_average_bid_ask_price(symbol = args.spot_trading_pair, size = args.spot_entry_vol)
				(avg_perpetual_bid, avg_perpetual_ask) 	= client.get_perpetual_average_bid_ask_price(symbol = args.perpetual_trading_pair, size = args.perpetual_entry_lot_size)
				
				decision 		= trade_strategy.bid_ask_trade_decision(spot_bid_price 			= avg_spot_bid,
																		spot_ask_price 			= avg_spot_ask,
																		futures_bid_price 		= avg_perpetual_bid,
																		futures_ask_price 		= avg_perpetual_ask,
																		futures_funding_rate 	= perpetual_funding_rate,
																		futures_estimated_funding_rate = perpetual_estimated_funding_rate,
																		entry_threshold 		= args.entry_gap_frac,
																		take_profit_threshold 	= args.profit_taking_frac
																	)
				price_str 		= f"Spot bid/ask: {(avg_spot_bid, avg_spot_ask)}, Perpetual bid/ask: {(avg_perpetual_bid, avg_perpetual_ask)}"
			
			funding_str = f"Current/Est Funding: {(perpetual_funding_rate, perpetual_estimated_funding_rate)}"
			logging.info(f"{decision} - {price_str} - {funding_str}")

			# Execute orders
			new_order_execution = False

			if decision == ExecutionDecision.TAKE_PROFIT_LONG_FUTURE_SHORT_SPOT:
				new_order_execution = bot_executor.long_spot_short_perpetual(	spot_params = {
																					"symbol" 	 		: args.spot_trading_pair, 
																					"order_type" 		: args.order_type, 
																					"price" 	 		: spot_price if args.order_type == "limit" else 1,
																					"size" 		 		: args.spot_entry_vol,
																					"target_currency" 	: "base_ccy",
																				},
																				perpetual_params = {
																					"symbol" 	 	: args.perpetual_trading_pair,
																					"position_side" : "long",
																					"order_type" 	: args.order_type, 
																					"price" 	 	: perpetual_price if args.order_type == "limit" else 1,
																					"size" 		 	: args.perpetual_entry_lot_size,
																				}
																		)

				trade_strategy.change_asset_holdings(delta_spot = args.spot_entry_vol, delta_futures = -1 * args.perpetual_entry_lot_size) \
				if new_order_execution else None

			elif decision == ExecutionDecision.TAKE_PROFIT_LONG_SPOT_SHORT_FUTURE:
				new_order_execution = bot_executor.short_spot_long_perpetual(	spot_params = {
																					"symbol" 	 		: args.spot_trading_pair, 
																					"order_type" 		: args.order_type, 
																					"price" 	 		: spot_price if args.order_type == "limit" else 1,
																					"size" 		 		: args.spot_entry_vol,
																					"target_currency" 	: "base_ccy" 
																				},
																				perpetual_params = {
																					"symbol" 	 	: args.perpetual_trading_pair,
																					"position_side" : "short",
																					"order_type" 	: args.order_type, 
																					"price" 	 	: perpetual_price if args.order_type == "limit" else 1,
																					"size" 		 	: args.perpetual_entry_lot_size,
																				}
																		)

				trade_strategy.change_asset_holdings(delta_spot = -1 * args.spot_entry_vol, delta_futures = args.perpetual_entry_lot_size) \
				if new_order_execution else None

			elif decision == ExecutionDecision.GO_LONG_SPOT_SHORT_FUTURE:
				new_order_execution = bot_executor.long_spot_short_perpetual(	spot_params = {
																					"symbol" 	 		: args.spot_trading_pair, 
																					"order_type" 		: args.order_type, 
																					"price" 	 		: spot_price if args.order_type == "limit" else 1,
																					"size" 		 		: args.spot_entry_vol,
																					"target_currency" 	: "base_ccy" 
																				},
																				perpetual_params = {
																					"symbol" 	 	: args.perpetual_trading_pair,
																					"position_side" : "short",
																					"order_type" 	: args.order_type, 
																					"price" 	 	: perpetual_price if args.order_type == "limit" else 1,
																					"size" 		 	: args.perpetual_entry_lot_size,
																				}
																		)

				trade_strategy.change_asset_holdings(delta_spot = args.spot_entry_vol, delta_futures = -1 * args.perpetual_entry_lot_size) \
				if new_order_execution else None

			elif decision == ExecutionDecision.GO_LONG_FUTURE_SHORT_SPOT:
				new_order_execution = bot_executor.short_spot_long_perpetual(	spot_params = {
																					"symbol" 	 		: args.spot_trading_pair, 
																					"order_type" 		: args.order_type, 
																					"price" 	 		: spot_price if args.order_type == "limit" else 1,
																					"size" 		 		: args.spot_entry_vol,
																					"target_currency" 	: "base_ccy" 
																				},
																				perpetual_params = {
																					"symbol" 	 	: args.perpetual_trading_pair,
																					"position_side" : "long",
																					"order_type" 	: args.order_type, 
																					"price" 	 	: perpetual_price if args.order_type == "limit" else 1,
																					"size" 		 	: args.perpetual_entry_lot_size,
																				}
																		)

				trade_strategy.change_asset_holdings(delta_spot = -1 * args.spot_entry_vol, delta_futures = args.perpetual_entry_lot_size) \
				if new_order_execution else None

			if new_order_execution and args.db_url is not None:
				(current_spot_vol, current_perpetual_lot_size) = trade_strategy.get_asset_holdings()
				db_spot_client.set_position(size = current_spot_vol)
				db_perpetual_clients.set_position(size = current_perpetual_lot_size)

			if 	(new_order_execution) or \
				(decision == ExecutionDecision.NO_DECISION):
				sleep(args.poll_interval_s)
			
			else:
				raise Exception(f"Order execution failed - Status: {new_order_execution}, Decision: {decision}")

		except Exception as ex:
			logging.error(ex)
			sleep(args.retry_timeout_s)

		finally:
			try:
				client.maintain_connection()
			except Exception as ex:
				logging.error("Restoring connection to WS server")
				client.make_connection()