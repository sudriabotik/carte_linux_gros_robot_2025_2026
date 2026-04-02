"""
Robot State Module

This module provides the Robot class which maintains the robot's position state.
The position is automatically updated from CAN TPDO[1] messages received from
the asserv node (odometry).

TPDO[1] format (CAN ID 0x281 for node 1):
- Bytes 0-1: Position X in mm (INT16, little-endian)
- Bytes 2-3: Position Y in mm (INT16, little-endian)
- Bytes 4-5: Orientation θ in degrees (INT16, little-endian)
- Bytes 6-7: Unused

The position is updated at ~10Hz (every 100ms) from the microcontroller.
"""


class Robot:
	"""
	Represents the robot's state, including position and orientation.

	The position is automatically updated when TPDO[1] messages are received
	from the asserv node via CAN bus.
	"""

	def __init__(self, node_asserv=None, node_autom=None):
		"""
		Initialize the Robot with references to the control nodes.

		:param node_asserv: Reference to the asserv/odometry node (optional)
		:param node_autom: Reference to the automation node (optional)
		"""
		# References to control nodes
		self.asserv = node_asserv
		self.autom = node_autom

		#couleur equipe
		self.couleur_equipe = None

		# Robot position state (updated from TPDO[1])
		self.position_x = 0  # Position X in millimeters
		self.position_y = 0  # Position Y in millimeters
		self.angle = 0       # Orientation θ in degrees
		self.lin_vel = 0     # Linear velocity in mm/s

	def update_couleur_equipe(self, couleur_equipe):
		self.couleur_equipe = couleur_equipe

	def update_position(self, x, y, angle, lin_vel=0):
		"""
		Update the robot's position from TPDO[1] data.

		This method is called automatically by the CAN listener when a TPDO[1]
		message is received from the asserv node.

		:param x: Position X in millimeters (INT16)
		:param y: Position Y in millimeters (INT16)
		:param angle: Orientation θ in degrees (INT16)
		:param lin_vel: Linear velocity in mm/s (INT16), default 0
		"""
		self.position_x = x
		self.position_y = y
		self.angle = angle
		self.lin_vel = lin_vel

	def get_position(self):
		"""
		Get the current position as a tuple.

		:return: Tuple (x, y, angle) with x, y in mm and angle in degrees
		"""
		return (self.position_x, self.position_y, self.angle)

	def __str__(self):
		"""
		String representation of the robot's position.

		:return: Formatted string with position information
		"""
		return f"Robot(x={self.position_x}mm, y={self.position_y}mm, θ={self.angle}°, v={self.lin_vel}mm/s)"

	def __repr__(self):
		"""
		Technical representation of the robot.

		:return: Technical string representation
		"""
		return f"Robot(x={self.position_x}, y={self.position_y}, angle={self.angle}, lin_vel={self.lin_vel})"

