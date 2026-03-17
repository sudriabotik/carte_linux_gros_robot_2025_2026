"""
Base class for canopen nodes implementing the TPDO and RPDO necessary for action requests.
See docs/action_comm.md
"""

import canopen_wrapper
from canopen_wrapper import FUNCTION_CODE
import can
import traceback
import threading

from robot_comm_data import *
import logger



class _CanActionNodeReader(can.Listener) :

	def __init__(self):
		super().__init__()

		self.current_command_status = -1
		self.current_command_id = 0
		self.current_action_id = 0
		self.last_completed_command_id = 0
		self.command_error_code = 0

	def on_message_received(self, msg):

		print(f"message received on thread : {threading.get_native_id()}")

		logger.log_verbose("CanActionNodeReader", "message received")
		
		func, i = canopen_wrapper.instance.determine_message_type(msg)
		id = canopen_wrapper.instance.determine_message_node_id(msg)

		if id :
			logger.log_verbose("CanActionNodeReader", f"received message from {id}")
			if func == FUNCTION_CODE.IS_TPDO and i == 0 :

				logger.log_verbose("CanActionNodeReader", "message is TPDO 0")
				try :
					vals = canopen_wrapper.instance.decode_tpdo(msg, [0, 1, 1, 2, 2, 3, 3, 4])
					logger.log_verbose("CanActionNodeReader", f"received {vals}")
				except Exception as e :
					print(f"{e}")
				logger.log_verbose("CanActionNodeReader", f"received {vals}")
				if vals != None :
					self.current_command_status = vals[0]
					self.current_command_id = vals[1]
					self.current_action_id = vals[2]
					self.last_completed_command_id = vals[3]
					self.command_error_code = vals[4]
					logger.log_verbose("CanActionNodeReader", "variables updated")
	
	def __string__(self) :
		return f"current_command_status : {self.current_command_status}"



class CanActionNode :

	def __init__(self, bus : can.BusABC, node_id : int):

		self.node_id = node_id

		logger.log_info("CanActionNode", f"node with id {node_id} initialized")

		self.can_reader = _CanActionNodeReader()
		can.Notifier(bus, [self.can_reader])

		self.thread_lock = threading.Lock()

		print(f"node {self.node_id} created on thread : {threading.get_native_id()}")
	

	def __del__(self) :

		self.can_reader.stop()
	

	def is_busy(self) :
		"""
		Check if the node is currently executing a command
		"""
		print(f"vars : {self.can_reader.current_command_status}")
		
		try :
			return not (self.can_reader.current_command_status in [2,3,4])
		except Exception as e :
			logger.log_error("CanActionNode", f"error : {type(e).__name__}: {e}")
			logger.log_traceback("CanActionNode", str(traceback.format_exc()))
			

