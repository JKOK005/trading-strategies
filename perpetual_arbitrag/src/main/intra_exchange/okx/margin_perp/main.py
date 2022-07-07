import argparse
import os
import logging
from clients.OkxApiClientWS import OkxApiClientWS
from datetime import datetime, timedelta
from db.MarginClients import MarginClients
from db.PerpetualClients import PerpetualClients
from execution.MarginPerpetualBotExecution import MarginPerpetualBotExecution
from feeds.CryptoStoreRedisFeeds import CryptoStoreRedisFeeds
from strategies.MarginPerpArbitrag import MarginPerpArbitrag, MarginPerpExecutionDecision
from time import sleep

"""
python3 main/intra_exchange/okx/margin_perp/main.py \
--client_id 123asd \
--margin_trading_pair BTC-USDT \
--perpetual_trading_pair BTC-USDT-SWAP \
--api_key xxx \
--api_secret_key xxx \
--api_passphrase xxx \
--order_type market \
--margin_entry_vol 0.01 \
--max_margin_vol 0.1 \
--margin_leverage 1 \
--margin_tax_rate 0.001 \
--margin_loan_period_hr 24 \
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
--feed_latency_s 0.05
"""

if __name__ == "__main__":
	parser 	= argparse.ArgumentParser(description='margin - perpetual arbitrag trading')
	parser.add_argument('--client_id', type=str, nargs='?', default=os.environ.get("CLIENT_ID"), help='Client ID registered on the exchange')
	parser.add_argument('--margin_trading_pair', type=str, nargs='?', default=os.environ.get("MARGIN_TRADING_PAIR"), help='Margin trading pair symbol as defined by exchange')
	parser.add_argument('--perpetual_trading_pair', type=str, nargs='?', default=os.environ.get("PERPETUAL_TRADING_PAIR"), help='Perpetual trading pair symbol as defined by exchange')
	parser.add_argument('--order_type', type=str, nargs='?', default=os.environ.get("ORDER_TYPE"), help='Either limit or market orders')
	parser.add_argument('--poll_interval_s', type=float, nargs='?', default=os.environ.get("POLL_INTERVAL_S"), help='Poll interval in seconds')
	parser.add_argument('--margin_entry_vol', type=float, nargs='?', default=os.environ.get("MARGIN_ENTRY_VOL"), help='Volume of margin assets for each entry')
	parser.add_argument('--max_margin_vol', type=float, nargs='?', default=os.environ.get("MAX_MARGIN_VOL"), help='Max volume of margin assets to long / short')
	parser.add_argument('--margin_leverage', type=float, nargs='?', default=os.environ.get("MARGIN_LEVERAGE"), help='Leverage for each entry for margin')
	parser.add_argument('--margin_tax_rate', type=float, nargs='?', default=os.environ.get("MARGIN_TAX_RATE"), help='Tax rate by the exchange, needed to offset the entry / exit amount of the asset to maintain a balanced position.')
	parser.add_argument('--margin_loan_period_hr', type=int, nargs='?', default=os.environ.get("MARGIN_LOAN_PERIOD_HR"), help='How long are we going to hold the margin position for? This will impact the funding rate for the margined asset.')
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
	parser.add_argument('--db_reset', action='store_true', help='Resets the state in the database to zero-state. This means all margin / perpetual lot sizes are set to 0')
	parser.add_argument('--feed_url', type=str, nargs='?', default=os.environ.get("FEED_URL"), help="URL pointing to price feed channel")
	parser.add_argument('--feed_port', type=str, nargs='?', default=os.environ.get("FEED_PORT"), help="Port pointing to price feed channel")
	parser.add_argument('--feed_latency_s', type=float, nargs='?', default=os.environ.get("FEED_LATENCY_S"), help="Permissible latency between fetches of data from price feed")
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

	(quote_ccy, base_ccy) = args.margin_trading_pair.split("-")
	client.make_connection()
	client.set_margin_leverage(symbol = args.margin_trading_pair, ccy = base_ccy, leverage = args.margin_leverage)
	client.set_perpetual_leverage(symbol = args.perpetual_trading_pair, leverage = args.perpetual_leverage)

	assert 	args.margin_entry_vol >= client.get_margin_min_volume(symbol = args.margin_trading_pair), "Minimum margin entry size not satisfied."
	assert 	args.perpetual_entry_lot_size >= client.get_perpetual_min_lot_size(symbol = args.perpetual_trading_pair), "Minimum perpetual entry size not satisfied."

	if args.db_url is not None:
		logging.info(f"State management at {args.db_url}")

		strategy_id = MarginPerpArbitrag.get_strategy_id()
		client_id 	= args.client_id

		db_margin_client 	 = MarginClients(url = args.db_url, strategy_id = strategy_id, client_id = client_id, exchange = "okx", symbol = args.margin_trading_pair, units = "vol").create_session()
		db_perpetual_clients = PerpetualClients(url = args.db_url, strategy_id = strategy_id, client_id = client_id, exchange = "okx", symbol = args.perpetual_trading_pair, units = "lot").create_session()
		
		db_margin_client.create_entry() if not db_margin_client.is_exists() else None
		db_perpetual_clients.create_entry() if not db_perpetual_clients.is_exists() else None
		
		db_margin_client.set_position(size = 0) if args.db_reset else None
		db_perpetual_clients.set_position(size = 0) if args.db_reset else None

		(current_margin_vol, current_perpetual_lot_size) = (db_margin_client.get_position(), db_perpetual_clients.get_position())
	else:
		logging.warning(f"Zero state execution as no db_url detected")
		(current_margin_vol, current_perpetual_lot_size) = (0, 0)

	trade_strategy 	= MarginPerpArbitrag(margin_symbol 			 = args.margin_trading_pair,
										 current_margin_position = current_margin_vol,
										 max_margin_position 	 = args.max_margin_vol,
										 perp_symbol 			 = args.perpetual_trading_pair,
										 current_perp_position 	 = current_perpetual_lot_size,
										 max_perp_position		 = args.max_perpetual_lot_size,
										)

	bot_executor 	= MarginPerpetualBotExecution(api_client = client)

	#TODO: @JKOK005 Implement interest rate refresh feature
	margin_quote_funding_rate = client.get_margin_effective_funding_rate( ccy = quote_ccy, 
																		 loan_period_hrs = args.margin_loan_period_hr)

	margin_base_funding_rate = client.get_margin_effective_funding_rate(ccy = base_ccy, 
																		loan_period_hrs = args.margin_loan_period_hr)

	(perpetual_funding_rate, perpetual_estimated_funding_rate) = client.get_perpetual_effective_funding_rate(symbol = args.perpetual_trading_pair, 
																											 seconds_before_current = args.current_funding_interval_s,
																											 seconds_before_estimated = args.estimated_funding_interval_s)

	while True:
		try:
			if 	args.order_type == "limit":
				margin_price 	= client.get_margin_trading_price(symbol = args.margin_trading_pair)
				perpetual_price = client.get_perpetual_trading_price(symbol = args.perpetual_trading_pair)
				
				decision 		= trade_strategy.trade_decision(
									margin_bid_price = margin_price,
									margin_ask_price = margin_price,
									margin_quote_interest_rate = margin_quote_funding_rate,
									margin_base_interest_rate = margin_base_funding_rate,
									perp_bid_price = perpetual_price,
									perp_ask_price = perpetual_price,
									perp_funding_rate = perpetual_funding_rate,
									perp_estimated_funding_rate = perpetual_estimated_funding_rate,
									entry_threshold = args.entry_gap_frac,
									take_profit_threshold = args.profit_taking_frac
							 	)

				price_str 			= f"Margin price: {margin_price}, perpetual price: {perpetual_price}"		
				margin_long_size 	= args.margin_entry_vol * margin_price

			elif args.order_type == "market":				
				(avg_margin_bid, avg_margin_ask, margin_ts) 			= client.get_margin_average_bid_ask_price(symbol = args.margin_trading_pair, size = args.margin_entry_vol)
				(avg_perpetual_bid, avg_perpetual_ask, perpetual_ts) 	= client.get_perpetual_average_bid_ask_price(symbol = args.perpetual_trading_pair, size = args.perpetual_entry_lot_size)
				
				decision 		= trade_strategy.trade_decision(
									margin_bid_price = avg_margin_bid,
									margin_ask_price = avg_margin_ask,
									margin_quote_interest_rate = margin_quote_funding_rate,
									margin_base_interest_rate = margin_base_funding_rate,
									perp_bid_price = avg_perpetual_bid,
									perp_ask_price = avg_perpetual_ask,
									perp_funding_rate = perpetual_funding_rate,
									perp_estimated_funding_rate = perpetual_estimated_funding_rate,
									entry_threshold = args.entry_gap_frac,
									take_profit_threshold = args.profit_taking_frac
							 	)
				price_str 			= f"Margin bid/ask: {(avg_margin_bid, avg_margin_ask)}, Perpetual bid/ask: {(avg_perpetual_bid, avg_perpetual_ask)}"
				margin_long_size 	= args.margin_entry_vol * avg_margin_ask
				assert datetime.utcnow() - min(datetime.utcfromtimestamp(margin_ts), datetime.utcfromtimestamp(perpetual_ts)) <= timedelta(milliseconds = args.feed_latency_s * 1000), "Trade latency too large" 

			funding_str = f"Margin quote - base interests: {margin_quote_funding_rate} / {margin_base_funding_rate} - Current/Est Funding: {(perpetual_funding_rate, perpetual_estimated_funding_rate)}"
			logging.info(f"{decision} - {price_str} - {funding_str}")

			# Execute orders
			new_order_execution = False

			import IPython
			IPython.embed()

			if decision == MarginPerpExecutionDecision.TAKE_PROFIT_LONG_PERP_SHORT_MARGIN:
				new_order_execution = bot_executor.long_margin_short_perpetual(	margin_params = {
																					"symbol" 	 		: args.margin_trading_pair,
																					"ccy" 				: "USDT",
																					"trade_mode" 		: "cross",
																					"order_type" 		: args.order_type, 
																					"price" 	 		: margin_price if args.order_type == "limit" else 1,
																					"entry_size" 		: margin_long_size,
																					"revert_size" 		: args.margin_entry_vol,
																				},
																				perpetual_params = {
																					"symbol" 	 		: args.perpetual_trading_pair,
																					"position_side" 	: "long",
																					"order_type" 		: args.order_type, 
																					"price" 	 		: perpetual_price if args.order_type == "limit" else 1,
																					"size" 		 		: args.perpetual_entry_lot_size,
																				}
																		)

				trade_strategy.change_asset_holdings(delta_margin = args.margin_entry_vol, delta_perp = -1 * args.perpetual_entry_lot_size) \
				if new_order_execution else None

			elif decision == MarginPerpExecutionDecision.TAKE_PROFIT_LONG_MARGIN_SHORT_PERP:
				new_order_execution = bot_executor.short_margin_long_perpetual(	margin_params = {
																					"symbol" 	 		: args.margin_trading_pair,
																					"ccy" 				: "USDT",
																					"trade_mode" 		: "cross",
																					"order_type" 		: args.order_type, 
																					"price" 	 		: margin_price if args.order_type == "limit" else 1,
																					"entry_size" 		: args.margin_entry_vol * (1 - args.margin_tax_rate),
																					"revert_size" 		: margin_long_size,
																				},
																				perpetual_params = {
																					"symbol" 	 	: args.perpetual_trading_pair,
																					"position_side" : "short",
																					"order_type" 	: args.order_type, 
																					"price" 	 	: perpetual_price if args.order_type == "limit" else 1,
																					"size" 		 	: args.perpetual_entry_lot_size,
																				}
																		)

				trade_strategy.change_asset_holdings(delta_margin = -1 * args.margin_entry_vol, delta_perp = args.perpetual_entry_lot_size) \
				if new_order_execution else None

			elif decision == MarginPerpExecutionDecision.GO_LONG_MARGIN_SHORT_PERP:
				new_order_execution = bot_executor.long_margin_short_perpetual(	margin_params = {
																					"symbol" 	 		: args.margin_trading_pair,
																					"ccy" 				: "USDT",
																					"trade_mode" 		: "cross",
																					"order_type" 		: args.order_type, 
																					"price" 	 		: margin_price if args.order_type == "limit" else 1,
																					"entry_size" 		: margin_long_size,
																					"revert_size" 		: args.margin_entry_vol,
																				},
																				perpetual_params = {
																					"symbol" 	 	: args.perpetual_trading_pair,
																					"position_side" : "short",
																					"order_type" 	: args.order_type, 
																					"price" 	 	: perpetual_price if args.order_type == "limit" else 1,
																					"size" 		 	: args.perpetual_entry_lot_size,
																				}
																		)

				trade_strategy.change_asset_holdings(delta_margin = args.margin_entry_vol, delta_perp = -1 * args.perpetual_entry_lot_size) \
				if new_order_execution else None

			elif decision == MarginPerpExecutionDecision.GO_LONG_PERP_SHORT_MARGIN:
				new_order_execution = bot_executor.short_margin_long_perpetual(	margin_params = {
																					"symbol" 	 		: args.margin_trading_pair,
																					"ccy" 				: "USDT",
																					"trade_mode" 		: "cross",
																					"order_type" 		: args.order_type, 
																					"price" 	 		: margin_price if args.order_type == "limit" else 1,
																					"entry_size" 		: args.margin_entry_vol * (1 - args.margin_tax_rate),
																					"revert_size" 		: margin_long_size,
																				},
																				perpetual_params = {
																					"symbol" 	 	: args.perpetual_trading_pair,
																					"position_side" : "long",
																					"order_type" 	: args.order_type, 
																					"price" 	 	: perpetual_price if args.order_type == "limit" else 1,
																					"size" 		 	: args.perpetual_entry_lot_size,
																				}
																		)

				trade_strategy.change_asset_holdings(delta_margin = -1 * args.margin_entry_vol, delta_perp = args.perpetual_entry_lot_size) \
				if new_order_execution else None

			if new_order_execution and args.db_url is not None:
				(current_margin_vol, current_perpetual_lot_size) = trade_strategy.get_asset_holdings()
				db_margin_client.set_position(size = current_margin_vol)
				db_perpetual_clients.set_position(size = current_perpetual_lot_size)

			if 	(new_order_execution) or \
				(decision == MarginPerpExecutionDecision.NO_DECISION):
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