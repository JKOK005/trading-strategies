import enum
import logging
from db.DbClient import DbClient, BASE
from sqlalchemy import *

class SecretKeys(BASE):
	__tablename__ 	= "secret_keys"
	__table_args__ 	= {'extend_existing': True} 

	ID 				= Column(Integer, primary_key = True)
	user_id 		= Column(Integer, ForeignKey('users.ID'))
	exchange 		= Column(String,  nullable = False)
	client_id 		= Column(String,  nullable = False)
	api_keys 		= Column(String,  nullable = False)

	def __repr__(self):
		return f"{self.ID}-{self.user_id}"

class SecretsClient(DbClient):
	def table_ref(self):
		return SecretKeys