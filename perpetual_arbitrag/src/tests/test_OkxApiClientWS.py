import copy
import sys
import pytest
from clients.OkxApiClientWS import OkxApiClientWS
from unittest import TestCase
from unittest.mock import patch

class TestOkxApiClientWS(TestCase):

	def setUp(self):
		self.okx_api_client = OkxApiClientWS(api_key 			= "123", 
											 api_secret_key 	= "123", 
											 passphrase 		= "fake_spot_passphrase",
											 feed_client 		= None,
											 funding_rate_enable = True,
											)

	def test_get_spot_average_bid_ask_price(self):
		pass

	def test_get_perpetual_average_bid_ask_price(self):
		pass

	def test_assert_spot_resp_error(self):
		pass

	def test_assert_perpetual_resp_error(self):
		pass

	def test_place_spot_order(self):
		pass

	def test_place_perpetual_order(self):
		pass