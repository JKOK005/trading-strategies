import copy
import redis
from feeds.CryptoStoreRedisFeeds import CryptoStoreRedisFeeds, assert_latency
from freezegun import freeze_time
from unittest import TestCase
from unittest.mock import patch

class TestCryptoStoreRedisFeeds(TestCase):
	def setUp(self):
		self.redis_url = None
		self.redis_port = None
		self.permissible_latency_s = 5
		self.cli = CryptoStoreRedisFeeds(redis_url = self.redis_url, redis_port = self.redis_port, permissible_latency_s = self.permissible_latency_s)
		return

	@patch("redis.Redis")
	def test_sorted_order_book_is_sorted_correctly(self, mock_redis):
		mock_redis.zrange.return_value = ['{"exchange":"OKX","symbol":"DOT-USDT-PERP","book":{"bid":{"18.081":1,"18.08":95,"18.077":58,"18.076":103},"ask":{"18.082":36,"18.083":49,"18.084":6,"18.085":7}},"timestamp":1647401540.262,"receipt_timestamp":1647401540.288211}']
		self.cli.redis_cli = mock_redis

		with patch.object(self.cli, "symbol_to_key_mapping") as mock_symbol_to_key_mapping:
			mock_symbol_to_key_mapping.return_value = "DOT-USDT-PERP"
			order_book = self.cli.sorted_order_book.__wrapped__(self.cli, symbol = "DOT-USDT-SWAP", exchange = "OKX")
			assert(	
					order_book["bids"] == sorted(order_book["bids"], key = lambda x: x[0], reverse = True) and
					order_book["asks"] == sorted(order_book["asks"], key = lambda x: x[0], reverse = False)
				)

	@freeze_time("2022-03-01 01:00:04")
	def test_latency_within_tolerence(self):
		@assert_latency
		def _mock_fnct(self):
			# For date 01/03/2022 01:00:00
			return {"updated" : 1646096400}

		_mock_fnct(self)
		return

	@freeze_time("2022-03-01 01:00:06")
	def test_latency_beyond_tolerence(self):
		@assert_latency
		def _mock_fnct(self):
			# For date 01/03/2022 01:00:00
			return {"updated" : 1646096400}

		with self.assertRaises(Exception):
 			_mock_fnct(self)
		return

	def test_symbol_to_key_mapping_okx(self):
		input_symbol 	= "DOT-USDT-SWAP"
		input_exchange 	= "OKX"
		expected_symbol = "DOT-USDT-PERP"
		assert(self.cli.symbol_to_key_mapping(symbol = input_symbol, exchange = input_exchange) == expected_symbol)