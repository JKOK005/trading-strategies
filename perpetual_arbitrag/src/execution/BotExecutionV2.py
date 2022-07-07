import asyncio
import logging

class BotExecutionV2(object):
	logger 		= logging.getLogger('BotExecutionV2')

	async def _trade_execution(self, trade_fnct, trade_params):
		return trade_fnct(**trade_params)

	async def _trade_pair_execution(self, 	asset_A_order_fn, asset_A_params, 
											asset_B_order_fn, asset_B_params):

		return await asyncio.gather(
							self._trade_execution(trade_fnct = asset_A_order_fn, trade_params = asset_A_params), 
							self._trade_execution(trade_fnct = asset_B_order_fn, trade_params = asset_B_params)
						)

	def idempotent_trade_execution(self, asset_A_order_fn,
								 		 asset_A_revert_fn,
								 		 asset_A_assert_resp_error_fn,
								 		 asset_A_params,
								 		 asset_A_revert_params,
										 asset_B_order_fn,
										 asset_B_revert_fn,
										 asset_B_assert_resp_error_fn,
										 asset_B_params,
										 asset_B_revert_params
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
				asset_A_revert_fn(order_resp = asset_A_order_resp, revert_params = asset_A_revert_params)

			if asset_B_order_succeed:
				asset_B_revert_fn(order_resp = asset_B_order_resp, revert_params = asset_B_revert_params)
					
		return asset_A_order_succeed and asset_B_order_succeed

	def idempotent_trade_execution_async(self, 	asset_A_order_fn,
										 		asset_A_revert_fn,
										 		asset_A_assert_resp_error_fn,
										 		asset_A_params,
										 		asset_A_revert_params,
												asset_B_order_fn,
												asset_B_revert_fn,
												asset_B_assert_resp_error_fn,
												asset_B_params,
												asset_B_revert_params
								):

		asset_A_order_resp 		= None
		asset_B_order_resp 		= None
		asset_A_order_succeed 	= False
		asset_B_order_succeed	= False

		[asset_A_order_resp, asset_B_order_resp] = asyncio.get_event_loop().run_until_complete(
																				self._trade_pair_execution(
																					asset_A_order_fn = asset_A_order_fn, 
																					asset_A_params = asset_A_params,
																					asset_B_order_fn = asset_B_order_fn,
																					asset_B_params = asset_B_params
																				)
																			)
		try:
			asset_A_assert_resp_error_fn(asset_A_order_resp)
			asset_A_order_succeed 	= True
		except Exception as ex:
			self.logger.error(ex)

		try:
			asset_B_assert_resp_error_fn(asset_B_order_resp)
			asset_B_order_succeed 	= True
		except Exception as ex:
			self.logger.error(ex)

		if asset_A_order_succeed and not asset_B_order_succeed:
			asset_A_revert_fn(order_resp = asset_A_order_resp, revert_params = asset_A_revert_params)

		elif asset_B_order_succeed and not asset_A_order_succeed:
			asset_B_revert_fn(order_resp = asset_B_order_resp, revert_params = asset_B_revert_params)
					
		elif not asset_A_order_succeed and not asset_B_order_succeed:
			asyncio.get_event_loop().run_until_complete(
										self._trade_pair_execution(
											asset_A_order_fn = asset_A_revert_fn, 
											asset_A_params = asset_A_revert_params,
											asset_B_order_fn = asset_B_revert_fn,
											asset_B_params = asset_B_revert_params
										)
									)
		return asset_A_order_succeed and asset_B_order_succeed

	