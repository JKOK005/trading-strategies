import copy
import sys
import pytest
from execution.FailSafeTrigger import FailSafeTrigger, FailSafeException
from unittest import TestCase
from unittest.mock import MagicMock

class TestFailSafeTrigger(TestCase):
	def setUp(self):
		self.fail_safe_trigger = FailSafeTrigger(counts_to_trigger = 4)
		return

	def test_increment_trigger_without_exceed(self):
		_fail_safe_trigger = copy.deepcopy(self.fail_safe_trigger)
		
		_fail_safe_trigger.increment(trigger_exception_on_exceed = True)
		assert _fail_safe_trigger.trigger == 1

		_fail_safe_trigger.increment(trigger_exception_on_exceed = True)
		assert _fail_safe_trigger.trigger == 2

	def test_increment_trigger_with_exceed(self):
		_fail_safe_trigger = copy.deepcopy(self.fail_safe_trigger)
		_fail_safe_trigger.counts_to_trigger = 1

		with self.assertRaises(FailSafeException):
			_fail_safe_trigger.increment(trigger_exception_on_exceed = True)
		return

	def test_increment_trigger_exception_disabled(self):
		_fail_safe_trigger = copy.deepcopy(self.fail_safe_trigger)
		_fail_safe_trigger.counts_to_trigger = 1
		_fail_safe_trigger.increment(trigger_exception_on_exceed = False)
		assert _fail_safe_trigger.trigger == 1
	
	def test_reset_trigger(self):
		_fail_safe_trigger = copy.deepcopy(self.fail_safe_trigger)
		
		_fail_safe_trigger.increment(trigger_exception_on_exceed = True)
		assert _fail_safe_trigger.trigger == 1

		_fail_safe_trigger.reset()
		assert _fail_safe_trigger.trigger == 0