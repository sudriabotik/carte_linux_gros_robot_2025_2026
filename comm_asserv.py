"""
Contains functions allowing to send the correct action_id and arguments
at the correct address to control the asserv card.
"""

import canopen_wrapper
import canopen

CAN_ASSERV_ID = 2


class CommAsserv :

	def __init__(self):
		self.node = canopen.RemoteNode(2, "dic.eds")

	def comm_asserv_translation(self, distance : float, speed : float, accel : float) :
		"""
		performs a simple translation.
		:param float distance: The distance to travel in mm.
		Can be set negative to go backwards.
		:param float speed: The speed in mm/s.
		:param float accel: The acceleration in mm/s^2.
		"""

		canopen_wrapper.instance.request_action(self.node, 10, [distance, speed, accel])


instance = CommAsserv()