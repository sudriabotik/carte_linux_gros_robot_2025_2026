"""
Contains functions allowing to send the correct action_id and arguments
at the correct address to control the card.
"""
from enum import IntEnum

import canopen_wrapper
import time

from action_comm_node import CanActionNode

class Face(IntEnum) :

	FACE_AVANT = 0
	FACE_ARRIERE = 1


class Facing(IntEnum) :
	POSITIVE_X = 0
	POSITIVE_Y = 1
	NEGATIVE_X = 2
	NEGATIVE_Y = 3


# all the state enum from the C code

class CanAsservNode(CanActionNode) : 

	def __init__(self, bus, node_id : int):
		super().__init__(bus, node_id)
	

	def action_set_linear_speed_accel(self, speed: int, acceleration : int) :
		"""
		performs the homing (initialisation of the motor positions using the switches)
		The speed is in thousandths of mm/ms
		The velocity is in thousandths of mm/ms^2
		"""
		canopen_wrapper.instance.request_action(self.node_id, 1, [speed, acceleration])
		self.timestamp_last_command = time.time()
	
	def action_set_angular_speed_accel(self, speed: int, acceleration : int) :
		"""
		performs the homing (initialisation of the motor positions using the switches)
		The speed is in thousandths of deg/ms
		The velocity is in thousandths of deg/ms^2
		"""
		canopen_wrapper.instance.request_action(self.node_id, 2, [speed, acceleration])
		self.timestamp_last_command = time.time()
	
	def action_goto_xy(self, x_mm: int, y_mm : int, face : Face) :
		"""
		Goes to the given point, using the requested face
		"""
		canopen_wrapper.instance.request_action(self.node_id, 5, [x_mm, y_mm, face])
		self.timestamp_last_command = time.time()

	def action_translation(self, distance_mm: int, speed : int, accel : int) :
		"""
		performs a translation
		The speed is in thousandths of mm/ms
		The acceleration is in thousandths of mm/ms^2
		"""
		canopen_wrapper.instance.request_action(self.node_id, 3, [distance_mm, speed, accel])
		self.timestamp_last_command = time.time()
	

	def action_recalibration(self, facing : Facing, face : Face) :
		"""
		Resets a coordinate of the robot using the walls of the table
		"""
		canopen_wrapper.instance.request_action(self.node_id, 6, [facing, face])
		self.timestamp_last_command = time.time()

