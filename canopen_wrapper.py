import canopen
import can

import sys
import traceback


class CanopenWrapper :

	def __init__(self, bus : can.BusABC):
		
		self.network = canopen.Network(bus)
		self.action_id = 1 # TEMP
	

	def request_action(self, node : canopen.RemoteNode, action_id : int, params : list) :
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
			
			node.rpdo[1]["ACTION_ID"].raw = action_id

			node.rpdo[1]["param_1"].raw = param_resized[0]
			node.rpdo[1]["param_2"].raw = param_resized[1]
			node.rpdo[1]["param_3"].raw = param_resized[2]

			node.rpdo[2]["param_4"].raw = param_resized[3]
			node.rpdo[2]["param_5"].raw = param_resized[4]
			node.rpdo[2]["param_6"].raw = param_resized[5]

			self.action_id += 1 # TEMP
			node.rpdo[2]["Command_ID"].raw = self.action_id # TEMP

			node.rpdo[1].transmit()
			node.rpdo[2].transmit()

			return True
		
		except Exception as e :
			sys.stderr.write(f"error : {type(e).__name__}: {e}\n")
			sys.stderr.write(f"traceback : {traceback.format_exc()}\n")
			
			return False

instance : CanopenWrapper = None
