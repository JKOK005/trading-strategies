import datetime
import logging
import sys
from okex.swap_api import SwapAPI
from okex.spot_api import SpotAPI
from clients.ExchangeSpotClients import ExchangeSpotClients
from clients.ExchangePerpetualClients import ExchangePerpetualClients

class OkexApiClient(ExchangeSpotClients, ExchangePerpetualClients):
	spot_client = None
	perp_client = None
	logger 		= logging.getLogger('OkexApiClient')

	okex_funding_rate_snapshot_times = ["04:00", "12:00", "20:00"]

	def __init__(self, 	api_key: str, 
						api_secret_key: str,
						passphrase: str,
						funding_rate_enable: bool
				):
		
		spot_client 	= SpotAPI(	api_key = api_key, 
									api_secret_key = api_secret_key, 
									passphrase = passphrase)

		perp_client 	= SwapAPI(	api_key = api_key, 
									api_secret_key = api_secret_key, 
									passphrase = passphrase)

		self.funding_rate_enable = funding_rate_enable
		self.logger.info(f"Enable for funding rate computation set to {funding_rate_enable}")
		return

	def get_spot_trading_account_details(self, currency: str):
		"""
		Retrieves spot trading details
		"""
		spot_accounts 	= self.spot_client.get_account_info()
		return list(filter(lambda x: x["type"] == "trade" and x["currency"] == currency, spot_accounts))[0]

	def get_perpetual_trading_account_details(self, currency: str):
		"""
		Retrieves perpetual trading account details
		"""
		return self.perp_client.get_coin_account(underlying = currency)

	def get_spot_trading_price(self, symbol: str):
		"""
		Retrieves current spot pricing for trading symbol
		"""
		asset_info 		= self.spot_client.get_specific_ticker(instrument_id = symbol)
		return asset_info["last"]

	def get_perpetual_trading_price(self, symbol: str):
		"""
		Retrieves current perpetual price for trading symbol
		"""
		perp_info 		= self.perp_client.get_specific_ticker(instrument_id = symbol)
		return perp_info["last"]

	def get_spot_min_volume(self, symbol: str):
		"""
		Retrieves minimum order volume for spot trading symbol
		"""
		all_spot_info 	= self.spot_client.get_ticker()
		spot_info 		= next(filter(lambda x: x["instrument_id"] == symbol, all_spot_info))
		return float(spot_info["min_size"])

	def get_perpetual_min_lot_size(self, symbol: str):
		"""
		Retrieves minimum order lot size for perpetual trading symbol

		# Based on definition in https://www.okx.com/docs/en/#swap-swap---orders, minimum contract size is 1
		"""
		return 1

	def _compute_average_margin_purchase_price(self, price_qty_pairs_ordered: [float, float], size: float):
		"""
		We will read pricing - qty data from the first entry of the list. 

		This logic will differ, depending on whether we want to go long / short on the asset. 
		As such, the ordering of the price-qty pairs in the list has to be handled properly by the user. 
		"""
		all_trade_qty 		= size
		trade_amt 			= 0
		executed_trade_qty 	= 0
		for each_price_qty_pairs in price_qty_pairs_ordered:
			if all_trade_qty < 0:
				break
			else:
				[price, qty] 	=  each_price_qty_pairs
				trade_qty 		=  min(all_trade_qty, qty)
				trade_amt 	 	+= price * trade_qty
				all_trade_qty 	-= trade_qty
				executed_trade_qty += trade_qty
		return trade_amt / executed_trade_qty

	def _compute_average_bid_price(self, bids: [[float, float]], size: float):
		# Sell into bids starting from the highest to the lowest.
		_bids 	= sorted(bids, key = lambda x: x[0], reverse = True)
		if len(_bids) > 0:
			return self._compute_average_margin_purchase_price(price_qty_pairs_ordered = _bids, size = size)
		return 0

	def _compute_average_ask_price(self, asks: [[float, float]], size: float):
		# Buy into asks starting from the lowest to the highest.
		_asks 	= sorted(asks, key = lambda x: x[0], reverse = False)
		if len(_asks) > 0:
			return self._compute_average_margin_purchase_price(price_qty_pairs_ordered = _asks, size = size)
		return sys.maxsize

	def get_spot_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the spot asset, assuming that we intend to trade at a given volume.

		# TODO: Assert that number of liquidated orders in returned bid_ask_orders list is not needed in computation
		"""
		bid_ask_orders 		= self.spot_client.get_depth(instrument_id = symbol, size = 100)
		bids 				= bid_ask_orders["bids"]
		bids 				= list(map(lambda x: [float(x[0]), float(x[1])], bids))
		average_bid_price 	= self._compute_average_bid_price(bids = bids, size = size)

		asks 				= bid_ask_orders["asks"]
		asks 				= list(map(lambda x: [float(x[0]), float(x[1])], asks))
		average_sell_price 	= self._compute_average_ask_price(asks = asks, size = size)
		return (average_bid_price, average_sell_price)

	def get_perpetual_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the perpetual asset, assuming that we intend to trade at a given lot size. 
		"""
		bid_ask_orders 		= self.perp_client.get_depth(instrument_id = symbol, size = 100)
		bids 				= bid_ask_orders["bids"]
		bids 				= list(map(lambda x: [float(x[0]), float(x[1])], bids))
		average_bid_price 	= self._compute_average_bid_price(bids = bids, size = size)

		asks 				= bid_ask_orders["asks"]
		asks 				= list(map(lambda x: [float(x[0]), float(x[1])], asks))
		average_sell_price 	= self._compute_average_ask_priclientce(asks = asks, size = size)
		return (average_bid_price, average_sell_price)

	def get_spot_open_orders(self, symbol: str):
		"""
		Gets information of all open spot orders by the user
		"""
		resp = self.spot_client.get_orders_pending(instrument_id = symbol)
		return resp

	def get_perpetual_open_orders(self, symbol: str):
		"""
		Gets information of all open future orders by the user
		"""
		resp = self.perp_client.get_order_list(instrument_id = symbol, state = 6)
		return resp["order_info"]

	def get_spot_most_recent_open_order(self, symbol: str):
		"""
		Gets the most recent open orders for spot

		Based on https://www.okx.com/docs/en/#spot-orders_pending , the most recent order is at the first entry.
		"""
		open_orders = self.get_spot_open_orders(symbol = symbol)
		most_recent_open_order = open_orders[0] if len(open_orders) > 0 else open_orders
		return most_recent_open_order

	def get_perpetual_most_recent_open_order(self, symbol: str):
		"""
		Gets the most recent open orders for perpetual

		Based on https://www.okx.com/docs/en/#futures-list , the most recent order is at the first entry
		"""
		open_orders = self.get_perpetual_open_orders(symbol = symbol)
		most_recent_open_order = open_orders[0] if len(open_orders) > 0 else open_orders
		return most_recent_open_order

	def get_spot_fulfilled_orders(self, symbol: str):
		"""
		Gets information for all fulfilled spot orders by the user
		"""
		resp = self.spot_client.get_orders_list(instrument_id = symbol, state = 2)
		return resp

	def get_perpetual_fulfilled_orders(self, symbol: str):
		"""
		Gets information of all fulfilled future orders by the user
		"""
		resp = self.perp_client.get_order_list(instrument_id = symbol, state = 2)
		return resp

	def get_spot_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent spot trade that have been fulfilled

		Based on https://www.okx.com/docs/en/#spot-list , the most recent fulfilled order is at the first entry
		"""
		fulfilled_orders = self.get_spot_fulfilled_orders(symbol = symbol)
		most_recent_fulfilled_order = fulfilled_orders[0] if len(fulfilled_orders) > 0 else fulfilled_orders
		return most_recent_fulfilled_order

	def get_perpetual_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent perpetual trade that have been fulfilled

		Based on https://www.okx.com/docs/en/#swap-swap---list , the most recent fulfilled order is at the first entry
		"""
		fulfilled_orders = self.get_perpetual_fulfilled_orders(symbol = symbol)
		most_recent_fulfilled_order = fulfilled_orders[0] if len(fulfilled_orders) > 0 else fulfilled_orders
		return most_recent_fulfilled_order

	def get_perpetual_funding_rate(self, symbol: str):
		"""
		Gets the immediate and predicted funding rate for futures contract
		"""
		funding_rate_info = self.perp_client.get_funding_time(instrument_id = symbol)
		return (funding_rate_info["funding_rate"], funding_rate_info["estimated_rate"])

	def funding_rate_valid_interval(self, seconds_before: int):
		current_time = datetime.datetime.utcnow()
		for each_snaphsot_time in self.okex_funding_rate_snapshot_times:
			ts = datetime.datetime.strptime(each_snaphsot_time, "%H:%M")
			snapshot_timestamp = current_time.replace(hour = ts.hour, minute = ts.minute, second = 0)
			if snapshot_timestamp - timedelta(seconds = seconds_before) <= current_time and current_time <= snapshot_timestamp:
				return True
		return False

	def get_perpetual_effective_funding_rate(self, symbol: str, seconds_before: int):
		"""
		Gets the effective funding rate for perpetual contract.

		Effective funding rate takes into account a variety of factors to decide on the funding rate.

		1) If we are not within a valid funding interval, then the estimated funding rates are 0.
		2) If funding rate computation has been disabled, then all rates are 0.
		"""
		(funding_rate, estimated_funding_rate) = (0, 0)
		if self.funding_rate_enable: 
			if self.funding_rate_valid_interval(seconds_before = seconds_before):
				(funding_rate, estimated_funding_rate) = self.get_perpetual_funding_rate(symbol = symbol)
			else:
				(funding_rate, _) = self.get_perpetual_funding_rate(symbol = symbol)
		self.logger.info(f"Funding rate: {funding_rate}, Estimated funding rate: {estimated_funding_rate}")
		return (funding_rate, estimated_funding_rate)
 
	def place_spot_order(self, 	symbol: str, 
								order_type: str, 
								order_side: str, 
								price: int,
								size: float,
								*args, **kwargs):
		"""
		order_type 	- Either limit or market
		order_side 	- Either buy or sell
		size 		- VOLUME of asset to purchase
		"""
		self.logger.info(f"Sport order - asset: {symbol}, side: {order_side}, type: {order_type}, price: {price}, size: {size}")
		if order_type == "limit":
			return self.spot_client.take_order(	instrument_id = symbol, 
												side 		= order_side, 
												type 		= order_type,
												price 		= price,
												size 		= size, 
												order_type 	= 0
											)
		elif order_type == "market":
			return self.spot_client.take_order(	instrument_id = symbol, 
												side 		= order_side, 
												type 		= order_type,
												price 		= 1,
												size 		= size if order_side == "sell" else 0, 
												notational 	= price * size if order_side == "buy" else 1,
												order_type 	= 0
											)

	def place_perpetual_order(self, symbol: str, 
									order_type: str, 
									order_side: str, 
									price: int,
									size: int,
									*args, **kwargs):
		"""
		order_type 	- Either limit or market
		order_side 	- Either buy or sell
		size 		- LOTS of asset to purchase

		Ref: https://www.okx.com/docs/en/#swap-swap---orders
		"""
		self.logger.info(f"Futures order - asset: {symbol}, side: {order_side}, type: {order_type}, price: {price}, size: {size}")
		return self.perp_client.take_order(	instrument_id = symbol,
											size 		= size,
											type 		= '1' if order_side == "buy" else '2',
											match_price = '1' if order_type == "market" else '0',
											price 		= price,
											order_type 	= 0
										)

	def cancel_spot_order(self, symbol: str, order_id: str):
		self.logger.info(f"Cancelling spot order ID {order_id}")

		try:
			self.spot_client.revoke_order(instrument_id = symbol, order_id = order_id)
		except Exception as ex:
			self.logger.error(ex)
		return

	def cancel_perpetual_order(self, symbol: str, order_id: str):
		self.logger.info(f"Cancelling futures order ID {order_id}")

		try:
			self.perp_client.revoke_order(instrument_id = symbol, order_id = order_id)
		except Exception as ex:
			self.logger.error(ex)
		return