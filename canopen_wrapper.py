"""
A simple wrapper around the python-can library to enable sending and interpreting messages as canopen messages.
"""

import can
from enum import Enum

import sys
import traceback

import logger


COB_ID_RPDO = [0b0100, 0b0110, 0b1000, 0b1010]
COB_ID_TPDO = [0b0011, 0b0101, 0b0111, 0b1001]

# FIXED BY CLAUDE: Convert signed int16 to unsigned uint16 using two's complement
# This is necessary to correctly encode negative values for CAN transmission
def to_uint16(value):
	"""
	Convert a signed INT16 value to unsigned UINT16 using two's complement.

	Example: -50 becomes 65486 (0xFFCE)
	This allows negative values to be correctly transmitted over CAN and
	interpreted by the microcontroller as signed values.

	:param value: Signed integer value
	:return: Unsigned 16-bit representation
	"""
	if value < 0:
		return value & 0xFFFF
	return value

class FUNCTION_CODE(Enum) :
	IS_UNKNOWN = 0
	IS_RPDO = 1
	IS_TPDO = 2


class CanopenWrapper :

	def __init__(self, bus : can.BusABC):
		
		self.network = bus
		self.command_id = 1 # TEMP

		self.notifier = can.Notifier(bus=bus)

	
	def add_listener(self, listener : can.Listener) :
		self.notifier.add_listener(listener)
	

	def send_rpdo(self, node_id : int, rpdo_num : int, data : list[int]) :
		"""
		Send a rpdo with the given data as bytes
		"""

		msg = can.Message(arbitration_id=COB_ID_RPDO[rpdo_num] << 7 | node_id, data=data, is_extended_id=False)

		logger.log_info("CanOpenWrapper", f"sending rpdo {msg}")

		self.network.send(msg, timeout=None)

		logger.log_info("CanOpenWrapper", f"sent rpdo ")
	

	def determine_message_node_id(self, msg : can.Message) -> int :
		node_id = msg.arbitration_id & 0b1111111 # 7 bits ID
		return node_id
	

	def determine_message_type(self, msg : can.Message) -> tuple[FUNCTION_CODE, int] :
		
		id = msg.arbitration_id
		function_code = (id >> 7) & 0xF

		for i in range(len(COB_ID_RPDO)) :
			if COB_ID_RPDO[i] == function_code : return FUNCTION_CODE.IS_RPDO, i
		
		for i in range(len(COB_ID_TPDO)) :
			if COB_ID_TPDO[i] == function_code : return FUNCTION_CODE.IS_TPDO, i
		

		# if correspond to nothing, is unknown
		return FUNCTION_CODE.IS_UNKNOWN, 0



	def decode_tpdo(self, msg : can.Message, slots : list[int]) -> list[int] :
		"""
		The number of times an index appear in the list indicates how much space a variable takes.
		IMPORTANT : THE INDICES MUST BE FROM HIGHEST TO LOWEST
		"""

		vals = [0] * (slots[-1] + 1)

		if len(slots) != len(msg.data) :
			logger.log_error("CanOpenWrapper", f"tpdo decoding : given byte slots length {len(slots)} not equal to message byte length {len(msg.data)}")

		try :

			consecutive = 0
			last_val = None
			i = 0
			while i < len(slots) :

				if slots[i] == last_val : consecutive += 1
				else : consecutive = 0

				vals[slots[i]] = vals[slots[i]] | (msg.data[i] << (consecutive*8))

				last_val = slots[i]

				i += 1
		
		except Exception as e :
			logger.log_error("CanOpenWrapper", f"tpdo decoding : {e}")
		
		return vals
	

	def request_action(self, node_id : int, action_id : int, params : list) :
		"""
		Sends RPDOS to modify a set of value to give to the node the action_id and parameters.
		"""

		"""
		Expects that the RPDO1 is used for : action_id, argument_1, argument_2, argument_3.
		RPDO2 should map to argument_4, argument_5, argument_6, command_id
		"""

		try :
			param_resized = params.copy()
			if len(param_resized) > 6 :
				raise ValueError(f"too many parameters given for an action request")
			if len(param_resized) < 6 :
				param_resized += [0] * (6 - len(param_resized))

			for i in range(len(param_resized)) :
				param_resized[i] = int(param_resized[i])
			
			logger.log_info("CanOpenWrapper", f"requesting to node {node_id} the action {action_id} with arguments {param_resized}")

			# FIXED BY CLAUDE: Convert to uint16 to handle negative values correctly
			action_id_u16 = to_uint16(action_id)
			param_0_u16 = to_uint16(param_resized[0])
			param_1_u16 = to_uint16(param_resized[1])
			param_2_u16 = to_uint16(param_resized[2])

			# prepare data for first rpdo
			# FIXED BY CLAUDE: Corrected bit shifts to match send_rpdo_interactive.py

			data = \
			[
				action_id_u16 & 0xFF,
				(action_id_u16 >> 8) & 0xFF,  # Extract high byte with right shift
				param_0_u16 & 0xFF,
				(param_0_u16 >> 8) & 0xFF,  # Extract high byte with right shift
				param_1_u16 & 0xFF,
				(param_1_u16 >> 8) & 0xFF,  # Extract high byte with right shift
				param_2_u16 & 0xFF,
				(param_2_u16 >> 8) & 0xFF,  # Extract high byte with right shift
			]

			self.send_rpdo(node_id=node_id, rpdo_num=0, data=data)

			# prepare data for second rpdo

			self.command_id += 1 # TEMP

			# FIXED BY CLAUDE: Convert to uint16 to handle negative values correctly
			param_3_u16 = to_uint16(param_resized[3])
			param_4_u16 = to_uint16(param_resized[4])
			param_5_u16 = to_uint16(param_resized[5])
			command_id_u16 = to_uint16(self.command_id)

			# FIXED BY CLAUDE: Use correct parameters (3,4,5) and right shift to match send_rpdo_interactive.py
			data = \
			[
				param_3_u16 & 0xFF,  # Use param_3 (not param_0)
				(param_3_u16 >> 8) & 0xFF,  # Extract high byte with right shift
				param_4_u16 & 0xFF,  # Use param_4 (not param_1)
				(param_4_u16 >> 8) & 0xFF,  # Extract high byte with right shift
				param_5_u16 & 0xFF,  # Use param_5 (not param_2)
				(param_5_u16 >> 8) & 0xFF,  # Extract high byte with right shift
				command_id_u16 & 0xFF,
				(command_id_u16 >> 8) & 0xFF,  # Extract high byte with right shift
			]

			self.send_rpdo(node_id=node_id, rpdo_num=1, data=data)
			
			"""
			node.rpdo[1]["ACTION_ID"].raw = action_id

			node.rpdo[1]["param_1"].raw = param_resized[0]
			node.rpdo[1]["param_2"].raw = param_resized[1]
			node.rpdo[1]["param_3"].raw = param_resized[2]

			node.rpdo[2]["param_4"].raw = param_resized[3]
			node.rpdo[2]["param_5"].raw = param_resized[4]
			node.rpdo[2]["param_6"].raw = param_resized[5]

			self.action_id += 1 # TEMP
			node.rpdo[2]["Command_ID"].raw = self.action_id # TEMP

			node.rpdo[1].save()
			node.rpdo[2].save()

			node.rpdo[1].transmit()
			node.rpdo[2].transmit()

			"""

			return True
		
		except Exception as e :
			sys.stderr.write(f"error : {type(e).__name__}: {e}\n")
			sys.stderr.write(f"traceback : {traceback.format_exc()}\n")
			
			return False

instance : CanopenWrapper = None