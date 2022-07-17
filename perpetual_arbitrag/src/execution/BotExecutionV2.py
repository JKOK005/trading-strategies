import asyncio
import logging
import json

class BotExecutionV2(object):
	logger 		= logging.getLogger('BotExecutionV2')

	async def _trade_execution(self, trade_fnct, trade_params):
		resp_future = await trade_fnct(**trade_params)
		resp 		= await resp_future
		return json.loads(resp)

	async def _trade_pair_execution(self, 	asset_A_order_fn, asset_A_params, 
											asset_B_order_fn, asset_B_params):

		[resp_A_future, resp_B_future] = await asyncio.gather(
												asset_A_order_fn(**asset_A_params), 
												asset_B_order_fn(**asset_B_params)
											)
		resp_A = await resp_A_future
		resp_B = await resp_B_future
		return [json.loads(resp_A), json.loads(resp_B)]

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
		
		self.logger.info(f"{asset_A_order_resp}")
		self.logger.info(f"{asset_B_order_resp}")
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

		[asset_A_order_resp_unordered, asset_B_order_resp_unordered] = asyncio.get_event_loop().run_until_complete(
																				self._trade_pair_execution(
																					asset_A_order_fn = asset_A_order_fn, 
																					asset_A_params = asset_A_params,
																					asset_B_order_fn = asset_B_order_fn,
																					asset_B_params = asset_B_params
																				)
																			)

		# By convention, asset A is the asset we are shorting and asset B is the asset we are going long
		asset_A_order_resp = asset_A_order_resp_unordered if "sell" in asset_A_order_resp_unordered["id"] else asset_B_order_resp_unordered
		asset_B_order_resp = asset_B_order_resp_unordered if "buy" 	in asset_B_order_resp_unordered["id"] else asset_A_order_resp_unordered

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
			asset_A_params = {"order_resp" : asset_A_order_resp, "revert_params" : asset_A_revert_params}
			asyncio.get_event_loop().run_until_complete(
										self._trade_execution(
											trade_fnct = asset_A_revert_fn, 
											trade_params = asset_A_params,
										)
									)

		elif asset_B_order_succeed and not asset_A_order_succeed:
			asset_B_params = {"order_resp" : asset_B_order_resp, "revert_params" : asset_B_revert_params}
			asyncio.get_event_loop().run_until_complete(
										self._trade_execution(
											trade_fnct = asset_B_revert_fn, 
											trade_params = asset_B_params,
										)
									)
					
		self.logger.info(f"{asset_A_order_resp}")
		self.logger.info(f"{asset_B_order_resp}")
		return asset_A_order_succeed and asset_B_order_succeed

	