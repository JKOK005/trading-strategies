from execution.BotExecution import BotExecution
import logging

class BotSimulatedExecution(BotExecution):
	logger = logging.getLogger('BotSimulatedExecution')

	def __init__(self, 	*args, **kwargs):
		self.logger.warning("Order execution is simulated.")
		super(BotSimulatedExecution, self).__init__(*args, *kwargs)

	def _place_spot_order(self, symbol: str,
								order_type: str,
								order_side: str,
								price: int,
								size: float
						):
		return 	{"orderId" : "0001"}

	def _place_futures_order(self, 	symbol: str,
									order_type: str,
									order_side: str,
									price: int,
									size: int,
									lever: int
							):
		return 	{"orderId" : "0002"}