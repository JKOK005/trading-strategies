from abc import ABCMeta
from abc import abstractmethod

class BaseClients(metaclass = ABCMeta):
	@abstractmethod
	def get_client_id(self):
		"""
		Retrieves unique identifier for client ID
		"""
		return