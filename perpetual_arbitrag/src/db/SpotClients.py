import logging
from AssetInfoTable import *
from sqlalchemy import *
from sqlalchemy.orm import declarative_base

BASE = declarative_base()

class SpotInfoTable(AssetInfoTable, BASE):
	__tablename__ 		= "spot_info"

class SpotClients(AssetClient):
	logger 		= logging.getLogger('SpotClients')
	
	def __init__(self, **kwargs):
		super(SpotClients, self).__init__(**kwargs)
		return