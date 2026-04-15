"""
Initialisation globale du robot (interfaces + état robot + connexions)

Ce fichier fait l'interface entre les différentes classes des sous-dossiers
et orchestre l'initialisation complète du robot.
"""
from dataclasses import dataclass
from core.interface.init_interface import initialize_interfaces
from core.robot.robot import Robot
from core.robot.function_strat import FunctStrat
from core.interface.log_management import logger
import time

@dataclass
class RobotContext:
	"""
	Regroupe TOUT ce dont le robot a besoin pour fonctionner
	"""
	# Interfaces hardware
	bus: any
	node_asserv: any
	node_autom: any
	read_gpio_tirette: callable
	read_gpio_couleur: callable

	# État du robot
	robot_state: Robot

	# Stratégie de jeu
	strat: FunctStrat

def initialize_all() -> RobotContext:
	"""
	Initialise TOUT le robot : interfaces + état + connexions

	Cette fonction orchestre l'initialisation complète :
	1. Initialise les interfaces (CAN, GPIO, logs)
	2. Crée l'objet Robot qui stocke l'état
	3. Fait les injections de dépendances (connecte les modules)

	Returns:
		RobotContext: Tout le contexte du robot initialisé et prêt à être utilisé
	"""
	# 1. Initialiser toutes les interfaces hardware
	logger.log_info("Core", "Initializing all hardware interfaces...")
	interfaces = initialize_interfaces()

	# 2. Créer l'état du robot
	robot_state = Robot(interfaces.node_asserv, interfaces.node_autom)
	logger.log_info("Core", f"Robot state initialized: {robot_state}")

	# 3. INJECTION DE DÉPENDANCES : Connecter les nodes au robot
	# Cela permet aux nodes de mettre à jour automatiquement la position du robot
	if interfaces.node_asserv:
		interfaces.node_asserv.can_reader.robot = robot_state
		logger.log_info("Core", "Robot position tracking enabled via TPDO[1] from asserv node")

	if interfaces.node_autom:
		interfaces.node_autom.can_reader.robot = robot_state
		logger.log_info("Core", "Autom node connected to robot state")
	
	if interfaces.node_lidar:
		interfaces.node_lidar.robot = robot_state
		logger.log_info("Core", "Lidar node connected to robot state")

		def on_evitement() :
			interfaces.node_asserv.action_evitement()
		interfaces.node_lidar.on_evitement = on_evitement

	# 4. Créer la stratégie de jeu
	strat = FunctStrat(
		node_autom=interfaces.node_autom,
		node_asserv=interfaces.node_asserv,
		robot_state=robot_state
	)
	logger.log_info("Core", f"Strategy initialized: {strat}")

	# 5. Petite pause pour s'assurer que tous les logs sont bien écrits
	time.sleep(0.200)

	# 6. Retourner tout le contexte
	return RobotContext(
		bus=interfaces.bus,
		node_asserv=interfaces.node_asserv,
		node_autom=interfaces.node_autom,
		read_gpio_tirette=interfaces.read_gpio_tirette,
		read_gpio_couleur=interfaces.read_gpio_couleur,
		robot_state=robot_state,
		strat=strat
	)
