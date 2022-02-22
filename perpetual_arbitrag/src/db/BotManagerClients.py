import enum
import logging
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

class BotManagerTable(object):
	# For spot / futures / perpetual arbitrag, we follow the order of spot / futures / perpetual as pair_A.

	ID 				= Column(Integer, primary_key = True)
	exchange 		= Column(String,  nullable = False)
	asset_pair 		= Column(String,  nullable = False)
	docker_img 		= Column(String,  nullable = False)
	default_args 	= Column(String,  nullable = False)
	entry_args 		= Column(String,  nullable = False)
	exit_args 		= Column(String,  nullable = False)
	is_active 		= Column(Boolean, nullable = False)
	to_close 		= Column(Boolean, nullable = False)

	def __repr__(self):
		return f"{self.exchange}-{self.asset_pair}-active_{self.is_active}-close_{self.to_close}"

class BotManagerClients():
	db_url 		= None
	session 	= None
	symbol 		= None

	def __init__(self, 	url: str,
						exchange: str,
						asset_pair: str
				):
		self.db_url 	= url
		self.exchange 	= exchange
		self.asset_pair = asset_pair
		return

	def modify_entry(self, entry, attribute, new_value):
		# TODO: Fix logging issue within context manager session
		setattr(entry, attribute, new_value)
		# self.logger.info(f"Modify {attribute} of {entry} -> {new_value}")
		return

	def _with_session_context(func):
		def wrapper(self, *args, **kwargs):
			with self.session() as conn, conn.begin():
				res = func(self, conn = conn, *args, **kwargs)
				return res
		return wrapper

	def table_ref(self):
		return BotManagerTable

	def create_session(self):
		# Do not invoke this part for testing
		engine 			= create_engine(self.db_url, echo = False)
		self.session 	= sessionmaker(engine)
		return self

	def get_entry(self, conn, **filters):
		return conn.query(self.table_ref()).filter_by(**filters).first()

	def get_entries(self, conn, **filters):
		return conn.query(self.table_ref()).filter_by(**filters).all()

	@_with_session_context
	def get_trades(self, conn, is_active: bool, to_close: bool):
		return self.get_entries(conn = conn, 
								exchange = self.exchange, 
								asset_pair = self.asset_pair,
								is_active = is_active,
								to_close = to_close
							)

	@_with_session_context
	def set_status(self, conn, id: int, is_active: bool):
		entry = self.get_entry(conn = conn, ID = id)
		self.modify_entry(entry = entry, attribute = "is_active", new_value = is_active)
		return