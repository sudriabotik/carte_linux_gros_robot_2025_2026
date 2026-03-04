"""
Contains functions allowing to send the correct action_id and arguments
at the correct address to control the card.
"""

import canopen_wrapper
import canopen


# all the state enum from the C code

class CommAutom :

	def __init__(self, network : canopen.Network,  node_id : int, dictionary_path : str):
		self.node = canopen.RemoteNode(node_id, dictionary_path)
		network.add_node(self.node)
		self.node.nmt.state = 'PRE-OPERATIONAL'
		self.node.rpdo.read()
		self.node.tpdo.read()
		self.node.nmt.state = 'OPERATIONAL'

		self.node.tpdo[1].add_callback(lambda data : self._on_tpdo_reception(data))
		self.node.tpdo[1].enabled = True
		self.node.tpdo[1].save()
	

	def _on_tpdo_reception(self, data) :
		print(f"received tpdo {data}")
		for var in data :
			print(f"{var.name} : {var.raw}")
		print("")
	

	def get_od(self) :
		return self.node.object_dictionary


	def action_homing(self, speed_h_percent: int = 8, speed_v_percent : int = 8) :
		"""
		performs the homing (initialisation of the motor positions using the switches)
		"""
		canopen_wrapper.instance.request_action(self.node, 1, [speed_h_percent, speed_h_percent])


	def action_grab(self) :
		"""
		performs a grab
		"""
		canopen_wrapper.instance.request_action(self.node, 2, []) # no args to give


	def action_pos_elevator_h(self, pos_mm : int) :
		"""
		sets the horizontal position of the elevator
		"""
		canopen_wrapper.instance.request_action(self.node, 4, [pos_mm])


	def action_pos_elevator_v(self, pos_mm : int) :
		"""
		sets the vertical position of the elevator
		"""
		canopen_wrapper.instance.request_action(self.node, 5, [pos_mm])

