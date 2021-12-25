import copy
import sys
import sqlalchemy
from clients.SqlClient import SqlClient
from clients.DataAccessClients import AssetInfoTable
from sqlalchemy.orm import Session
from unittest import TestCase
from unittest.mock import patch

class TestSqlClient(TestCase):

	def setUp(self):
		asset_info 					= AssetInfoTable()
		asset_info.spot_symbol 		= "TESTCOIN-USDT"
		asset_info.futures_symbol 	= "TESTCOINUSDTM"
		asset_info.spot_volume 		= 10
		asset_info.futures_lot_size = 10

		self.client 		= SqlClient(url = "test", spot_symbol = "TESTCOIN-USDT", futures_symbol = "TESTCOINUSDTM")
		self.return_asset 	= asset_info

	def test_assert_spot_futures_pair_does_not_exist(self):
		with patch.object(SqlClient, "get_entry") as mock_get_entry:
			mock_get_entry.return_value = None
			assert(self.client.is_exists() is False)

	def test_assert_spot_futures_pair_does_exist(self):
		with patch.object(SqlClient, "get_entry") as mock_get_entry:
			mock_get_entry.return_value = self.return_asset
			assert(self.client.is_exists() is True)

	@patch("sqlalchemy.orm.Session")
	def test_create_new_entry_adds_new_record_with_correct_symbols_and_values(self, mock_session):
		# TODO: Check that a new row object is created in the DB with 0 volume / lot size
		_client 		= copy.deepcopy(self.client)
		_client.session = mock_session
		_client.create_entry()

		assert(
			(_client.session.add.called) 	and 
			(_client.session.commit.called)
		)