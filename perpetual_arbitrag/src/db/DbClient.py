import enum
import logging
from abc import ABCMeta
from abc import abstractmethod
from sqlalchemy import *
from sqlalchemy.orm import declarative_base, sessionmaker

BASE = declarative_base()

class DbClient(metaclass = ABCMeta):
	@abstractmethod
	def table_ref(self):
		pass

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