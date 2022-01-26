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
		"""
		pass

	def get_spot_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the spot asset, assuming that we intend to trade at a given volume. 
		"""
		pass

	def get_perpetual_average_bid_ask_price(self, symbol: str, size: float):
		"""
		Returns the average bid / ask price of the perpetual asset, assuming that we intend to trade at a given lot size. 
		"""
		pass

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