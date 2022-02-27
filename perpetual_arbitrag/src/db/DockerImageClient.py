import enum
import logging
from db.DbClient import DbClient, BASE
from sqlalchemy import *

class ArbitragDockerImages(BASE):
	__tablename__ 	= "arbitrag_docker_images"
	__table_args__ 	= {'extend_existing': True} 

	ID 				= Column(Integer, primary_key = True)
	exchange		= Column(String,  nullable = False)
	asset_pair 		= Column(String,  nullable = False)
	docker_img 		= Column(String,  nullable = False)

	def __repr__(self):
		return f"{self.ID}-{self.docker_img}"

class DockerImageClient(DbClient):
	def table_ref(self):
		return ArbitragDockerImages

	@DbClient._with_session_context
	def get_img_name(self, conn, exchange, asset_pair):
		image_info 	= self.get_entry(conn = conn,
									 exchange = exchange,
									 asset_pair = asset_pair,
									)

		return image_info.docker_img