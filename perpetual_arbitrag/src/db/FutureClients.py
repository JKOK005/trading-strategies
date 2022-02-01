import logging
from db.AssetInfoTable import *
from sqlalchemy import *
from sqlalchemy.orm import declarative_base

BASE = declarative_base()

class FutureInfoTable(AssetInfoTable, BASE):
	__tablename__ 		= "future_info"

class FutureClients(AssetClient):
	logger 		= logging.getLogger('FutureClients')

	def table_ref(self):
		return FutureInfoTable

	def new_table(self):
		return FutureInfoTable(	strategy_id = self.strategy_id, client_id = self.client_id, exchange = self.exchange,
							 	symbol = self.symbol, size = 0, units = self.units)
	
	def __init__(self, **kwargs):
		super(FutureClients, self).__init__(**kwargs)
		return