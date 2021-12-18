import logging
from clients.DataAccessClients import DataAccessClients
from clients.DataAccessClients import AssetInfoTable
from sqlalchemy import create_engine

class SqlClient(DataAccessClients):
	logger 			= logging.getLogger('SqlClient')
	db 				= None
	spot_symbol 	= None
	futures_symbol 	= None

	def __init__(self, 	url: str,
						spot_symbol: str,
						futures_symbol: str
				):
		self.db 			= create_engine(url, echo = True)
		self.spot_symbol 	= spot_symbol
		self.futures_symbol = futures_symbol
		return

	def get_spot_volume(self):
		pass

	def get_futures_lot_size(self):
		pass

	def set_spot_volume(self, volume: float):
		pass

	def set_futures_lot_size(self, lot_size: int):
		pass