class FailSafeException(Exception):
	def __init__(self, trigger):
		super(FailSafeException, self).__init__(f"Trigger {trigger} exceeded.")
		return

class FailSafeTrigger(object):
	trigger = 0

	def __init__(self, counts_to_trigger: int):
		self.counts_to_trigger = counts_to_trigger
		return

	def increment(self, trigger_exception_on_exceed: bool = True):
		self.trigger += 1
		if self.trigger >= self.counts_to_trigger and trigger_exception_on_exceed:
			raise FailSafeException(trigger = self.trigger)
		return self.trigger

	def reset(self):
		self.trigger = 0
		return self.trigger