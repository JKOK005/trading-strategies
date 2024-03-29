import copy
import logging
from execution.BotExecutionV2 import BotExecutionV2

class SpotPerpetualBotExecution(BotExecutionV2):
	api_client 	= None
	logger 		= logging.getLogger('SpotPerpetualBotExecution')

	def __init__(self, api_client):
		self.api_client = api_client
		return

	def long_spot_short_perpetual(self, spot_params,
									  	perpetual_params,
									  	spot_revert_params,
									  	perpetual_revert_params,
								):
		self.logger.info(spot_params)
		self.logger.info(perpetual_params)
		return self.idempotent_trade_execution_async(asset_A_order_fn 				= self.api_client.place_perpetual_order_async,
													 asset_A_params 				= perpetual_params,
													 asset_A_assert_resp_error_fn 	= self.api_client.assert_perpetual_resp_error,
													 asset_A_revert_fn 				= self.api_client.revert_perpetual_order_async,
													 asset_A_revert_params 			= perpetual_revert_params,
													 asset_B_order_fn 				= self.api_client.place_spot_order_async,
													 asset_B_params 				= spot_params,
													 asset_B_assert_resp_error_fn 	= self.api_client.assert_spot_resp_error,
													 asset_B_revert_fn 				= self.api_client.revert_spot_order_async,
													 asset_B_revert_params 			= spot_revert_params
												)

	def short_spot_long_perpetual(self, spot_params,
									  	perpetual_params,
									  	spot_revert_params,
									  	perpetual_revert_params,
								):
		self.logger.info(spot_params)
		self.logger.info(perpetual_params)
		return self.idempotent_trade_execution_async(asset_A_order_fn 				= self.api_client.place_spot_order_async,
												 	 asset_A_params 				= spot_params,
												 	 asset_A_assert_resp_error_fn 	= self.api_client.assert_spot_resp_error,
													 asset_A_revert_fn 				= self.api_client.revert_spot_order_async,
												 	 asset_A_revert_params 			= spot_revert_params,
												 	 asset_B_order_fn 				= self.api_client.place_perpetual_order_async,
													 asset_B_params 				= perpetual_params,
												 	 asset_B_assert_resp_error_fn 	= self.api_client.assert_perpetual_resp_error,
													 asset_B_revert_fn 				= self.api_client.revert_perpetual_order_async,
												 	 asset_B_revert_params 			= perpetual_revert_params
												)

class SpotPerpetualSimulatedBotExecution(SpotPerpetualBotExecution):
	def __init__(self, *args, **kwargs):
		self.logger.warning("Order execution is simulated.")
		super(SpotPerpetualSimulatedBotExecution, self).__init__(*args, *kwargs)

	def long_spot_short_perpetual(self, *args, **kwargs):
		return True

	def short_spot_long_perpetual(self, *args, **kwargs):
		return True