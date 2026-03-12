import can

import sys
import traceback

import logger


COB_ID_RPDO = [0b0100, 0b0110, 0b1000, 0b1010]
COB_ID_TPDO = [0b0011, 0b0101, 0b0111, 0b1001]


class CanopenWrapper :

	def __init__(self, bus : can.BusABC):
		
		self.network = bus
		self.command_id = 1 # TEMP
	

	def send_rpdo(self, node_id : int, rpdo_num : int, data : list[int]) :
		"""
		Send a rpdo with the given data as bytes
		"""

		msg = can.Message(arbitration_id=COB_ID_RPDO[rpdo_num] << 7 | node_id, data=data, is_extended_id=False)

		logger.log_info("CanOpenWrapper", f"sending rpdo {msg}")

		self.network.send(msg, timeout=None)

		logger.log_info("CanOpenWrapper", f"sent rpdo ")

	

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
			
			logger.log_info("CanOpenWrapper", f"requesting to node {node_id} the action {action_id} with arguments {param_resized}")

			# prepare data for first rpdo

			data = \
			[
				action_id & 0xFF,
				(action_id << 8) & 0xFF,
				param_resized[0] & 0xFF,
				(param_resized[0] << 8) & 0xFF, 
				param_resized[1] & 0xFF,
				(param_resized[1] << 8) & 0xFF, 
				param_resized[2] & 0xFF,
				(param_resized[2] << 8) & 0xFF, 
			]

			self.send_rpdo(node_id=node_id, rpdo_num=0, data=data)

			# prepare data for second rpdo

			self.command_id += 1 # TEMP

			data = \
			[
				param_resized[0] & 0xFF,
				(param_resized[0] << 8) & 0xFF, 
				param_resized[1] & 0xFF,
				(param_resized[1] << 8) & 0xFF, 
				param_resized[2] & 0xFF,
				(param_resized[2] << 8) & 0xFF, 
				self.command_id & 0xFF,
				(self.command_id << 8) & 0xFF,
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
