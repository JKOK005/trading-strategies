import copy
import logging
from execution.BotExecutionV2 import BotExecutionV2

class SpotFutureBotExecution(BotExecutionV2):
	api_client 	= None
	logger 		= logging.getLogger('SpotFutureBotExecution')

	def __init__(self, api_client):
		self.api_client = api_client
		return

	def long_spot_short_futures(self, spot_params,
									  future_params,
									  spot_revert_params,
									  future_revert_params,
								):
		self.logger.info(spot_params)
		self.logger.info(future_params)
		return self.idempotent_trade_execution(	asset_A_order_fn 				= self.api_client.place_futures_order,
												asset_A_params 					= future_params,
												asset_A_assert_resp_error_fn 	= self.api_client.assert_futures_resp_error,
												asset_A_revert_fn 				= self.api_client.revert_futures_order,
												asset_A_revert_params 			= future_revert_params,
												asset_B_order_fn 				= self.api_client.place_spot_order,
												asset_B_params 					= spot_params,
												asset_B_assert_resp_error_fn 	= self.api_client.assert_spot_resp_error,
												asset_B_revert_fn 				= self.api_client.revert_spot_order,
												asset_B_revert_params 			= spot_revert_params
											)

	def short_spot_long_futures(self, spot_params,
									  future_params,
									  spot_revert_params,
									  future_revert_params,
								):		
		self.logger.info(spot_params)
		self.logger.info(future_params)
		return self.idempotent_trade_execution(	asset_A_order_fn 				= self.api_client.place_spot_order,
												asset_A_params 					= spot_params,
												asset_A_assert_resp_error_fn 	= self.api_client.assert_spot_resp_error,
												asset_A_revert_fn 				= self.api_client.revert_spot_order,
												asset_A_revert_params 			= spot_revert_params,
												asset_B_order_fn 				= self.api_client.place_futures_order,
												asset_B_params 					= future_params,
												asset_B_assert_resp_error_fn 	= self.api_client.assert_futures_resp_error,
												asset_B_revert_fn 				= self.api_client.revert_futures_order,
												asset_B_revert_params 			= future_revert_params
											)

class SpotFutureSimulatedBotExecution(SpotFutureBotExecution):
	def __init__(self, *args, **kwargs):
		self.logger.warning("Order execution is simulated.")
		super(SpotFutureSimulatedBotExecution, self).__init__(*args, *kwargs)

	def long_spot_short_futures(self, *args, **kwargs):
		return True

	def short_spot_long_futures(self, *args, **kwargs):
		return True