from typing import Union

import canopen

import logger
import comm_autom
import comm_asserv


class Resources :
	"""
	Class that contains all kind of handles to peripherals/functions
	"""

	def __init__(self):
		
		self._network : Union[None, canopen.Network]
		self._node_autom : Union[None, comm_autom.CanAutomNode]
		self._node_asserv : Union[None, comm_asserv.CanAsservNode]
	
	
	def NETWORK(self) :
		if not self._network_ok() : self._network_repair()
		return self._network

	
	def NODE_AUTOM(self) :
		if not self._node_autom_ok() : self._node_autom_repair()
		return self._node_autom

	
	def NODE_ASSERV(self) :
		if not self._node_asserv_ok() : self._node_asserv_repair()
		return self._node_asserv



	def init_all(self) :

		self._network_init()
		self._node_autom_init()
	

	def _network_init(self) :

		try :
			self._network = canopen.Network()
			self._network.connect(interface="socketcan", channel="can0", bitrate=500000)
		except :
			pass
	
	def _network_ok(self) :

		return self._network != None
	
	def _network_repair(self) :

		try :
			self._network.disconnect()
		except :
			pass

		try :
			self._network.connect(interface="socketcan", channel="can0", bitrate=500000)
		except :
			pass
	


	def _node_autom_init(self) :

		try :
			self.node_autom = comm_autom.CanAutomNode(self.NETWORK, 2, "./canopen_od/autom.eds")
		except Exception as e :
			logger.log_error("Main", f"cannot create autom node, {e}")
	
	def _node_autom_ok(self) :

		return self._node_autom != None
	
	def _node_autom_repair(self) :

		pass
	


	def _node_asserv_init(self) :

		try :
			self.node_autom = comm_asserv.CanAsservNode(self.NETWORK, 1, "./canopen_od/autom.eds")
		except Exception as e :
			logger.log_error("Main", f"cannot create asserv node, {e}")
	
	def _node_asserv_ok(self) :

		return self._node_asserv != None
	
	def _node_asserv_repair(self) :

		pass