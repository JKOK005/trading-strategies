import copy
import sys
import sqlalchemy
from db.BotManagerClient import *
from sqlalchemy.orm import Session, declarative_base
from unittest import TestCase
from unittest.mock import patch, MagicMock

BASE = declarative_base()

class AssetPairJobsMock(AssetPairsJobs, BASE):
	__tablename__ 	= "asset_pair_jobs_mock"

class BotManagerClientMock(BotManagerClient):
	def table_ref(self):
		return AssetPairJobsMock

	def __init__(self, **kwargs):
		super(BotManagerClientMock, self).__init__(**kwargs)
		return

class TestBotManagerClient(TestCase):

	def setUp(self):
		asset_info 				= AssetPairJobsMock()
		asset_info.exchange 	= "exchange"
		asset_info.asset_pair 	= "spot-perp"
		asset_info.client_id 	= 123
		asset_info.docker_img 	= "docker"
		asset_info.default_args = {"args" : "val"}
		asset_info.entry_args 	= {"args" : "entry"}
		asset_info.exit_args 	= {"args" : "exit"}
		asset_info.is_active 	= True
		asset_info.to_close 	= False

		self.client 			= BotManagerClientMock(	url = "blank", exchange = "exchange", asset_pair = "spot-perp", client_id = 123)
		self.client.session 	= MagicMock()
		self.return_asset 		= asset_info

	def test_retrieve_jobs(self):
		pass

	def test_deactivate_job(self):
		pass