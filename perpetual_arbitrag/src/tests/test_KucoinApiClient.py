import copy
from clients.KucoinApiClient import KucoinApiClient
from unittest import TestCase
from unittest.mock import patch

class TestKucoinApiClient(TestCase):
	def setUp(self):
		self.kucoin_api_client 	= KucoinApiClient(	spot_client_api_key 			= "123", 
													spot_client_api_secret_key 		= "123", 
													spot_client_pass_phrase 		= "fake_spot_passphrase",
													futures_client_api_key 			= "456", 
													futures_client_api_secret_key 	= "456", 
													futures_client_pass_phrase 		= "fake_futures_passphrase",
													sandbox = True
												)

	@patch("kucoin.client.User")
	def test_trading_account_details_filters_correct_symbol(self, patch_user):
		_kucoin_api_client 				= copy.deepcopy(self.kucoin_api_client)
		_kucoin_api_client.spot_user 	= patch_user
		patch_user.get_account_list.return_value 	= [ {"type" : "trade", "currency" : "BTC"},
														{"type" : "trade", "currency" : "USDT"},
														{"type" : "trade", "currency" : "XRP"},
														{"type" : "trade", "currency" : "ETH"},
														{"type" : "main", "currency" : "ETH"}]

		account_details 	= _kucoin_api_client.get_spot_trading_account_details(currency = "ETH")
		assert(account_details["type"] == "trade" and account_details["currency"] == "ETH")