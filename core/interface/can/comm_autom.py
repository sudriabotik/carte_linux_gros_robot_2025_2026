"""
Contains functions allowing to send the correct action_id and arguments
at the correct address to control the card.
"""

import core.interface.can.canopen_wrapper as canopen_wrapper
import time

from core.interface.can.action_comm_node import CanActionNode, _CanActionNodeReader  # CLAUDE: Import listener class

# debut config pour les hint uniquement : 
from core.interface.can.canopen_wrapper import CanopenWrapper  # Type hint uniquement
# Pour l'autocomplétion dans l'IDE
canopen_wrapper.instance = CanopenWrapper(None)
# debut config pour les hint uniquement : 

# all the state enum from the C code

class CanAutomNode(CanActionNode) : 

	"""
	NOTE: Les méthodes commençant par "action_" déclenchent automatiquement un wait
	avant leur exécution (via AutoWaitWrapper dans FunctStrat).
	Cela évite les appels manuels wait_asserv()/wait_autom() dans le code stratégie.
	"""

	def __init__(self, bus, node_id : int):
		super().__init__(bus, node_id, _CanActionNodeReader)  # CLAUDE: Pass listener class to parent
	

	def action_homing(self, speed_v_percent: int = 13, speed_h_percent: int = 13) :
		"""
		CMD_HOMING (1): Performs the homing sequence (initialisation of motor positions using switches)

		:param speed_v_percent: Vertical homing speed (default 10)
		:param speed_h_percent: Horizontal homing speed (default 10)
		"""
		canopen_wrapper.instance.request_action(self.node_id, 1, [speed_v_percent, speed_h_percent])
		self.timestamp_last_command = time.time()
		

	def action_grab(self) :
		"""
		CMD_GRAB (2): Performs a grab sequence
		"""
		canopen_wrapper.instance.request_action(self.node_id, 2, [])
		self.timestamp_last_command = time.time()


	def action_pos_elevator_h(self, pos_mm : int) :
		"""
		sets the horizontal position of the elevator
		"""
		canopen_wrapper.instance.request_action(self.node_id, 4, [pos_mm])
		self.timestamp_last_command = time.time()


	def action_deposit(self) :
		"""
		CMD_DEPOSIT (3): Performs a deposit sequence
		"""
		canopen_wrapper.instance.request_action(self.node_id, 3, [])
		self.timestamp_last_command = time.time()


	def action_pos_elevator_v(self, pos_mm : int) :
		"""
		CMD_POS_ELAVATOR_V (5): Sets the vertical position of the elevator

		:param pos_mm: Position in millimeters
		"""
		canopen_wrapper.instance.request_action(self.node_id, 5, [pos_mm])
		self.timestamp_last_command = time.time()


	def action_pos_ax(self, id_ax: int, pos_ax: int) :
		"""
		CMD_POS_AX (6): Sets the position of an AX servo motor

		:param id_ax: AX servo motor ID
		:param pos_ax: Target position for the AX servo
		"""
		canopen_wrapper.instance.request_action(self.node_id, 6, [id_ax, pos_ax])
		self.timestamp_last_command = time.time()


	def action_pump_on_off(self, on_off: bool) :
		"""
		CMD_POMP_ON_OFF (7): Turns the pumps (3 and 4) on or off

		:param on_off: True to turn on, False to turn off
		"""
		canopen_wrapper.instance.request_action(self.node_id, 7, [1 if on_off else 0])
		self.timestamp_last_command = time.time()


	def action_open_pince(self) :
		"""
		CMD_OPEN_PINCE (8): Opens the gripper (pince)
		"""
		canopen_wrapper.instance.request_action(self.node_id, 8, [])
		self.timestamp_last_command = time.time()


	def action_ejecter(self, num_element: int) :
		"""
		CMD_EJECTER (9): Ejects a specified number of elements

		:param num_element: Number of elements to eject
		"""
		canopen_wrapper.instance.request_action(self.node_id, 9, [num_element])
		self.timestamp_last_command = time.time()


	def action_i2c_servo(self, channel: int, position: int) :
		"""
		CMD_I2C_SERVO_MOTEUR (10): Controls an I2C servo motor

		:param channel: I2C servo channel
		:param position: Target position (typically between 500 and 2500)
		"""
		canopen_wrapper.instance.request_action(self.node_id, 10, [channel, position])
		self.timestamp_last_command = time.time()


	def action_close_pince(self) :
		"""
		CDM_CLOSE_PINCE (11): Closes the gripper (pince)
		"""
		canopen_wrapper.instance.request_action(self.node_id, 11, [])
		self.timestamp_last_command = time.time()


	def action_ready_to_grap(self) :
		"""
		CDM_READY_TO_GRAP (12): Moves to ready-to-grab position
		"""
		canopen_wrapper.instance.request_action(self.node_id, 12, [])
		self.timestamp_last_command = time.time()


	def action_safe_position_ascenseur(self) :
		"""
		CDM_SAFE_POSITION_ASCENSEUR (13): Moves elevator to safe position
		"""
		canopen_wrapper.instance.request_action(self.node_id, 13, [])
		self.timestamp_last_command = time.time()

	def action_couleur_equipe(self, couleur_equipe ):
		"""
		CMD_COULEUR_EQUIPE (14)
		"""
		canopen_wrapper.instance.request_action(self.node_id, 14, [couleur_equipe])
		self.timestamp_last_command = time.time()

	def action_fermer_porte_rentrer_ax_caca(self):
		"""
		CMD_FERMER_PORTE_RENTRER_AX_CACA(15)
		"""
		canopen_wrapper.instance.request_action(self.node_id, 15, [])
		self.timestamp_last_command = time.time()

	def action_pos_vitesse_ax(self, id, position, vitesse):
		"""
		CMD_POS_VITESSE_AX (16)
		param position : 0.29 [°]/unité maximum 1023-->(300 degrés)
		param vitess : 0.111 rpm / unité  
		ax12 max rpm = 59 --> maximum = 59/0.111 = 531 
		"""
		canopen_wrapper.instance.request_action(self.node_id, 16, [id, position, vitesse])
		self.timestamp_last_command = time.time()

	def action_pos_ax_caca_calage(self) :
		"""
		CMD_POS_AX_CACA_CALAGE (17): il ne faut pas que l'ax soit en position ejecter avant de faire un calage
		sinon le robott va se caler sur l'ax.
		"""
		canopen_wrapper.instance.request_action(self.node_id, 17, [])
		self.timestamp_last_command = time.time()

	def action_open_cursor(self):  # CLAUDE
		"""
		CMD_AX_CURSOR_OUVERT (18): Ouvre le curseur/pince
		"""
		canopen_wrapper.instance.request_action(self.node_id, 18, [])
		self.timestamp_last_command = time.time()

	def action_close_cursor(self):  # CLAUDE
		"""
		CMD_AX_CURSOR_FERMER (19): Ferme le curseur/pince
		"""
		canopen_wrapper.instance.request_action(self.node_id, 19, [])
		self.timestamp_last_command = time.time()

	def action_open_cursor_2(self):
		"""
		CMD_OPEN_CURSOR_2 (21): Ouvre le curseur/pince 2
		"""
		canopen_wrapper.instance.request_action(self.node_id, 21, [])
		self.timestamp_last_command = time.time()

	def action_close_cursor_2(self):
		"""
		CMD_CLOSE_CURSOR_2 (22): Ferme le curseur/pince 2
		"""
		canopen_wrapper.instance.request_action(self.node_id, 22, [])
		self.timestamp_last_command = time.time()

	def action_grab_pince(self):
		"""
		CMD_AX_GRAB_PINCE (20)
		"""
		canopen_wrapper.instance.request_action(self.node_id, 20, [])
		self.timestamp_last_command = time.time()

	def action_start_match(self):
		"""
		CMD_START_MATCH (23): Démarre le chronomètre du match

		Enregistre le tick de départ du match côté STM32 pour le timing interne.
		Utilisé pour synchroniser les actions temporisées.
		"""
		canopen_wrapper.instance.request_action(self.node_id, 23, [])
		self.timestamp_last_command = time.time()

	def action_emergency_stop(self):
		"""
		CMD_EMERGENCY_STOP (99): Arrêt d'urgence du robot

		Stoppe immédiatement tous les mouvements et actions en cours.
		Fonction critique pour la sécurité.
		ATTENTION: Cette commande met le système en boucle infinie d'urgence.
		"""
		canopen_wrapper.instance.request_action(self.node_id, 99, [])
		self.timestamp_last_command = time.time()

