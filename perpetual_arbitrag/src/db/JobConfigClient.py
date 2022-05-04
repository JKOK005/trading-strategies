import enum
import logging
import json
from db.DbClient import DbClient, BASE
from sqlalchemy import *

class JobConfig(BASE):
	# Follow the order spot / futures / perpetual in defining first & second assets
	# For example, a spot asset will be first and a futures asset will be second
	 
	__tablename__ 	= "job_config"
	__table_args__ 	= (
						UniqueConstraint('user_id', 'exchange', 'asset_type', 'first_asset' , 'second_asset', name = 'jobconfig_constraint'),
						{'extend_existing': True} 
					)

	ID 				= Column(Integer, primary_key = True)
	user_id 		= Column(Integer, ForeignKey('users.ID'))
	exchange 		= Column(String, nullable = False)
	asset_type 		= Column(String, nullable = False)
	first_asset 	= Column(String, nullable = False)
	second_asset 	= Column(String, nullable = False)
	default_args 	= Column(String, nullable = False)

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