import copy
import sys
import pytest
from execution.BotExecutionV2 import BotExecutionV2
from unittest import TestCase
from unittest.mock import MagicMock
class TestBotExecution(TestCase):

	def setUp(self):
		self.bot_executor = BotExecutionV2()

	def test_trade_execution_succeeds(self):
		fn_params = {
						"asset_A_order_fn" 				: MagicMock(return_value = None),
						"asset_A_params" 				: {},
						"asset_A_assert_resp_error_fn" 	: MagicMock(return_value = None),
						"asset_A_revert_fn" 			: MagicMock(return_value = None),
						"asset_A_revert_params" 		: {},
						"asset_B_order_fn" 				: MagicMock(return_value = None),
						"asset_B_params" 				: {},
						"asset_B_assert_resp_error_fn" 	: MagicMock(return_value = None),
						"asset_B_revert_fn" 			: MagicMock(return_value = None),
						"asset_B_revert_params" 		: {},

					}
		
		execution_resp 	= self.bot_executor.idempotent_trade_execution(**fn_params)
		assert execution_resp == True

	def test_trade_execution_fails_for_asset_A_order(self):
		fn_params = {
						"asset_A_order_fn" 				: MagicMock(side_effect = Exception('order failed')),
						"asset_A_params" 				: {},
						"asset_A_assert_resp_error_fn" 	: MagicMock(return_value = None),
						"asset_A_revert_fn" 			: MagicMock(return_value = None),
						"asset_A_revert_params" 		: {},
						"asset_B_order_fn" 				: MagicMock(return_value = None),
						"asset_B_params" 				: {},
						"asset_B_assert_resp_error_fn" 	: MagicMock(return_value = None),
						"asset_B_revert_fn" 			: MagicMock(return_value = None),
						"asset_B_revert_params" 		: {},
					}
		
		execution_resp 	= self.bot_executor.idempotent_trade_execution(**fn_params)
		assert execution_resp == False

	def test_trade_execution_fails_for_asset_A_resp(self):
		fn_params = {
						"asset_A_order_fn" 				: MagicMock(return_value = None),
						"asset_A_params" 				: {},
						"asset_A_assert_resp_error_fn" 	: MagicMock(side_effect = Exception('order failed')),
						"asset_A_revert_fn" 			: MagicMock(return_value = None),
						"asset_A_revert_params" 		: {},
						"asset_B_order_fn" 				: MagicMock(return_value = None),
						"asset_B_params" 				: {},
						"asset_B_assert_resp_error_fn" 	: MagicMock(return_value = None),
						"asset_B_revert_fn" 			: MagicMock(return_value = None),
						"asset_B_revert_params" 		: {},
					}
		
		execution_resp 	= self.bot_executor.idempotent_trade_execution(**fn_params)
		assert execution_resp == False

	def test_trade_execution_fails_for_asset_B_order(self):
		fn_params = {
						"asset_A_order_fn" 				: MagicMock(return_value = None),
						"asset_A_params" 				: {},
						"asset_A_assert_resp_error_fn" 	: MagicMock(return_value = None),
						"asset_A_revert_fn" 			: MagicMock(return_value = None),
						"asset_A_revert_params" 		: {},
						"asset_B_order_fn" 				: MagicMock(side_effect = Exception('order failed')),
						"asset_B_params" 				: {},
						"asset_B_assert_resp_error_fn" 	: MagicMock(return_value = None),
						"asset_B_revert_fn" 			: MagicMock(return_value = None),
						"asset_B_revert_params" 		: {},
					}
		
		execution_resp 	= self.bot_executor.idempotent_trade_execution(**fn_params)
		assert execution_resp == False

	def test_trade_execution_fails_for_asset_B_resp(self):
		fn_params = {
						"asset_A_order_fn" 				: MagicMock(return_value = None),
						"asset_A_params" 				: {},
						"asset_A_assert_resp_error_fn" 	: MagicMock(return_value = None),
						"asset_A_revert_fn" 			: MagicMock(return_value = None),
						"asset_A_revert_params" 		: {},
						"asset_B_order_fn" 				: MagicMock(return_value = None),
						"asset_B_params" 				: {},
						"asset_B_assert_resp_error_fn" 	: MagicMock(side_effect = Exception('order failed')),
						"asset_B_revert_fn" 			: MagicMock(return_value = None),
						"asset_B_revert_params" 		: {},
					}

		execution_resp 	= self.bot_executor.idempotent_trade_execution(**fn_params)
		assert execution_resp == False

	def test_no_revertion_when_asset_A_order_fails(self):
		fn_params = {
						"asset_A_order_fn" 				: MagicMock(side_effect = Exception('order failed')),
						"asset_A_params" 				: {},
						"asset_A_assert_resp_error_fn" 	: MagicMock(return_value = None),
						"asset_A_revert_fn" 			: MagicMock(return_value = None),
						"asset_A_revert_params" 		: {},
						"asset_B_order_fn" 				: MagicMock(return_value = None),
						"asset_B_params" 				: {},
						"asset_B_assert_resp_error_fn" 	: MagicMock(side_effect = Exception('order failed')),
						"asset_B_revert_fn" 			: MagicMock(return_value = None),
						"asset_B_revert_params" 		: {},
					}
		
		execution_resp 	= self.bot_executor.idempotent_trade_execution(**fn_params)
		assert not fn_params["asset_A_revert_fn"].called and not fn_params["asset_B_revert_fn"].called

	def test_asset_A_order_revertion_invoked_when_asset_B_order_fails(self):
		fn_params = {
						"asset_A_order_fn" 				: MagicMock(return_value = {"order_id" : 100}),
						"asset_A_params" 				: {},
						"asset_A_assert_resp_error_fn" 	: MagicMock(return_value = None),
						"asset_A_revert_fn" 			: MagicMock(return_value = None),
						"asset_A_revert_params" 		: {},
						"asset_B_order_fn" 				: MagicMock(side_effect = Exception('order failed')),
						"asset_B_params" 				: {},
						"asset_B_assert_resp_error_fn" 	: MagicMock(return_value = None),
						"asset_B_revert_fn" 			: MagicMock(return_value = None),
						"asset_B_revert_params" 		: {},
					}
		
		execution_resp 	= self.bot_executor.idempotent_trade_execution(**fn_params)
		assert fn_params["asset_A_revert_fn"].called and not fn_params["asset_B_revert_fn"].called