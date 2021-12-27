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
		asset_info.futures_lot_size = 50

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

	@patch("sqlalchemy.orm.Session")
	def test_set_position(self, mock_session):
		_client 		= copy.deepcopy(self.client)
		_client.session = mock_session

		with patch.object(SqlClient, "get_entry") as mock_get_entry:
			mock_get_entry.return_value = self.return_asset
			_client.set_position(spot_volume = -100, futures_lot_size = 1000)
			modified_row = mock_get_entry.return_value
			
			assert(	(modified_row.spot_volume == -100) 		and 
					(modified_row.futures_lot_size == 1000) and
					(_client.session.commit.called)
				)

	@patch("sqlalchemy.orm.Session")
	def test_set_spot_volume(self, mock_session):
		_client 		= copy.deepcopy(self.client)
		_client.session = mock_session

		with patch.object(SqlClient, "get_entry") as mock_get_entry:
			mock_get_entry.return_value = self.return_asset
			_client.set_spot_volume(volume = -100)
			modified_row = mock_get_entry.return_value
			
			assert(	(modified_row.spot_volume == -100) and 
					(_client.session.commit.called)
				)

	@patch("sqlalchemy.orm.Session")
	def test_set_futures_lot_size(self, mock_session):
		_client 		= copy.deepcopy(self.client)
		_client.session = mock_session

		with patch.object(SqlClient, "get_entry") as mock_get_entry:
			mock_get_entry.return_value = self.return_asset
			_client.set_futures_lot_size(lot_size = -100)
			modified_row = mock_get_entry.return_value
			
			assert(	(modified_row.futures_lot_size == -100) and 
					(_client.session.commit.called)
				)

	def test_get_position(self):
		with patch.object(SqlClient, "get_entry") as mock_get_entry:
			mock_get_entry.return_value = self.return_asset
			(spot_volume, futures_lot_size) = self.client.get_position()
			assert(spot_volume == 10 and futures_lot_size == 50)

	def test_get_spot_volume(self):
		with patch.object(SqlClient, "get_entry") as mock_get_entry:
			mock_get_entry.return_value = self.return_asset
			spot_volume = self.client.get_spot_volume()
			assert(spot_volume == 10)

	def test_get_futures_lot_size(self):
		with patch.object(SqlClient, "get_entry") as mock_get_entry:
			mock_get_entry.return_value = self.return_asset
			futures_lot_size = self.client.get_futures_lot_size()
			assert(futures_lot_size == 50)