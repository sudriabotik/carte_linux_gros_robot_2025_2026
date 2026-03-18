"""
Contains functions allowing to send the correct action_id and arguments
at the correct address to control the card.
"""

import canopen_wrapper
import time

from action_comm_node import CanActionNode


# all the state enum from the C code

class CanAutomNode(CanActionNode) : 

	def __init__(self, node_id : int):
		super().__init__(node_id)
	


	def action_homing(self, speed_h_percent: int = 8, speed_v_percent : int = 8) :
		"""
		performs the homing (initialisation of the motor positions using the switches)
		"""
		canopen_wrapper.instance.request_action(self.node_id, 1, [speed_h_percent, speed_h_percent])
		self.timestamp_last_command = time.time()


	def action_grab(self) :
		"""
		performs a grab
		"""
		canopen_wrapper.instance.request_action(self.node_id, 2, []) # no args to give
		self.timestamp_last_command = time.time()


	def action_pos_elevator_h(self, pos_mm : int) :
		"""
		sets the horizontal position of the elevator
		"""
		canopen_wrapper.instance.request_action(self.node_id, 4, [pos_mm])
		self.timestamp_last_command = time.time()


	def action_pos_elevator_v(self, pos_mm : int) :
		"""
		sets the vertical position of the elevator
		"""
		canopen_wrapper.instance.request_action(self.node_id, 5, [pos_mm])
		self.timestamp_last_command = time.time()

