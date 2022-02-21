import enum
import logging
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

class BotManagerTable(object):
	# For spot / futures / perpetual arbitrag, we follow the order of spot / futures / perpetual as pair_A.

	ID 			= Column(Integer, primary_key = True)
	exchange 	= Column(String, nullable = False)
	asset_pair 	= Column(String, nullable = False)
	pair_A 		= Column(String, nullable = False)
	dca_size_A 	= Column(Float, nullable = False)
	max_dca_A 	= Column(Float, nullable = False)
	pair_B 		= Column(String, nullable = False)
	dca_size_B 	= Column(Float, nullable = False)
	max_dca_B 	= Column(Float, nullable = False)

	def __repr__(self):
		return f"{self.exchange}-{self.asset_pair}-{self.pair_A}-{self.pair_B}"

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

	def get_entries(self, conn, **filters):
		return conn.query(self.table_ref()).filter_by(**filters)

	def get_entry(self, conn, **filters):
		return self.get_entries(conn = conn, **filters).first()

	@_with_session_context
	def get_trade_pairs(self, conn):
		entries = self.get_entries(	conn = conn, 
									exchange = self.exchange, 
									asset_pair = self.asset_pair)

		return list(map(lamda row: (row.pair_A, row.pair_B), entries))

	@_with_session_context
	def get_trade_pair_sizes(self, conn, pair_A_symbol, pair_B_symbol):
		entry 	= self.get_entry(	conn = conn, 
									exchange = self.exchange, 
									asset_pair = self.asset_pair, 
									pair_A = pair_A_symbol, 
									pair_B = pair_B_symbol)

		return (entry.pair_A, entry.dca_size_A, entry.max_dca_A, entry.pair_B, entry.dca_size_B, entry.max_dca_B)