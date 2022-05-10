import enum
import logging
import json
from db.DbClient import DbClient, BASE
from sqlalchemy import *

class AssetNames(object):
	__tablename__ 	= "asset_names"
	__table_args__	= (	
						UniqueConstraint("exchange", "symbol", name = "exchange_symbol_constraint"),
						{'extend_existing': True}
					)

	ID 			= Column(Integer, primary_key = True)
	exchange 	= Column(String, nullable = False)
	asset_type 	= Column(String, nullable = False)
	symbol 		= Column(String, nullable = False)
	base 		= Column(String, nullable = False)

	def __repr__(self):
		return f"{self.exchange}-{self.asset_type}-{self.symbol}"

class AssetNamesClient(DbClient):
	def table_ref(self):
		return AssetNames

	@DbClient._with_session_context
	def delete(self, conn, **filters):
		return self.delete_table(conn = conn, **filters)

	@DbClient._with_session_context
	def insert(self, conn, params):
		return self.insert_table(conn = conn, params = params, on_conflict_ignore = False, on_conflict_rule = '')