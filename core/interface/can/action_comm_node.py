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
import core.interface.log_management.unified_logger as module_unified_logger


class _CanActionNodeReader(can.Listener) :

	def __init__(self, id, robot=None):
		super().__init__()

		self.id = id
		self.robot = robot  # ADDED BY CLAUDE: Reference to Robot object for position updates

		self.current_command_status = -1
		self.current_command_id = 0
		self.current_action_id = 0
		self.last_completed_command_id = 0
		self.command_error_code = 0

		# IT IS IMPORTANT that this default value be lower than CanActionNode.timestamp_last_command
		self.timestamp_last_tpdo = -2

		# Cache for change detection - stores last logged values
		self.last_logged_values = {
			'command_status': None,
			'command_id': None,
			'action_id': None,
			'completed_command_id': None,
			'error_code': None
		}

	def _has_changed(self, vals):
		"""
		Check if CAN values have changed since last log.

		:param vals: Decoded TPDO values [status, cmd_id, action_id, completed_id, error]
		:return: True if any value changed, False otherwise
		"""
		changed = False

		if vals[0] != self.last_logged_values['command_status']:
			changed = True
		if vals[1] != self.last_logged_values['command_id']:
			changed = True
		if vals[2] != self.last_logged_values['action_id']:
			changed = True
		if vals[3] != self.last_logged_values['completed_command_id']:
			changed = True
		if vals[4] != self.last_logged_values['error_code']:
			changed = True

		return changed


	def _update_cache(self, vals):
		"""
		Update the cache with current values after logging.

		:param vals: Decoded TPDO values to store
		"""
		self.last_logged_values['command_status'] = vals[0]
		self.last_logged_values['command_id'] = vals[1]
		self.last_logged_values['action_id'] = vals[2]
		self.last_logged_values['completed_command_id'] = vals[3]
		self.last_logged_values['error_code'] = vals[4]


	def on_message_received(self, msg):
		"""
		Callback method called automatically by can.Notifier when a CAN message is received.

		This method name is MANDATORY and defined by the can.Listener abstract class.
		Changing the name would break the contract and prevent messages from being processed.

		:param msg: The received CAN message from the bus
		"""

		func, i = canopen_wrapper.instance.determine_message_type(msg)
		id = canopen_wrapper.instance.determine_message_node_id(msg)

		if id == self.id :
			if func == FUNCTION_CODE.IS_TPDO and i == 0 :

				self.timestamp_last_tpdo = time.time()
				try :
					# creates an array of int from the bytes of the message
					vals = canopen_wrapper.instance.decode_tpdo(msg, [0, 1, 1, 2, 2, 3, 3, 4])
					# Log CAN values based on DEBUG_CAN_CHANGES_ONLY setting
					if canopen_wrapper.DEBUG_CAN_CHANGES_ONLY:
						# Only log if values have changed
						if self._has_changed(vals):
							logger.log_info("CanActionNodeReader", f"[Node {id}] CAN CHANGE → status:{vals[0]} cmd_id:{vals[1]} action:{vals[2]} completed:{vals[3]} error:{vals[4]}")
							self._update_cache(vals)

							# MODIFIED BY CLAUDE: Write to unified logger
							if module_unified_logger.unified_logger and module_unified_logger.unified_logger.is_enabled():
								module_unified_logger.unified_logger.log_can_rx(id, vals)
					else:
						# MODIFIED BY CLAUDE: Write to unified logger (in debug mode, log all messages)
						if module_unified_logger.unified_logger and module_unified_logger.unified_logger.is_enabled():
							module_unified_logger.unified_logger.log_can_rx(id, vals)

				except Exception as e :
					logger.log_error("CanActionNodeReader", f"Error decoding TPDO: {e}")

				if vals != None :
					self.current_command_status = vals[0]
					self.current_command_id = vals[1]
					self.current_action_id = vals[2]
					self.last_completed_command_id = vals[3]
					self.command_error_code = vals[4]
					#logger.log_info("CanActionNodeReader", f"[DEBUG] Node {id} Updated current_command_status = {self.current_command_status}")  # ADDED BY CLAUDE: Debug

			# ADDED BY CLAUDE: Handle TPDO[1] - Robot position (X, Y, θ)
			elif func == FUNCTION_CODE.IS_TPDO and i == 1 :
				try :
					# TPDO[1] contains robot position data from odometry
					# Bytes 0-1: X position in mm (INT16, little-endian)
					# Bytes 2-3: Y position in mm (INT16, little-endian)
					# Bytes 4-5: Orientation θ in degrees (INT16, little-endian)
					# Bytes 6-7: Linear velocity in mm/s (INT16, little-endian)

					if len(msg.data) >= 8:
						# Decode INT16 values from little-endian bytes
						x = int.from_bytes(msg.data[0:2], byteorder='little', signed=True)
						y = int.from_bytes(msg.data[2:4], byteorder='little', signed=True)
						angle = int.from_bytes(msg.data[4:6], byteorder='little', signed=True)
						lin_vel = int.from_bytes(msg.data[6:8], byteorder='little', signed=True)
						#logger.log_info("CanActionNodeReader", f"[Node {id}] TPDO[1] Position → X:{x}mm Y:{y}mm θ:{angle}° V:{lin_vel}mm/s")
						# Update robot position if robot object exists
						if self.robot:
							self.robot.update_position(x, y, angle, lin_vel)

				except Exception as e :
					logger.log_error("CanActionNodeReader", f"Error decoding TPDO[1] position: {e}")


	def __string__(self) :
		return f"current_command_status : {self.current_command_status}"

class CanActionNode :

	def __init__(self, bus : can.BusABC, node_id : int, robot=None):

		self.node_id = node_id

		logger.log_info("CanActionNode", f"node with id {node_id} initialized")

		# instantiate the class resposible from catching and interpreting TPDOs
		# MODIFIED BY CLAUDE: Pass robot parameter to enable position updates from TPDO[1]
		self.can_reader = _CanActionNodeReader(node_id, robot=robot)

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
		BUSY = 1
		NOT_BUSY = 0

		try:
			# if we didn't receive any tpdos since the last command, it is likely the node is still busy
			if self.timestamp_last_command > self.can_reader.timestamp_last_tpdo:
				return BUSY

			if ((self.can_reader.current_command_status == CMD_STATUS_RUNNING) or 
				(self.can_reader.current_command_status == -1)):
				return BUSY
			
			# ═══════════════════════════════════════════════════════════
			# NOUVELLE VERSION : Vérifier le bon compteur selon le node
			# ═══════════════════════════════════════════════════════════
			
			# Récupérer le compteur command_id approprié selon le type de node
			if self.node_id == ID_NOEUD_CAN_ASSERV:
				# Pour le node ASSERV, utiliser command_id_asserv
				expected_command_id = canopen_wrapper.instance.command_id_asserv
			elif self.node_id == ID_NOEUD_CAN_AUTOM:
				# Pour le node AUTOM, utiliser command_id_autom
				expected_command_id = canopen_wrapper.instance.command_id_autom
			elif self.node_id == ID_NOEUD_CAN_LIDAR:
				# Pour le node LIDAR, utiliser command_id_lidar
				expected_command_id = canopen_wrapper.instance.command_id_lidar
			else:
				# Fallback pour nodes inconnus : utiliser le compteur global
				expected_command_id = canopen_wrapper.instance.command_id
			
			# Comparer le compteur attendu avec last_completed_command_id
			if expected_command_id == self.can_reader.last_completed_command_id:
				# Log debug info BEFORE returning
				if module_unified_logger.unified_logger and module_unified_logger.unified_logger.is_enabled():
					module_unified_logger.unified_logger.log_python(
						"CanActionNode",
						f"Node {self.node_id} NOT_BUSY: expected_id={expected_command_id} == completed_id={self.can_reader.last_completed_command_id}"
					)
				return NOT_BUSY
			else:
				return BUSY

		except Exception as e:
			error_msg = f"Node {self.node_id} is_busy() error: {type(e).__name__}: {e}"
			if module_unified_logger.unified_logger and module_unified_logger.unified_logger.is_enabled():
				module_unified_logger.unified_logger.log_python("CanActionNode_ERROR", error_msg)
				module_unified_logger.unified_logger.log_python("CanActionNode_TRACEBACK", str(traceback.format_exc()))
			else:
				# Fallback to console if unified_logger not available
				logger.log_error("CanActionNode", error_msg)
				logger.log_traceback("CanActionNode", str(traceback.format_exc()))
				
			return BUSY


			

