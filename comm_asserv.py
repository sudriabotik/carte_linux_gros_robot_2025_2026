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

	def __init__(self, bus, node_id : int, robot=None):
		# MODIFIED BY CLAUDE: Pass robot parameter to parent class for position updates
		super().__init__(bus, node_id, robot=robot)
	

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
	
	def action_translation(self, distance_mm: int, speed : int, accel : int) :
		"""
		performs a translation
		The speed is in thousandths of mm/ms
		The acceleration is in thousandths of mm/ms^2
		"""
		canopen_wrapper.instance.request_action(self.node_id, 3, [distance_mm, speed, accel])
		self.timestamp_last_command = time.time()


	def action_rotation(self, angle_deg: int, speed : int, accel : int) :
		"""
		CMD_ACTION_ROTATION (4): Performs a rotation by the specified angle

		:param angle_deg: Angle in degrees to rotate
		:param speed: Angular speed in thousandths of deg/ms
		:param accel: Angular acceleration in thousandths of deg/ms^2
		"""
		canopen_wrapper.instance.request_action(self.node_id, 4, [angle_deg, speed, accel])
		self.timestamp_last_command = time.time()


	def action_goto_xy(self, x_mm: int, y_mm : int, face : Face) :
		"""
		CMD_ACTION_GOTO (5): Goes to the given point, using the requested face

		:param x_mm: X coordinate in mm
		:param y_mm: Y coordinate in mm
		:param face: Face to use (FACE_AVANT or FACE_ARRIERE)
		"""
		canopen_wrapper.instance.request_action(self.node_id, 5, [x_mm, y_mm, face])
		self.timestamp_last_command = time.time()


	def action_recalibration(self, facing : Facing, face : Face) :
		"""
		CMD_ACTION_RECALIBRATE (6): Resets a coordinate of the robot using the walls of the table

		:param facing: Direction to recalibrate (POSITIVE_X, POSITIVE_Y, NEGATIVE_X, NEGATIVE_Y)
		:param face: Face to use during recalibration (FACE_AVANT or FACE_ARRIERE)
		"""
		canopen_wrapper.instance.request_action(self.node_id, 6, [facing, face])
		self.timestamp_last_command = time.time()


	def action_moveto(self, x_mm: int, y_mm : int, face : Face) :
		"""
		CMD_ACTION_MOVETO (7): Moves to the given point using the requested face (without rotation)

		:param x_mm: X coordinate in mm
		:param y_mm: Y coordinate in mm
		:param face: Face to use (FACE_AVANT or FACE_ARRIERE)
		"""
		canopen_wrapper.instance.request_action(self.node_id, 7, [x_mm, y_mm, face])
		self.timestamp_last_command = time.time()


	def action_lookat(self, x_mm: int, y_mm : int, face : Face) :
		"""
		CMD_ACTION_LOOKAT (8): Rotates to look at the given point using the requested face

		:param x_mm: X coordinate in mm to look at
		:param y_mm: Y coordinate in mm to look at
		:param face: Face to use (FACE_AVANT or FACE_ARRIERE)
		"""
		canopen_wrapper.instance.request_action(self.node_id, 8, [x_mm, y_mm, face])
		self.timestamp_last_command = time.time()


	def action_debug_on_off(self, enable: bool) :
		"""
		CMD_DEBUG_ON_OFF (9): Enables or disables debug UART of asservissement to view the graphe. 

		:param enable: True to enable debug output, False to disable
		"""
		canopen_wrapper.instance.request_action(self.node_id, 9, [1 if enable else 0])
		self.timestamp_last_command = time.time()

