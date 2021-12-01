class BotExecution(object):
	api_client = None

	def __init__(self, 	api_client):
		self.api_client = api_client

	def _place_spot_order(self, symbol: str,
								order_type: str,
								order_side: str,
								price: int,
								size: float
						):
		return 	self.api_client.place_spot_order(symbol 	= symbol,
												 order_type = order_type,
												 order_side = order_side,
												 price 		= price,
												 size 		= size
												)

	def _place_futures_order(self, 	symbol: str,
									order_type: str,
									order_side: str,
									price: int,
									size: int,
									lever: int
							):
		return 	self.api_client.place_futures_order(symbol 		= symbol,
													order_type 	= order_type,
													order_side 	= order_side,
													price 		= price,
													size 		= size,
													lever 		= lever
											)

	def long_spot_short_futures(self, 	spot_symbol: str,
										spot_order_type: str,
										spot_price: int,
										spot_size: float,
										futures_symbol: str,
										futures_order_type: str,
										futures_price: int,
										futures_size: int,
										futures_lever: int
								):
		spot_order_id 			= None
		futures_order_id		= None

		try:
			spot_order_id  		= self._place_spot_order(symbol 	= spot_symbol,
														 order_type = spot_order_type,
														 order_side = "buy",
														 price 		= spot_price,
														 size 		= spot_size
													)

			futures_order_id 	= self._place_futures_order(symbol 		= futures_symbol,
															order_type 	= futures_order_type,
															order_side 	= "sell",
															price 		= futures_price,
															size 		= futures_size,
															lever 		= futures_lever
														)
		except Exception as ex:
			# TODO: Delete straggling open orders
			pass

	def short_spot_long_futures(self, 	spot_symbol: str,
										spot_order_type: str,
										spot_price: int,
										spot_size: float,
										futures_symbol: str,
										futures_order_type: str,
										futures_price: int,
										futures_size: int,
										futures_lever: int
								):
		spot_order_id 			= None
		futures_order_id		= None

		try:
			spot_order_id  		= self._place_spot_order(symbol 	= spot_symbol,
														 order_type = spot_order_type,
														 order_side = "sell",
														 price 		= spot_price,
														 size 		= spot_size
													)

			futures_order_id 	= self._place_futures_order(symbol 		= futures_symbol,
															order_type 	= futures_order_type,
															order_side 	= "buy",
															price 		= futures_price,
															size 		= futures_size,
															lever 		= futures_lever
														)
		except Exception as ex:
			# TODO: Delete straggling open orders
			pass

