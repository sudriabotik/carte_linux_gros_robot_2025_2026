"""
Base class for canopen nodes implementing the TPDO and RPDO necessary for action requests.
See docs/action_comm.md
"""

import canopen
import can
import traceback
import time
import threading

from robot_comm_data import *
import logger

class CanActionNode :

	def __init__(self, network : canopen.Network,  node_id : int, dictionary_path : str):

		self._lock = threading.Lock()
		self._lock.acquire()

		self.node = canopen.RemoteNode(node_id, dictionary_path)
		network.add_node(self.node)
		self.node.nmt.state = 'PRE-OPERATIONAL'
		self.node.rpdo.read()
		self.node.tpdo.read()
		self.node.nmt.state = 'OPERATIONAL'

		self.node.tpdo[1].add_callback(lambda data : self._on_tpdo_reception(data))
		self.node.tpdo[1].enabled = True
		self.node.tpdo[1].save()

		self.time_last_tpdo = time.time()

		logger.log_info("CanActionNode", f"node with id {node_id} initialized")

		self._lock.release()

		
	

	def _on_tpdo_reception(self, data) :
		print(f"received tpdo {data}")
		for var in data :
			print(f"{var.name} : {var.raw}")
		print("")
		self.time_last_tpdo = time.time()
	

	def is_busy(self) :
		"""
		Check if the node is currently executing a command
		"""

		self._lock.acquire()

		try :
			print(f"{self.node.object_dictionary["current_command_status"].value}")
			return self.node.object_dictionary["current_command_status"].value not in (CMD_STATUS_IDLE, CMD_STATUS_COMPLETED, CMD_STATUS_ABORTED)
		except Exception as e :
			logger.log_error("CanActionNode", f"error : {type(e).__name__}: {e}")
			logger.log_traceback("CanActionNode", str(traceback.format_exc()))
		
		self._lock.release()
	

	def is_locked(self) :
		"""
		Checks whether another thread has locked this object
		"""
		return self._lock.locked()


	def get_problems(self) :
		return None	
	

	def get_od(self) :
		return self.node.object_dictionary

