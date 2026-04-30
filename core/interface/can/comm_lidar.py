"""
Contains functions allowing to send the correct action_id and arguments
at the correct address to control the card.
"""

from typing import Callable  # CLAUDE: Use Callable instead of FunctionType for Python 3.11 compatibility
#from typing import override
from typing import Type
from typing_extensions import override

import can

import core.interface.can.canopen_wrapper as canopen_wrapper
import core.interface.log_management.logger as logger
import math
import time

from core.interface.can.comm_node import CanCommNode
from core.robot.robot import Robot



class _CanLidarNodeReader(can.Listener) :

	def __init__(self, id : int, on_msg_callback : Callable):  # CLAUDE: Callable instead of FunctionType
		super().__init__()

		self.id : int = id;

		self.opponent_x : int
		self.opponent_y : int
		self.lidar_status : int

		self.timestamp_last_tpdo : float = -2

		self.on_msg_callback : Callable = on_msg_callback  # CLAUDE: Callable instead of FunctionType
	

	@override
	def on_message_received(self, msg: can.Message) -> None:

		func, i = canopen_wrapper.instance.determine_message_type(msg)
		id = canopen_wrapper.instance.determine_message_node_id(msg)

		if id == self.id :

			if func == canopen_wrapper.FUNCTION_CODE.IS_TPDO :

				if i == 0 :

					# this is the packet contaning data about the opponent's position and the lidar status.
					vals = canopen_wrapper.instance.decode_tpdo(msg, [0, 0, 1, 1, 2])

					if (vals != None) :
						self.opponent_x = vals[0]
						self.opponent_y = vals[1]
						self.lidar_status = vals[2]

						self.timestamp_last_tpdo = time.time()

						self.on_msg_callback()

					else :
						logger.log_info("CanActionNode", f"error receiving TPDO 1 for node {self.id}")
			



class CanLidarNode(CanCommNode) :

	def __init__(self, bus : can.BusABC, node_id : int, robot : Robot | None):

		def callback() : self.process_opponent_data()
		
		self.lidar_reader : _CanLidarNodeReader = _CanLidarNodeReader(node_id, callback)

		super().__init__(bus, node_id, self.lidar_reader)

		self.robot : Robot | None = robot
		self.on_evitement : Callable | None  # CLAUDE: Callable instead of FunctionType
	
	def get_opponent_pos(self) :
		return (self.lidar_reader.opponent_x, self.lidar_reader.opponent_y)

	def get_opponent_distance(self) :
		if self.robot == None : return None
		x, y = self.robot.get_position_x_y()
		return math.sqrt((x - self.lidar_reader.opponent_x)**2 + (y - self.lidar_reader.opponent_y)**2)

	def process_opponent_data(self) :
		
		distance = self.get_opponent_distance()
		if (distance == None) :
			logger.log_error("CanLidarNode", "Cannot obtain distance to opponent")
			return

		if distance < 2000 :
			if self.on_evitement != None :
				self.on_evitement()

