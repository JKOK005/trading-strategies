import copy
import logging
from execution.BotExecutionV2 import BotExecutionV2

class MarginPerpetualBotExecution(BotExecutionV2):
	api_client 	= None
	logger 		= logging.getLogger('MarginPerpetualBotExecution')

	def __init__(self, api_client):
		self.api_client = api_client
		return

	def long_margin_short_perpetual(self, margin_params,
									  	  perpetual_params,
								):

		margin_entry_params 	= copy.copy(margin_params)
		margin_revert_params 	= copy.copy(margin_params)
		perpetual_revert_params = copy.copy(perpetual_params)

		margin_entry_params["order_side"] 		= "buy"
		margin_entry_params["size"] 			= margin_params["entry_size"]
		
		margin_revert_params["order_side"] 		= "sell"
		margin_revert_params["size"] 			= margin_params["revert_size"]
		
		perpetual_params["order_side"] 			= "sell"
		perpetual_revert_params["order_side"] 	= "buy"

		self.logger.info(margin_params)
		self.logger.info(perpetual_params)

		return self.idempotent_trade_execution_async(asset_A_order_fn 				= self.api_client.place_perpetual_order,
													 asset_A_params 					= perpetual_params,
													 asset_A_assert_resp_error_fn 	= self.api_client.assert_perpetual_resp_error,
													 asset_A_revert_fn 				= self.api_client.revert_perpetual_order,
													 asset_A_revert_params 			= perpetual_revert_params,
													 asset_B_order_fn 				= self.api_client.place_margin_order,
													 asset_B_params 					= margin_entry_params,
													 asset_B_assert_resp_error_fn 	= self.api_client.assert_margin_resp_error,
													 asset_B_revert_fn 				= self.api_client.revert_margin_order,
													 asset_B_revert_params 			= margin_revert_params
												)

	def short_margin_long_perpetual(self, margin_params,
									  	  perpetual_params,
								):

		margin_entry_params 	= copy.copy(margin_params)
		margin_revert_params 	= copy.copy(margin_params)
		perpetual_revert_params = copy.copy(perpetual_params)

		margin_entry_params["order_side"] 		= "sell"
		margin_entry_params["size"] 			= margin_params["entry_size"]

		margin_revert_params["order_side"] 		= "buy"
		margin_revert_params["size"] 			= margin_params["revert_size"]
		
		perpetual_params["order_side"] 			= "buy"
		perpetual_revert_params["order_side"] 	= "sell"

		self.logger.info(margin_params)
		self.logger.info(perpetual_params)

		return self.idempotent_trade_execution_async(asset_A_order_fn 				= self.api_client.place_margin_order,
													 asset_A_params 					= margin_entry_params,
													 asset_A_assert_resp_error_fn 	= self.api_client.assert_margin_resp_error,
													 asset_A_revert_fn 				= self.api_client.revert_margin_order,
													 asset_A_revert_params 			= margin_revert_params,
													 asset_B_order_fn 				= self.api_client.place_perpetual_order,
													 asset_B_params 					= perpetual_params,
													 asset_B_assert_resp_error_fn 	= self.api_client.assert_perpetual_resp_error,
													 asset_B_revert_fn 				= self.api_client.revert_perpetual_order,
													 asset_B_revert_params 			= perpetual_revert_params
												)

class MarginPerpetualSimulatedBotExecution(MarginPerpetualBotExecution):
	def __init__(self, *args, **kwargs):
		self.logger.warning("Order execution is simulated.")
		super(MarginPerpetualSimulatedBotExecution, self).__init__(*args, *kwargs)

	def long_margin_short_perpetual(self, *args, **kwargs):
		return True

	def short_margin_long_perpetual(self, *args, **kwargs):
		return True