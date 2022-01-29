import logging
from execution.BotExecutionV2 import BotExecutionV2

class SpotPerpetualBotExecution(BotExecutionV2):
	api_client 	= None
	logger 		= logging.getLogger('SpotPerpetualBotExecution')

	def __init__(self, api_client):
		self.api_client = api_client
		return

	def long_spot_short_perpetual(self, spot_params, 
										perpetual_params
								):

		spot_params["order_side"] 		= "buy"
		perpetual_params["order_side"] 	= "sell"
		return self.idempotent_trade_execution(	asset_A_order_fn 		= self.api_client.place_perpetual_order,
												asset_A_cancel_fn 		= self.api_client.cancel_perpetual_order,
												asset_A_params 			= perpetual_params,
												asset_A_order_id_ref 	= perpetual_params["order_id_ref"],
												asset_B_order_fn 		= self.api_client.place_spot_order,
												asset_B_cancel_fn 		= self.api_client.cancel_spot_order,
												asset_B_params 			= spot_params,
												asset_B_order_id_ref 	= spot_params["order_id_ref"],
											)

	def short_spot_long_perpetual(self, spot_params, 
										perpetual_params
								):

		spot_params["order_side"] 		= "sell"
		perpetual_params["order_side"] 	= "buy"
		return self.idempotent_trade_execution(	asset_A_order_fn 		= self.api_client.place_spot_order,
												asset_A_cancel_fn 		= self.api_client.cancel_spot_order,
												asset_A_params 			= spot_params,
												asset_A_order_id_ref 	= spot_params["order_id_ref"],
												asset_B_order_fn 		= self.api_client.place_perpetual_order,
												asset_B_cancel_fn 		= self.api_client.cancel_perpetual_order,
												asset_B_params 			= perpetual_params,
												asset_B_order_id_ref 	= perpetual_params["order_id_ref"],
											)