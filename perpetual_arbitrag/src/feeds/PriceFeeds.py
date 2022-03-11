from abc import ABCMeta
from abc import abstractmethod

class PriceFeeds(metaclass = ABCMeta):

	def __init__(self, *args, **kwargs):
		return		

	@abstractmethod
	def sorted_order_book(self, *args, **kwargs):
		"""
		Fetches bid / ask order book in the format
	
		The order book has the following features:
		- Expected datatype	: {"bids" : [[bid_1], [bid_2]], "asks" : [[ask_1], [ask_2]], "updated" : <timestamp>}
		- Sorted book 		: Bids are sorted by highest price first. Asks are sorted by lowest price first.
		- Relevance 		: The book reflects the latest data available. The `updated` field contains the timestamp for the order book
		- Bid / Asks 		: All bids / asks will be structured as [price, qty]
		"""
		pass