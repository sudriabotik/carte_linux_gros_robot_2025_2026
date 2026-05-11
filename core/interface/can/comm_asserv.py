"""
Contains functions allowing to send the correct action_id and arguments
at the correct address to control the card.
"""
from enum import IntEnum

import core.interface.can.canopen_wrapper as canopen_wrapper
import time
from core.interface.can.constants import *
from core.interface.can.action_comm_node import CanActionNode, _CanActionNodeReader  # CLAUDE: Import listener class
from core.interface.gpio.gpio import read_gpio_couleur

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

	"""
	NOTE: Les méthodes commençant par "action_" déclenchent automatiquement un wait
	avant leur exécution (via AutoWaitWrapper dans FunctStrat).
	Cela évite les appels manuels wait_asserv()/wait_autom() dans le code stratégie.
	"""

	def __init__(self, bus, node_id : int):
		super().__init__(bus, node_id, _CanActionNodeReader)  # CLAUDE: Pass listener class to parent (robot param removed, set later by init_core.py)
		self.couleur = None

	
	""" 1 pour jaune, 0 pour bleu"""
	def get_couleur(self) :
		return read_gpio_couleur()
	
	def set_couleur(self,couleur: int):
		self.couleur = couleur

	def team_dependent_flip_x_coordinates(self, x) -> int :
		if self.couleur == BLEU:
			return 3000 - x
		else :
			return x # keep original if yellow
	
	def team_dependent_flip_rotation(self, rot) -> int :
		#il ne faut pas utiliser cette fonction
		if self.couleur == BLEU:
			return -rot
		else :
			return rot # keep original if yellow
	
	def team_dependent_flip_orientation(self, orientation) -> int :
		if self.couleur == BLEU:
			if orientation == 0:
				return 180
			elif orientation == 180:
				return 0
		
		return orientation
	

	def action_set_linear_speed_accel(self, speed: float, acceleration : float) :
		"""
		CMD_ACTION_SET_LINEAR_SPD_ACC (1): Set linear speed and acceleration

		:param speed: Linear speed in m/s (ex: 0.1)
		:param acceleration: Linear acceleration in m/s^2 (ex: 0.05)
		"""
		speed_int = int(speed * 1000 )
		accel_int = int(acceleration * 1000)
		canopen_wrapper.instance.request_action(self.node_id, 1, [speed_int, accel_int])
		self.timestamp_last_command = time.time()
	
	def action_set_angular_speed_accel(self, speed: float, acceleration : float) :
		"""
		CMD_ACTION_SET_ANGULAR_SPD_ACC (2): Set angular speed and acceleration

		:param speed: Angular speed in deg/s (ex: 45.0)
		:param acceleration: Angular acceleration in deg/s^2 (ex: 30.0)
		"""
		speed_int = int(speed  )
		accel_int = int(acceleration )
		canopen_wrapper.instance.request_action(self.node_id, 2, [speed_int, accel_int])
		self.timestamp_last_command = time.time()
	
	def action_translation(self, distance_mm: int, speed_percent: int=100, accel_percent: int=100) :
		"""
		CMD_ACTION_TRANSLATION (100): Performs a translation

		:param distance_mm: Distance in mm
		:param speed_percent: Speed coefficient 0-100% (0 or 100 = full speed), default 100
		:param accel_percent: Acceleration coefficient 0-100% (0 or 100 = full accel), default 100
		"""
		canopen_wrapper.instance.request_action(self.node_id, 100, [distance_mm, speed_percent, accel_percent])
		self.timestamp_last_command = time.time()


	def action_rotation(self, angle_deg: int, speed_percent: int=100, accel_percent: int=100) :
		"""
		CMD_ACTION_ROTATION (101): Performs a rotation by the specified angle

		:param angle_deg: Angle in degrees to rotate
		:param speed_percent: Speed coefficient 0-100% (0 or 100 = full speed), default 100
		:param accel_percent: Acceleration coefficient 0-100% (0 or 100 = full accel), default 100
		"""

		angle_deg = self.team_dependent_flip_rotation(angle_deg)

		canopen_wrapper.instance.request_action(self.node_id, 101, [angle_deg, speed_percent, accel_percent])
		self.timestamp_last_command = time.time()


	def action_goto_xy(self, x_mm: int, y_mm : int, face : Face = Face.FACE_AVANT, speed_percent: int=100, accel_percent: int=100) :
		"""
		CMD_ACTION_GOTO (150): Goes to the given point, using the requested face

		:param x_mm: X coordinate in mm
		:param y_mm: Y coordinate in mm
		:param face: Face to use (FACE_AVANT or FACE_ARRIERE), default FACE_AVANT
		:param speed_percent: Speed coefficient 0-100% (0 or 100 = full speed), default 100
		:param accel_percent: Acceleration coefficient 0-100% (0 or 100 = full accel), default 100
		"""
		x_mm = self.team_dependent_flip_x_coordinates(x_mm)

		canopen_wrapper.instance.request_action(self.node_id, 150, [x_mm, y_mm, face, speed_percent, accel_percent])
		self.timestamp_last_command = time.time()


	def action_recalibration(self, facing : Facing, face : Face, speed_percent: int=12, accel_percent: int=12) :
		"""
		CMD_ACTION_RECALIBRATE (152): Resets a coordinate of the robot using the walls of the table

		:param facing: Direction to recalibrate (POSITIVE_X, POSITIVE_Y, NEGATIVE_X, NEGATIVE_Y)
		:param face: Face to use during recalibration (FACE_AVANT or FACE_ARRIERE)
		:param speed_percent: Speed coefficient 0-100% (0 or 100 = full speed), default 10
		:param accel_percent: Acceleration coefficient 0-100% (0 or 100 = full accel), default 10
		"""
		"""
		if self.get_couleur() == 0 : # bleu 
			if facing == Facing.POSITIVE_X :
				facing = Facing.NEGATIVE_X
			elif facing == Facing.NEGATIVE_X :
				facing = Facing.POSITIVE_X
		"""
		canopen_wrapper.instance.request_action(self.node_id, 152, [facing, face, speed_percent, accel_percent])
		self.timestamp_last_command = time.time()


	def action_moveto(self, x_mm: int, y_mm : int, face : Face, speed_percent: int=100, accel_percent: int=100) :
		"""
		CMD_ACTION_MOVETO (151): Moves to the given point using the requested face (without rotation)

		:param x_mm: X coordinate in mm
		:param y_mm: Y coordinate in mm
		:param face: Face to use (FACE_AVANT or FACE_ARRIERE)
		:param speed_percent: Speed coefficient 0-100% (0 or 100 = full speed), default 100
		:param accel_percent: Acceleration coefficient 0-100% (0 or 100 = full accel), default 100
		"""
		canopen_wrapper.instance.request_action(self.node_id, 151, [x_mm, y_mm, face, speed_percent, accel_percent])
		self.timestamp_last_command = time.time()


	def action_lookat(self, x_mm: int, y_mm : int, face : Face, speed_percent: int=100, accel_percent: int=100) :
		"""
		CMD_ACTION_LOOKAT (153): Rotates to look at the given point using the requested face

		:param x_mm: X coordinate in mm to look at
		:param y_mm: Y coordinate in mm to look at
		:param face: Face to use (FACE_AVANT or FACE_ARRIERE)
		:param speed_percent: Speed coefficient 0-100% (0 or 100 = full speed), default 100
		:param accel_percent: Acceleration coefficient 0-100% (0 or 100 = full accel), default 100
		"""

		x_mm = self.team_dependent_flip_x_coordinates(x_mm)

		canopen_wrapper.instance.request_action(self.node_id, 153, [x_mm, y_mm, face, speed_percent, accel_percent])
		self.timestamp_last_command = time.time()


	def action_debug_on_off(self, enable: bool) :
		"""
		CMD_DEBUG_ON_OFF (9): Enables or disables debug UART of asservissement to view the graphe.

		:param enable: True to enable debug output, False to disable
		"""
		canopen_wrapper.instance.request_action(self.node_id, 3, [1 if enable else 0])
		self.timestamp_last_command = time.time()


	def action_orientation(self, target_angle_deg: float, face: Face = Face.FACE_AVANT,
	                       speed_percent: int = 100, accel_percent: int = 100) :
		"""
		CMD_ACTION_ORIENTATION (154): Sets the robot orientation to a specific angle

		:param target_angle_deg: Target orientation in degrees
		:param face: Face to use (FACE_AVANT or FACE_ARRIERE), default FACE_AVANT
		:param speed_percent: Speed coefficient 0-100% (0 or 100 = full speed), default 100
		:param accel_percent: Acceleration coefficient 0-100% (0 or 100 = full accel), default 100
		"""

		target_angle_deg = self.team_dependent_flip_orientation(target_angle_deg)

		canopen_wrapper.instance.request_action(self.node_id, 154,
			[int(target_angle_deg), face, speed_percent, accel_percent])
		self.timestamp_last_command = time.time()

	def action_evitement_on_off(self,enable: bool):
		'''
		CMD_EVITEMENT_ON_OFF pour activer l'evitement ou le desactiver 
		:param enable: True to enable evitement, False to disable
		'''
		canopen_wrapper.instance.request_action(self.node_id, 4, [1 if enable else 0])
		self.timestamp_last_command = time.time()
	
	def action_evitement(self) :

		canopen_wrapper.instance.request_action(self.node_id, 12, [])
		self.timestamp_last_command = time.time()

	def action_set_pid_vitesse(self, kp: float, ki: float, kd: float, kff: float = 0.0, i_lim: float = 0.0):
		"""
		CMD_SET_PID_VITESSE (6): Configure les coefficients PID vitesse moteurs (roues droite et gauche)
		
		:param kp: Coefficient proportionnel (ex: 0.23)
		:param ki: Coefficient integral (ex: 0.4)
		:param kd: Coefficient derive (ex: 20.0)
		:param kff: Coefficient feedforward (optionnel, ex: 0.0)
		:param i_lim: Limite de l'intégrale (optionnel, ex: 50.0)
		"""
		kp_int = int(kp * 1000)
		ki_int = int(ki * 1000)
		kd_int = int(kd * 1000)
		kff_int = int(kff * 1000)
		i_lim_int = int(i_lim * 1000)
		
		canopen_wrapper.instance.request_action(
			self.node_id, 
			6, 
			[kp_int, ki_int, kd_int, kff_int, i_lim_int]
		)
		self.timestamp_last_command = time.time()

	def action_set_pid_translation(self, kp: float, ki: float, kd: float):
		"""
		CMD_SET_PID_COEFF_TRA (8): Configure les coefficients PID de translation

		:param kp: Coefficient proportionnel (ex: 2.0)
		:param ki: Coefficient integral (ex: 0.8)
		:param kd: Coefficient derive (ex: 0.2)
		"""
		kp_int = int(kp * 1000)
		ki_int = int(ki * 1000)
		kd_int = int(kd * 1000)
		canopen_wrapper.instance.request_action(self.node_id, 8, [kp_int, ki_int, kd_int])
		self.timestamp_last_command = time.time()


	def action_set_pid_rotation(self, kp: float, ki: float, kd: float):
		"""
		CMD_SET_PID_COEFF_ROT (9): Configure les coefficients PID de rotation

		:param kp: Coefficient proportionnel (ex: 2.0)
		:param ki: Coefficient integral (ex: 0.8)
		:param kd: Coefficient derive (ex: 0.2)
		"""
		kp_int = int(kp * 1000 )
		ki_int = int(ki * 1000 )
		kd_int = int(kd * 1000 )
		canopen_wrapper.instance.request_action(self.node_id, 9, [kp_int, ki_int, kd_int])
		self.timestamp_last_command = time.time()

	def action_set_pid_hold(self, kp: float, ki: float, kd: float, max_output: float, 
                        i_lim: float = 0.0, min_output: float = 0.0):
		"""
		CMD_ACTION_SET_PID_HOLD (10): Configure les coefficients PID Hold
		
		:param kp: Coefficient proportionnel (ex: 1.5)
		:param ki: Coefficient integral (ex: 0.5)
		:param kd: Coefficient derive (ex: 0.1)
		:param max_output: Sortie maximale du PID (ex: 100.0)
		:param i_lim: Limite de l'intégrale (optionnel, ex: 50.0)
		:param min_output: Sortie minimale du PID (optionnel, ex: -100.0)
		"""
		kp_int = int(kp * 1000)
		ki_int = int(ki * 1000)
		kd_int = int(kd * 1000)
		max_output_int = int(max_output * 100)
		i_lim_int = int(i_lim * 1000)
		
		canopen_wrapper.instance.request_action(
			self.node_id, 10,[kp_int, ki_int, kd_int, max_output_int, i_lim_int]
		)
		self.timestamp_last_command = time.time()