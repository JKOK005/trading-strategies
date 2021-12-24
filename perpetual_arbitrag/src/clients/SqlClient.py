import logging
from clients.DataAccessClients import DataAccessClients
from clients.DataAccessClients import AssetInfoTable
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class SqlClient(DataAccessClients):
	logger 			= logging.getLogger('SqlClient')
	session 		= None
	spot_symbol 	= None
	futures_symbol 	= None

	def __init__(self, 	url: str,
						spot_symbol: str,
						futures_symbol: str
				):
		engine 				= create_engine(url, echo = False)
		SESSION 			= sessionmaker()
		SESSION.configure(bind = engine)
		self.session 		= SESSION()
		self.spot_symbol 	= spot_symbol
		self.futures_symbol = futures_symbol
		return

	def get_entry(self):
		return self.session.query(AssetInfoTable).filter_by(spot_symbol = self.spot_symbol, futures_symbol = self.futures_symbol).first()

	def modify_entry(self, entry, attribute, new_value):
		setattr(entry, attribute, new_value)
		self.logger.info(f"Modify {attribute} of {entry} -> {new_value}")
		return

	def get_spot_volume(self):
		entry = self.get_entry()
		return entry.spot_volume

	def get_futures_lot_size(self):
		entry = self.get_entry()
		return entry.futures_lot_size

	def get_position(self):
		# Returns the (spot_vol, futures_lot_size) assets pair in a single query to the session
		entry = self.get_entry()
		return (entry.spot_volume, entry.futures_lot_size)

	def set_spot_volume(self, volume: float):
		entry = self.get_entry()
		self.modify_entry(entry = entry, attribute = "spot_volume", new_value = volume)
		self.session.commit()
		return

	def set_futures_lot_size(self, lot_size: int):
		entry = self.get_entry()
		self.modify_entry(entry = entry, attribute = "futures_lot_size", new_value = lot_size)
		self.session.commit()
		return

	def set_position(self, spot_volume: float, futures_lot_size: int):
		entry = self.get_entry()
		self.modify_entry(entry = entry, attribute = "spot_volume", new_value = spot_volume)
		self.modify_entry(entry = entry, attribute = "futures_lot_size", new_value = futures_lot_size)
		self.session.commit()
		return

	def create_entry(self):
		self.logger.info(f"New entry for {self.spot_symbol} / {self.futures_symbol} pair")
		new_entry = AssetInfoTable(spot_symbol = self.spot_symbol, futures_symbol = self.futures_symbol, spot_volume = 0, futures_lot_size = 0)
		self.session.add(new_entry)
		self.session.commit()
		return

	def is_exists(self):
		entry = self.get_entry()
		return entry is not None