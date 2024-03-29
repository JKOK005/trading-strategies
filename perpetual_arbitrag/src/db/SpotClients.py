import logging
from db.AssetClient import *
from sqlalchemy import *
from sqlalchemy.orm import declarative_base

BASE = declarative_base()

class SpotInfoTable(AssetInfoTable, BASE):
	__tablename__ 	= "spot_info"
	__table_args__ 	= {'extend_existing': True} 

class SpotClients(AssetClient):
	logger 		= logging.getLogger('SpotClients')
	
	def table_ref(self):
		return SpotInfoTable

	def new_table(self):
		return SpotInfoTable(strategy_id = self.strategy_id, client_id = self.client_id, exchange = self.exchange,
							 symbol = self.symbol, size = 0, units = self.units)

	def __init__(self, **kwargs):
		super(SpotClients, self).__init__(**kwargs)
		return