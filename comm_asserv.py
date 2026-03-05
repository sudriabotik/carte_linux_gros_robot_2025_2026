"""
Contains functions allowing to send the correct action_id and arguments
at the correct address to control the card.
"""

import canopen_wrapper
import canopen

from action_comm_node import CanActionNode


# all the state enum from the C code

class CanAsservNode(CanActionNode) : 

	def __init__(self, network : canopen.Network,  node_id : int, dictionary_path : str):
		super().__init__(network,  node_id, dictionary_path)
	


	def action_translation(self, distance_mm: int, speed : int, accel : int) :
		"""
		performs a translation
		The speed is in thousandths of mm/ms
		The acceleration is in thousandths of mm/ms^2
		"""
		canopen_wrapper.instance.request_action(self.node, 1, [distance_mm, speed, accel])
	

	def action_goto_xy(self, x_mm: int, y_mm : int) :
		"""
		performs the homing (initialisation of the motor positions using the switches)
		"""
		canopen_wrapper.instance.request_action(self.node, 3, [x_mm, y_mm])

