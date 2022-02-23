import copy
from db.BotManagerClient import *
from unittest import TestCase
from unittest.mock import patch, MagicMock

class BotManagerClientMock(BotManagerClient):
	def __init__(self, **kwargs):
		super(BotManagerClientMock, self).__init__(**kwargs)
		return

class TestBotManagerClient(TestCase):

	def setUp(self):
		asset_info 				= AssetPairsJobs()
		asset_info.user_id 		= 1
		asset_info.secret_id 	= 2
		asset_info.arb_img_id 	= 3
		asset_info.default_args = {"args" : "val"}
		asset_info.entry_args 	= {"args" : "entry"}
		asset_info.exit_args 	= {"args" : "exit"}
		asset_info.is_active 	= True
		asset_info.to_close 	= False

		secrets_info			= SecretKeys()
		secrets_info.user_id 	= 1
		secrets_info.exchange 	= "okx"
		secrets_info.client_id 	= 4
		secrets_info.api_keys 	= {"key" : "val"}

		arb_img_info 			= ArbitragDockerImages()
		arb_img_info.exchange 	= "okx"
		arb_img_info.asset_pair = "spot-perp"
		arb_img_info.docker_img = "docker-img"

		self.client 			= BotManagerClientMock(	url = "blank", user_id = 1)
		self.client.session 	= MagicMock()
		
		self.return_asset 		= asset_info
		self.return_secrets 	= secrets_info
		self.return_img 		= arb_img_info

	def test_retrieve_jobs(self):
		with patch.object(BotManagerClientMock, "get_entries") as mock_get_entries:
			mock_get_entries.return_value = [self.return_asset]
			fetched_jobs = self.client.get_jobs(is_active = True, to_close = False)
		assert(type(fetched_jobs) == list)

	def test_retrieve_secret_keys(self):
		with patch.object(BotManagerClientMock, "get_entry") as mock_get_entry:
			mock_get_entry.return_value = self.return_secrets
			fetched_secret = self.client.get_secret_keys(secret_id = 1)
		assert(fetched_secret == self.return_secrets.api_keys)

	def test_retrieve_image(self):
		with patch.object(BotManagerClientMock, "get_entry") as mock_get_entry:
			mock_get_entry.return_value = self.return_img
			fetched_img = self.client.get_image(image_id = 1)
		assert(fetched_img == self.return_img.docker_img)