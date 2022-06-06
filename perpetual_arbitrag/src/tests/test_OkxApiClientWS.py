import copy
import sys
import pytest
from clients.OkxApiClientWS import OkxApiClientWS
from feeds.CryptoStoreRedisFeeds import CryptoStoreRedisFeeds
from unittest import TestCase
from unittest.mock import patch, MagicMock

class TestOkxApiClientWS(TestCase):

	def setUp(self):
		mock_feeds = MagicMock()
		mock_feeds.sorted_order_book.return_value = {"bids" : [(30, 10), (20, 10), (10, 10)], "asks" : [(40, 10), (50, 10), (60, 10)], "updated" : 1647489600}
		
		self.okx_api_client = OkxApiClientWS(api_key 			 = "123", 
											 api_secret_key 	 = "123", 
											 passphrase 		 = "fake_spot_passphrase",
											 feed_client 		 = mock_feeds,
											 funding_rate_enable = True,
											)
		return

	def test_get_spot_average_bid_ask_price(self):
		(avg_bids, avg_asks) = self.okx_api_client.get_spot_average_bid_ask_price(symbol = "None", size = 20)
		assert(avg_bids == 25 and avg_asks == 45)

	def test_get_perpetual_average_bid_ask_price(self):
		(avg_bids, avg_asks) = self.okx_api_client.get_spot_average_bid_ask_price(symbol = "None", size = 30)
		assert(avg_bids == 20 and avg_asks == 50)

	def test_get_margin_average_bid_ask_price(self):
		(avg_bids, avg_asks) = self.okx_api_client.get_margin_average_bid_ask_price(symbol = "None", size = 30)
		assert(avg_bids == 20 and avg_asks == 50)

	def test_assert_spot_resp_no_error(self):
		order_resp = {"code" : "0"}
		self.okx_api_client.assert_spot_resp_error(order_resp = order_resp)
		return

	def test_assert_spot_resp_error(self):
		order_resp = {"code" : "1"}
		with self.assertRaises(Exception):
			self.okx_api_client.assert_spot_resp_error(order_resp = order_resp)
		return

	def test_assert_perpetual_resp_no_error(self):
		order_resp = {"code" : "0"}
		self.okx_api_client.assert_perpetual_resp_error(order_resp = order_resp)
		return

	def test_assert_perpetual_resp_error(self):
		order_resp = {"code" : "1"}
		with self.assertRaises(Exception):
			self.okx_api_client.assert_perpetual_resp_error(order_resp = order_resp)
		return

	def test_assert_margin_resp_no_error(self):
		order_resp = {"code" : "0"}
		self.okx_api_client.assert_margin_resp_error(order_resp = order_resp)
		return

	def test_assert_margin_resp_error(self):
		order_resp = {"code" : "1"}
		with self.assertRaises(Exception):
			self.okx_api_client.assert_margin_resp_error(order_resp = order_resp)
		return