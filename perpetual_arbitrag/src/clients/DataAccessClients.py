import deprecation
from abc import ABCMeta
from abc import abstractmethod
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Float, Integer, String
from sqlalchemy import UniqueConstraint

base = declarative_base()

class AssetInfoTable(base):
	__tablename__ 		= "asset_info"
	__table_args__		= (UniqueConstraint("spot_symbol", "futures_symbol"),)

	ID 					= Column(Integer, primary_key = True)
	spot_symbol 		= Column(String, nullable = False)
	futures_symbol 		= Column(String, nullable = False)
	spot_volume 		= Column(Float, nullable = False)
	futures_lot_size 	= Column(Integer, nullable = False)

	def __repr__(self):
		return f"{self.spot_symbol}-{self.futures_symbol}"

class DataAccessClients(metaclass = ABCMeta):
	@abstractmethod
	def get_spot_volume(self):
		pass

	@abstractmethod
	def get_futures_lot_size(self):
		pass

	@abstractmethod
	def set_spot_volume(self, volume: float):
		pass

	@abstractmethod
	def set_futures_lot_size(self, lot_size: int):
		pass