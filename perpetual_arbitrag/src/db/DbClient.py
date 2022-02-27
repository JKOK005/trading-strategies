import enum
import logging
from abc import ABCMeta
from abc import abstractmethod
from sqlalchemy import *
from sqlalchemy.orm import declarative_base, sessionmaker

BASE = declarative_base()

class DbClient(metaclass = ABCMeta):
	db_url 	= None
	session = None

	def __init__(self, db_url: str):
		self.db_url 	= db_url
		return

	@abstractmethod
	def table_ref(self):
		pass

	def create_session(self):
		# Do not invoke this part for testing
		engine 			= create_engine(self.db_url, echo = False)
		self.session 	= sessionmaker(engine)
		return self

	def modify_entry(self, entry, attribute, new_value):
		setattr(entry, attribute, new_value)
		return

	def _with_session_context(func):
		def wrapper(self, *args, **kwargs):
			with self.session() as conn, conn.begin():
				res = func(self, conn = conn, *args, **kwargs)
				return res
		return wrapper

	def create_session(self):
		# Do not invoke this part for testing
		engine 			= create_engine(self.db_url, echo = False)
		self.session 	= sessionmaker(engine)
		return self

	def get_entry(self, conn, **filters):
		return conn.query(self.table_ref()).filter_by(**filters).first()

	def get_entries(self, conn, **filters):
		return conn.query(self.table_ref()).filter_by(**filters).all()

	def insert_table(self, conn, params):
		# params can either be a dictionary or a list of dictionaries
	 	res = conn.execute(insert(self.table_ref()).values(params))
	 	return res