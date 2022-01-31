import enum
import logging
from sqlalchemy import *

class AssetInfoTable(object):
	__table_args__	= (UniqueConstraint("strategy_id", "client_id", "exchange", "symbol"),)

	ID 			= Column(Integer, primary_key = True)
	strategy_id = Column(String, nullable = False)
	client_id 	= Column(String, nullable = False)
	exchange 	= Column(String, nullable = False)
	symbol 		= Column(String, nullable = False)
	size 		= Column(Float, nullable = False)
	units  		= Column(String, nullable = True)

	def __repr__(self):
		return f"{self.strategy_id}-{self.client_id}-{self.exchange}-{self.symbol}"

class AssetClient(object):
	db_url 		= None
	session 	= None
	symbol 		= None

	def __init__(self, 	url: str,
						strategy_id: str,
						client_id: str,
						exchange: str,
						symbol: str,
						units: str
				):
		self.db_url 		= url
		self.strategy_id 	= strategy_id
		self.client_id 		= client_id
		self.exchange 		= exchange
		self.symbol 		= symbol
		self.units 			= units
		return

	def start_session(self):
		engine 				= create_engine(self.db_url, echo = False)
		SESSION 			= sessionmaker()
		SESSION.configure(bind = engine)
		self.session 		= SESSION()
		return self

	def get_entry(self):
		return self.session.query(SpotInfoTable).filter_by(	strategy_id = self.strategy_id,
															client_id 	= self.client_id,
															exchange	= self.exchange,
															symbol 		= self.symbol).first()

	def modify_entry(self, entry, attribute, new_value):
		setattr(entry, attribute, new_value)
		self.logger.info(f"Modify {attribute} of {entry} -> {new_value}")
		return

	def get_position(self):
		entry = self.get_entry()
		return entry.size

	def set_position(self, size: float):
		entry = self.get_entry()
		self.modify_entry(entry = entry, attribute = "size", new_value = size)
		self.session.commit()
		return

	def create_entry(self):
		new_entry = SpotInfoTable(	strategy_id = self.strategy_id, client_id = self.client_id, exchange = self.exchange,
									symbol = self.symbol, size = 0, units = self.units)
		self.session.add(new_entry)
		self.session.commit()
		self.logger.info(f"Created new entry for {new_entry}")
		return

	def is_exists(self):
		entry = self.get_entry()
		return entry is not None