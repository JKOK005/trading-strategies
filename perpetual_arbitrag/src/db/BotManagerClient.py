import enum
import logging
from sqlalchemy import *
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

BASE = declarative_base()

class Users(BASE):
	__tablename__ 	= "users"
	ID 				= Column(Integer, primary_key = True)
	name 			= Column(String, nullable = False)

	def __repr__(self):
		return f"{self.name}-{self.ID}"

class SecretKeys(BASE):
	__tablename__ 	= "secret_keys"
	ID 				= Column(Integer, primary_key = True)
	user_id 		= Column(Integer, ForeignKey('users.ID'))
	exchange 		= Column(String,  nullable = False)
	client_id 		= Column(String,  nullable = False)
	api_keys 		= Column(String,  nullable = False)

	def __repr__(self):
		return f"{self.user_id}-{self.exchange}-{self.ID}"		

class ArbitragDockerImages(BASE):
	__tablename__ 	= "arbitrag_docker_images"
	ID 				= Column(Integer, primary_key = True)
	exchange		= Column(String,  nullable = False)
	asset_pair 		= Column(String,  nullable = False)
	docker_img 		= Column(String,  nullable = False)

	def __repr__(self):
		return f"{self.exchange}-{self.asset_pair}-{self.ID}"

class AssetPairsJobs(BASE):
	# For spot / futures / perpetual arbitrag, we follow the order of spot / futures / perpetual as pair_A.
	__tablename__ 	= "asset_pairs_job"
	ID 				= Column(Integer, primary_key = True)
	user_id 		= Column(Integer, ForeignKey('users.ID'))
	secret_id 		= Column(Integer, ForeignKey('secret_keys.ID'))
	arb_img_id 		= Column(Integer, ForeignKey('arbitrag_docker_images.ID'))
	default_args 	= Column(String,  nullable = False)
	entry_args 		= Column(String,  nullable = False)
	exit_args 		= Column(String,  nullable = False)
	is_active 		= Column(Boolean, nullable = False)
	to_close 		= Column(Boolean, nullable = False)

	def __repr__(self):
		return f"{self.user_id}-{self.secret_id}-{self.ID}"

class BotManagerClient():
	db_url 		= None
	user_id 	= None
	session 	= None

	def __init__(self, 	url: str, user_id: int,
				):
		self.db_url 	= url
		self.user_id 	= user_id
		return

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

	def get_entry(self, conn, table_ref, **filters):
		return conn.query(table_ref).filter_by(**filters).first()

	def get_entries(self, conn, table_ref, **filters):
		return conn.query(table_ref).filter_by(**filters).all()

	@_with_session_context
	def get_jobs(self, conn, is_active: bool, to_close: bool):
		res = self.get_entries( conn = conn,
								table_ref = AssetPairsJobs,
								user_id = self.user_id,
								is_active = is_active,
								to_close = to_close
							)
		conn.expunge_all()
		return res

	@_with_session_context
	def get_secret_keys(self, conn, secret_id: int):
		res = self.get_entry( 	conn = conn,
								table_ref = SecretKeys,
								ID = secret_id,
							)
		return res.api_keys

	@_with_session_context
	def get_image(self, conn, image_id: int):
		res = self.get_entry( 	conn = conn,
								table_ref = ArbitragDockerImages,
								ID = image_id,
							)
		return res.docker_img
