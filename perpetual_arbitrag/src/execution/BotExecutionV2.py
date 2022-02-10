import logging

class BotExecutionV2(object):
	logger 		= logging.getLogger('BotExecutionV2')

	def idempotent_trade_execution(self, asset_A_order_fn,
								 		 asset_A_cancel_fn,
								 		 asset_A_assert_resp_error_fn,
								 		 asset_A_params, 
										 asset_A_order_id_ref: str,
										 asset_B_order_fn,
										 asset_B_cancel_fn,
										 asset_B_assert_resp_error_fn,
										 asset_B_params,
										 asset_B_order_id_ref: str,
								):

		asset_A_order_resp 	= None
		asset_B_order_resp	= None
		is_success 			= True

		try:
			asset_A_order_resp  = asset_A_order_fn(**asset_A_params)
			asset_A_assert_resp_error_fn(asset_A_order_resp)

			asset_B_order_resp 	= asset_B_order_fn(**asset_B_params)
			asset_B_assert_resp_error_fn(asset_B_order_resp)

		except Exception as ex:
			self.logger.error(ex)
			is_success		= False
			
			if asset_A_order_resp is not None:
				asset_A_cancel_fn(order_id = asset_A_order_resp[asset_A_order_id_ref])

			if asset_B_order_resp is not None:
				asset_B_cancel_fn(order_id = asset_B_order_resp[asset_B_order_id_ref])
		return is_success