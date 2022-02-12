import logging

class BotExecutionV2(object):
	logger 		= logging.getLogger('BotExecutionV2')

	def idempotent_trade_execution(self, asset_A_order_fn,
								 		 asset_A_cancel_fn,
								 		 asset_A_assert_resp_error_fn,
								 		 asset_A_params, 
										 asset_B_order_fn,
										 asset_B_cancel_fn,
										 asset_B_assert_resp_error_fn,
										 asset_B_params,
								):

		asset_A_order_resp 		= None
		asset_B_order_resp 		= None
		asset_A_order_succeed 	= False
		asset_B_order_succeed	= False

		try:
			asset_A_order_resp  = asset_A_order_fn(**asset_A_params)
			asset_A_assert_resp_error_fn(asset_A_order_resp)
			asset_A_order_succeed 	= True

			asset_B_order_resp 	= asset_B_order_fn(**asset_B_params)
			asset_B_assert_resp_error_fn(asset_B_order_resp)
			asset_B_order_succeed 	= True

		except Exception as ex:
			self.logger.error(ex)

			if asset_A_order_succeed:
				asset_A_cancel_fn(order_resp = asset_A_order_resp)

			if asset_B_order_succeed:
				asset_B_cancel_fn(order_resp = asset_B_order_resp)
					
		return asset_A_order_succeed and asset_B_order_succeed