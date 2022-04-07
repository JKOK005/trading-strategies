import enum
import logging
from db.DbClient import DbClient, BASE
from sqlalchemy import *

class Users(BASE):
	__tablename__ 	= "users"
	__table_args__ 	= (
						UniqueConstraint('name', name = 'username_constraint'),
						{'extend_existing': True},
					)

	ID 				= Column(Integer, primary_key = True)
	name 			= Column(String, nullable = False)
	password 		= Column(String, nullable = False)

	def __repr__(self):
		return f"{self.ID}-{self.name}"

class UsersClient(DbClient):
	def table_ref(self):
		return Users