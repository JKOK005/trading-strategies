import enum
import logging
import json
from db.DbClient import DbClient, BASE
from sqlalchemy import *

class TradeLogs(BASE):
	# Follow the order spot / futures / perpetual in defining first & second assets
	# For example, a spot asset will be first and a futures asset will be second
	 
	__tablename__ 	= "trade_logs"
	__table_args__ 	= (	
						Index('exchange', 'order_id'),
						UniqueConstraint('exchange', 'order_id', name = 'orderid_exchange_constraint'),
						{'extend_existing': True},
					)

	ID 				= Column(Integer, primary_key = True)
	exchange 		= Column(String, nullable = False)
	order_id  		= Column(String, nullable = False)
	client_id 		= Column(String, nullable = False)
	symbol 			= Column(String, nullable = False)
	order_type 		= Column(String, nullable = False)
	order_side 		= Column(String, nullable = False)
	pos_side 		= Column(String, nullable = True) 	# Only applicable for futures / perpetual
	order_size 		= Column(Float, nullable = False)
	order_ts 		= Column(Integer, nullable = False)
	created_at 		= Column(Integer, nullable = False)

	def __repr__(self):
		return f"{self.ID}-{self.exchange}-{self.client_id}-{self.order_id}"

class TradeLogsClient(DbClient):
	def table_ref(self):
		return TradeLogs