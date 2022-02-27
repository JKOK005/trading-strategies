import enum
import logging
from abc import ABCMeta
from abc import abstractmethod
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

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

# TODO: Shift implementation to DbClient in future

class AssetClient(metaclass = ABCMeta):
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

	def _with_session_context(func):
		def wrapper(self, *args, **kwargs):
			with self.session() as conn, conn.begin():
				res = func(self, conn = conn, *args, **kwargs)
				return res
		return wrapper

	@abstractmethod
	def table_ref(self):
		pass

	@abstractmethod
	def new_table(self):
		pass

	def create_session(self):
		# Do not invoke this part for testing
		engine 			= create_engine(self.db_url, echo = False)
		self.session 	= sessionmaker(engine)
		return self

	def modify_entry(self, entry, attribute, new_value):
		# TODO: Fix logging issue within context manager session
		setattr(entry, attribute, new_value)
		# self.logger.info(f"Modify {attribute} of {entry} -> {new_value}")
		return

	def get_entry(self, conn):
		return conn.query(self.table_ref()).filter_by(	strategy_id = self.strategy_id,
														client_id 	= self.client_id,
														exchange	= self.exchange,
														symbol 		= self.symbol).first()

	@_with_session_context
	def create_entry(self, conn):
		new_entry = self.new_table()
		conn.add(new_entry)
		return

	@_with_session_context
	def get_position(self, conn):
		entry = self.get_entry(conn = conn)
		return entry.size

	@_with_session_context
	def set_position(self, conn, size: float):
		entry = self.get_entry(conn = conn)
		self.modify_entry(entry = entry, attribute = "size", new_value = size)
		return

	@_with_session_context
	def is_exists(self, conn):
		entry = self.get_entry(conn = conn)
		return entry is not None