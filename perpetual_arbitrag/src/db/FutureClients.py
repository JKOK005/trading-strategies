import logging
from AssetInfoTable import *
from sqlalchemy import *
from sqlalchemy.orm import declarative_base

BASE = declarative_base()

class FutureInfoTable(AssetInfoTable, BASE):
	__tablename__ 		= "future_info"

class FutureClients(AssetClient):
	logger 		= logging.getLogger('FutureClients')
	
	def __init__(self, **kwargs):
		super(FutureClients, self).__init__(**kwargs)
		return