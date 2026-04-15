"""
Base class for canopen nodes implementing the TPDO and RPDO necessary for action requests.
See docs/action_comm.md
"""

import core.interface.can.canopen_wrapper as canopen_wrapper
from core.interface.can.canopen_wrapper import FUNCTION_CODE
import can
import traceback
import threading
import time

from core.interface.can.constants import *
import core.interface.log_management.logger as logger



class CanCommNode :

	def __init__(self, bus : can.BusABC, node_id : int, listener : can.Listener):

		self.node_id : int = node_id

		logger.log_info("CanActionNode", f"node with id {node_id} initialized")

		self.can_reader = listener

		canopen_wrapper.instance.register_listener(self.can_reader)

		self.thread_lock = threading.Lock()

		print(f"node {self.node_id} created")

	

	def __del__(self) :

		self.can_reader.stop()
	


