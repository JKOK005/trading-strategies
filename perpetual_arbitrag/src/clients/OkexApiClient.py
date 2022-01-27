import datetime
import logging
import sys
from okex.swap_api import SwapAPI
from okex.spot_api import SpotAPI
from clients.ExchangeSpotClients import ExchangeSpotClients
from clients.ExchangePerpetualClients import ExchangePerpetualClients

class OkexApiClient(ExchangeSpotClients, ExchangePerpetualClients):
	def __init__(self, 	api_key: str, 
						api_secret_key: str,
						passphrase: str):
		
		spot_client 	= SpotAPI(	api_key = api_key, 
									api_secret_key = api_secret_key, 
									passphrase = passphrase)

		perp_client 	= SwapAPI(	api_key = api_key, 
									api_secret_key = api_secret_key, 
									passphrase = passphrase)

		logger 			= logging.getLogger('OkexApiClient')
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
		pass

	def get_perpetual_open_orders(self, symbol: str):
		"""
		Gets information of all open future orders by the user
		"""
		pass

	def get_spot_most_recent_open_order(self, symbol: str):
		"""
		Gets the most recent open orders for spot
		"""
		pass

	def get_perpetual_most_recent_open_order(self, symbol: str):
		"""
		Gets the most recent open orders for perpetual
		"""
		pass

	def get_spot_fulfilled_orders(self, symbol: str):
		"""
		Gets information for all fulfilled spot orders by the user
		"""
		pass

	def get_perpetual_fulfilled_orders(self, symbol: str):
		"""
		Gets information of all fulfilled future orders by the user
		"""
		pass

	def get_spot_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent spot trade that have been fulfilled
		"""
		pass

	def get_perpetual_most_recent_fulfilled_order(self, symbol: str):
		"""
		Gets information of the most recent perpetual trade that have been fulfilled
		"""
		pass

	def get_perpetual_effective_funding_rate(self, symbol: str, seconds_before: int):
		"""
		Gets the effective funding rate for perpetual contract.

		Effective funding rate takes into account a variety of factors to decide on the funding rate.
		"""
		pass
 
	def place_spot_order(self, *args, **kwargs):
		pass

	def place_perpetual_order(self, *args, **kwargs):
		pass

	def cancel_spot_order(self, order_id: str):
		pass

	def cancel_perpetual_order(self, order_id: str):
		pass