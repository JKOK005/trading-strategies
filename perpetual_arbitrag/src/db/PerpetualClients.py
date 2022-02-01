import logging
from db.AssetInfoTable import *
from sqlalchemy import *
from sqlalchemy.orm import declarative_base

BASE = declarative_base()

class PerpetualInfoTable(AssetInfoTable, BASE):
	__tablename__ 		= "perpetual_info"

class PerpetualClients(AssetClient):
	logger 		= logging.getLogger('PerpetualClients')

	def table_ref(self):
		return PerpetualInfoTable

	def new_table(self):
		return PerpetualInfoTable(strategy_id = self.strategy_id, client_id = self.client_id, exchange = self.exchange,
							 	  symbol = self.symbol, size = 0, units = self.units)
	
	def __init__(self, **kwargs):
		super(PerpetualClients, self).__init__(**kwargs)
		return