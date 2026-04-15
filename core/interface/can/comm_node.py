"""
Base class for canopen nodes implementing the TPDO and RPDO necessary for action requests.
See docs/action_comm.md
"""

from abc import ABC, abstractmethod
import core.interface.can.canopen_wrapper as canopen_wrapper
from core.interface.can.canopen_wrapper import FUNCTION_CODE
import can
import traceback
import threading
import time

from core.interface.can.constants import *
import core.interface.log_management.logger as logger



class CanActionNode :

	def __init__(self, bus : can.BusABC, node_id : int, listener : any):

		self.node_id : int = node_id

		logger.log_info("CanActionNode", f"node with id {node_id} initialized")

		# instantiate the class resposible from catching and interpreting TPDOs
		# MODIFIED BY CLAUDE: Pass robot parameter to enable position updates from TPDO[1]
		self.can_reader = listener(node_id, robot=robot)

		#######
		# The 'can' library creates a single thread to listen for CAN messages continuously.
		# We use the Notifier to register 'self.can_reader' as the callback handler
		# that will be called each time a message is received.
		########
		# FIXED BY CLAUDE: Use the singleton Notifier from canopen_wrapper instead of creating a new one
		# This prevents the "multiple active Notifier instances" error
		canopen_wrapper.instance.register_listener(self.can_reader)

		self.thread_lock = threading.Lock()

		self.timestamp_last_command = -1

		print(f"node {self.node_id} created on thread : {threading.get_native_id()}")

	

	def __del__(self) :

		self.can_reader.stop()
	

	def is_busy(self) :
		"""
		Check if the node is currently executing a command
		"""
		#print(f"vars : {self.can_reader.current_command_status}")

		# if we didn't receive any tpdos since the last command, it is likely the node is still busy
		if self.timestamp_last_command > self.can_reader.timestamp_last_tpdo : return True
		
		try :
			return (self.can_reader.current_command_status == 1) or self.can_reader.current_command_status == -1
		except Exception as e :
			logger.log_error("CanActionNode", f"error : {type(e).__name__}: {e}")
			logger.log_traceback("CanActionNode", str(traceback.format_exc()))
			


