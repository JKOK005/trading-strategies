import logging
from AssetInfoTable import *
from sqlalchemy import *
from sqlalchemy.orm import declarative_base

BASE = declarative_base()

class PerpetualInfoTable(AssetInfoTable, BASE):
	__tablename__ 		= "perpetual_info"

class PerpetualClients(AssetClient):
	logger 		= logging.getLogger('PerpetualClients')
	
	def __init__(self, **kwargs):
		super(PerpetualClients, self).__init__(**kwargs)
		return