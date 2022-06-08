import logging
from db.AssetClient import *
from sqlalchemy import *
from sqlalchemy.orm import declarative_base

BASE = declarative_base()

class MarginInfoTable(AssetInfoTable, BASE):
	__tablename__ 	= "margin_info"
	__table_args__ 	= {'extend_existing': True} 

class MarginClients(AssetClient):
	logger 		= logging.getLogger('MarginClients')
	
	def table_ref(self):
		return MarginInfoTable

	def new_table(self):
		return MarginInfoTable(strategy_id = self.strategy_id, client_id = self.client_id, exchange = self.exchange,
							 symbol = self.symbol, size = 0, units = self.units)

	def __init__(self, **kwargs):
		super(MarginClients, self).__init__(**kwargs)
		return