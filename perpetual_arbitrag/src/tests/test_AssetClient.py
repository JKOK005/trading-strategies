import copy
import sys
import sqlalchemy
from db.AssetClient import *
from sqlalchemy.orm import Session, declarative_base
from unittest import TestCase
from unittest.mock import patch, MagicMock

BASE = declarative_base()

class AssetTableMock(AssetInfoTable, BASE):
	__tablename__ 		= "asset_table_mock"

class AssetClientMock(AssetClient):
	def table_ref(self):
		return AssetTableMock

	def new_table(self):
		return AssetTableMock( strategy_id = self.strategy_id, client_id = self.client_id, exchange = self.exchange,
							   symbol = self.symbol, size = 0, units = self.units)

	def __init__(self, **kwargs):
		super(AssetClientMock, self).__init__(**kwargs)
		return

class TestAssetClient(TestCase):

	def setUp(self):
		asset_info 				= AssetTableMock()
		asset_info.strategy_id 	= "123"
		asset_info.client_id 	= "456"
		asset_info.exchange 	= "exchange"
		asset_info.symbol 		= "TESTCOIN-USDT"
		asset_info.size 		= 10
		asset_info.units 		= "vol"

		self.client 		= AssetClientMock(	url = "blank", strategy_id = "123", client_id = "456", 
												exchange = "exchange", symbol = "TESTCOIN-USDT", units = "vol")
		self.client.session = MagicMock()
		self.return_asset 	= asset_info

	def test_assert_does_not_exist(self):
		with patch.object(AssetClientMock, "get_entry") as mock_get_entry:
			mock_get_entry.return_value = None
			assert(self.client.is_exists() is False)	

	def test_assert_does_exist(self):
		with patch.object(AssetClientMock, "get_entry") as mock_get_entry:
			mock_get_entry.return_value = self.return_asset
			assert(self.client.is_exists() is True)

	def test_create_new_entry_adds_new_record_with_correct_symbols_and_values(self):
		_client = copy.deepcopy(self.client)
		_client.session.return_value.__enter__.return_value = _client.session
		_client.create_entry()
		assert(_client.session.add.called)

	def test_set_position(self):
		_client = copy.deepcopy(self.client)
		_client.session.return_value.__enter__.return_value = _client.session

		with patch.object(AssetClientMock, "get_entry") as mock_get_entry:
			mock_get_entry.return_value = self.return_asset
			_client.set_position(size = -100)
			modified_row = mock_get_entry.return_value
			assert(modified_row.size == -100)

	def test_get_position(self):
		with patch.object(AssetClientMock, "get_entry") as mock_get_entry:
			mock_get_entry.return_value = self.return_asset
			size = self.client.get_position()
			assert(size == 10)