import enum
import logging
import json
from db.DbClient import DbClient, BASE
from functools import cmp_to_key
from sqlalchemy import *

class JobRanking(BASE):
	# Follow the order spot / futures / perpetual in defining first & second assets
	# For example, a spot asset will be first and a futures asset will be second
	 
	__tablename__ 	= "job_ranking"
	__table_args__ 	= {'extend_existing': True} 

	def __lt__(self, other):
         return self.ranking < other.ranking

	ID 				= Column(Integer, primary_key = True)
	exchange 		= Column(String, nullable = False)
	asset_type 		= Column(String, nullable = False)
	first_asset 	= Column(String, nullable = False)
	second_asset 	= Column(String, nullable = False)
	ranking 		= Column(Integer, nullable = False)

	def __repr__(self):
		return f"{self.ID}-{self.exchange}-{self.asset_type}-{self.first_asset}-{self.second_asset}"

class JobRankingClient(DbClient):
	def table_ref(self):
		return JobRanking

	@DbClient._with_session_context
	def fetch_ranked(self, conn, exchange: str, asset_type: str, top_N: int):
		rows = self.get_entries(conn = conn, exchange = exchange, asset_type = asset_type)
		conn.expunge_all()
		return rows.sort()[ : top_N]

	@DbClient._with_session_context
	def insert_row(self, conn, param):
		return self.insert_table(conn 	= conn, 
								 params = {
									"exchange" 		: param["exchange"], 
									"asset_type" 	: param["asset_type"],
									"first_asset" 	: param["first_asset"],
									"second_asset" 	: param["second_asset"],
									"ranking" 		: param["ranking"]
									}
							 	)

	@DbClient._with_session_context
	def insert_rows(self, conn, params):
		# params expected to be a list of dictionary containing params in JobRanking table
		return self.insert_table(conn = conn, params = params)