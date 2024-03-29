import enum
import logging
import json
from db.DbClient import DbClient, BASE
from sqlalchemy import *

class SecretKeys(BASE):
	__tablename__ 	= "secret_keys"
	__table_args__ 	= (
						UniqueConstraint('user_id', 'exchange', name = 'userid_exchange_constraint'),
						{'extend_existing': True} 
					)

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

	@DbClient._with_session_context
	def get_secrets(self, conn, user_id, exchange):
		secret_info 	= self.get_entry(conn = conn,
										 user_id = user_id,
										 exchange = exchange,
										)

		return json.loads(secret_info.api_keys)

	@DbClient._with_session_context
	def get_client_id(self, conn, user_id, exchange):
		secret_info 	= self.get_entry(conn = conn,
										 user_id = user_id,
										 exchange = exchange,
										)

		return secret_info.client_id

	@DbClient._with_session_context
	def get_all_secrets(self, conn, exchange):
		all_secrets = self.get_entries(conn = conn, exchange = exchange)
		conn.expunge_all()
		return all_secrets