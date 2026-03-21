"""
Base class for canopen nodes implementing the TPDO and RPDO necessary for action requests.
See docs/action_comm.md
"""

import canopen_wrapper
from canopen_wrapper import FUNCTION_CODE
import can
import traceback
import threading
import time

from robot_comm_data import *
import logger



class _CanActionNodeReader(can.Listener) :

	def __init__(self, id):
		super().__init__()

		self.id = id

		self.current_command_status = -1
		self.current_command_id = 0
		self.current_action_id = 0
		self.last_completed_command_id = 0
		self.command_error_code = 0

		# IT IS IMPORTANT that this default value be lower than CanActionNode.timestamp_last_command
		self.timestamp_last_tpdo = -2

	def on_message_received(self, msg):
		"""
		Callback method called automatically by can.Notifier when a CAN message is received.
		
		This method name is MANDATORY and defined by the can.Listener abstract class.
		Changing the name would break the contract and prevent messages from being processed.
		
		:param msg: The received CAN message from the bus
		"""

		logger.log_verbose("CanActionNodeReader", "message received")
		
		func, i = canopen_wrapper.instance.determine_message_type(msg)
		id = canopen_wrapper.instance.determine_message_node_id(msg)

		if id == self.id :
			logger.log_verbose("CanActionNodeReader", f"received message from {id}")
			if func == FUNCTION_CODE.IS_TPDO and i == 0 :

				logger.log_verbose("CanActionNodeReader", "message is TPDO 0")

				self.timestamp_last_tpdo = time.time()
				try :
					# creates an array of int from the bytes of the message
					vals = canopen_wrapper.instance.decode_tpdo(msg, [0, 1, 1, 2, 2, 3, 3, 4])
					logger.log_error("CanActionNodeReader", f"received vals {vals}")
				except Exception as e :
					logger.log_error("CanActionNodeReader", str(e))

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

		# instantiate the class resposible from catching and interpreting TPDOs
		self.can_reader = _CanActionNodeReader()

		#######
		# The 'can' library creates a single thread to listen for CAN messages continuously.
		# We use the Notifier to register 'self.can_reader' as the callback handler
		# that will be called each time a message is received.
		########
		can.Notifier(bus, [self.can_reader])  # <- Important line of the project

		self.thread_lock = threading.Lock()

		self.timestamp_last_command = -1

		print(f"node {self.node_id} created on thread : {threading.get_native_id()}")
	

	def __del__(self) :

		self.can_reader.stop()
	

	def is_busy(self) :
		"""
		Check if the node is currently executing a command
		"""
		print(f"vars : {self.can_reader.current_command_status}")

		# if we didn't receive any tpdos since the last command, it is likely the node is still busy
		if self.timestamp_last_command > self.can_reader.timestamp_last_tpdo : return True
		
		try :
			return (self.can_reader.current_command_status == 1) or self.can_reader.current_command_status == -1
		except Exception as e :
			logger.log_error("CanActionNode", f"error : {type(e).__name__}: {e}")
			logger.log_traceback("CanActionNode", str(traceback.format_exc()))
			

