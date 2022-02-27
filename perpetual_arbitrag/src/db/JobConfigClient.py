import enum
import logging
import json
from db.DbClient import DbClient, BASE
from sqlalchemy import *

class JobConfig(BASE):
	# Follow the order spot / futures / perpetual in defining first & second assets
	# For example, a spot asset will be first and a futures asset will be second
	 
	__tablename__ 	= "job_config"
	__table_args__ 	= {'extend_existing': True} 

	ID 				= Column(Integer, primary_key = True)
	user_id 		= Column(Integer, ForeignKey('users.ID'))
	exchange 		= Column(String, nullable = False)
	asset_type 		= Column(String, nullable = False)
	first_asset 	= Column(String, nullable = False)
	second_asset 	= Column(String, nullable = False)
	default_args 	= Column(String, nullable = False)
	entry_args 		= Column(String, nullable = False)
	exit_args 		= Column(String, nullable = False)

	def __repr__(self):
		return f"{self.ID}-{self.exchange}-{self.asset_type}-{self.first_asset}-{self.second_asset}"

class JobConfigClient(DbClient):
	def table_ref(self):
		return JobConfig

	@DbClient._with_session_context
	def get_entry_config(self, conn, user_id, exchange, asset_type, first_asset, second_asset):
		config_info 	= self.get_entry(conn = conn,
										 user_id = user_id,
										 exchange = exchange,
										 asset_type = asset_type,
										 first_asset = first_asset,
										 second_asset = second_asset 
										)

		asset_json 		= json.loads(config_info.asset_args)
		default_json 	= json.loads(config_info.default_args)
		entry_json 		= json.loads(config_info.entry_args)
		return {**asset_json, **default_json, **entry_json}

	@DbClient._with_session_context
	def get_exit_config(self, conn, user_id, exchange, asset_type, first_asset, second_asset):
		config_info 	= self.get_entry(conn = conn,
										 user_id = user_id,
										 exchange = exchange,
										 asset_type = asset_type,
										 first_asset = first_asset,
										 second_asset = second_asset 
										)

		asset_json 		= json.loads(config_info.asset_args)
		default_json 	= json.loads(config_info.default_args)
		exit_json 		= json.loads(config_info.exit_args)
		return {**asset_json, **default_json, **exit_json}