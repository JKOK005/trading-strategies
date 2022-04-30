import enum
import logging
import json
from db.DbClient import DbClient, BASE, func
from sqlalchemy import *

class TradeLogs(BASE):
	# Follow the order spot / futures / perpetual in defining first & second assets
	# For example, a spot asset will be first and a futures asset will be second
	 
	__tablename__ 	= "trade_logs"
	__table_args__ 	= (	
						UniqueConstraint('exchange', 'trade_id', name = 'tradeid_exchange_constraint'),
						{'extend_existing': True},
					)

	ID 				= Column(Integer, primary_key = True)
	page_id 		= Column(String, nullable = False) 		# Used to retrieved records beyond this number
	exchange 		= Column(String, nullable = False)
	order_id  		= Column(String, nullable = False)
	trade_id 		= Column(String, nullable = False)		# Note: Many trades can belong to the same order
	client_id 		= Column(String, nullable = False)
	symbol 			= Column(String, nullable = False)
	fill_price 		= Column(Float, nullable = False)
	fill_size 		= Column(Float, nullable = False)
	order_side 		= Column(String, nullable = False)
	pos_side 		= Column(String, nullable = True) 		# Only applicable for futures / perpetual
	order_ts 		= Column(String, nullable = False)
	created_at 		= Column(String, nullable = False, default = func.current_timestamp())

	def __repr__(self):
		return f"{self.ID}-{self.exchange}-{self.client_id}-{self.order_id}"

class TradeLogsClient(DbClient):
	def table_ref(self):
		return TradeLogs

	@DbClient._with_session_context
	def insert(self, conn, params):
		return self.insert_table(conn = conn, params = params)