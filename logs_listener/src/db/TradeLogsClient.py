import enum
import logging
import json
from db.DbClient import DbClient, BASE
from sqlalchemy import *

class TradeLogs(BASE):
	# Follow the order spot / futures / perpetual in defining first & second assets
	# For example, a spot asset will be first and a futures asset will be second
	 
	__tablename__ 	= "job_config"
	__table_args__ 	= {'extend_existing': True} 

	ID 				= Column(Integer, primary_key = True)
	client_id 		= Column(String, nullable = False)
	exchange 		= Column(String, nullable = False)
	asset_type 		= Column(String, nullable = False)
	order_side 		= Column(String, nullable = False)
	order_size 		= Column(Float, nullable = False)
	order_type 		= Column(String, nullable = False)
	position_side 	= Column(String, nullable = True) 	# Only applicable for futures / perpetual
	symbol 			= Column(String, nullable = False)

	def __repr__(self):
		return f"{self.ID}-{self.exchange}-{self.asset_type}-{self.first_asset}-{self.second_asset}"

class JobConfigClient(DbClient):
	def table_ref(self):
		return JobConfig

	@DbClient._with_session_context
	def get_job_config(self, conn, user_id, exchange, asset_type, first_asset, second_asset):
		config_info 	= self.get_entry(conn = conn,
										 user_id = user_id,
										 exchange = exchange,
										 asset_type = asset_type,
										 first_asset = first_asset,
										 second_asset = second_asset 
										)

		default_json 	= json.loads(config_info.default_args)
		return default_json