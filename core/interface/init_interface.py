"""
Initialisation de toutes les interfaces hardware (CAN, GPIO, logs)
Ce fichier contient tout le code d'initialisation qui était dans main.py (lignes 1-70)
"""
from dataclasses import dataclass
import can
import can.interfaces.serial.serial_can
import can.interfaces.socketcan.socketcan
from core.interface.can import canopen_wrapper
from core.interface.can import comm_autom
from core.interface.can import comm_asserv
from core.interface.log_management import logger
import core.interface.log_management.unified_logger as module_unified_logger
from core.interface.gpio.gpio import read_gpio_couleur, read_gpio_tirette

import time
import subprocess

@dataclass
class InterfacesContext:
    """
    Regroupe toutes les interfaces hardware initialisées
    """
    bus: can.Bus
    node_autom: comm_autom.CanAutomNode
    node_asserv: comm_asserv.CanAsservNode
    read_gpio_tirette: callable
    read_gpio_couleur: callable


def wait_for_can0(timeout=10):
    """
    Attend que can0 soit UP et configuré
    
    :param timeout: Temps max d'attente en secondes
    :return: True si can0 est prêt, False sinon
    """
    logger.log_info("Init", "Waiting for can0 interface...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Vérifier si can0 existe et est UP
            result = subprocess.run(
                ['ip', 'link', 'show', 'can0'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                # can0 existe, vérifier si UP
                if 'state UP' in result.stdout or 'UP' in result.stdout:
                    logger.log_info("Init", "can0 is UP and ready")
                    return True
                else:
                    logger.log_info("Init", f"can0 exists but not UP yet, waiting...")
            
        except Exception as e:
            logger.log_warning("Init", f"can0 check failed: {e}")
        
        time.sleep(0.5)  # Attendre 500ms avant de réessayer
    
    logger.log_error("Init", f"can0 not ready after {timeout}s")
    return False

def initialize_interfaces() -> InterfacesContext:
    """
    Initialise toutes les interfaces hardware : CAN, GPIO, logs

    Cette fonction contient tout le code qui était dans les 70 premières lignes de main.py

    Returns:
        InterfacesContext: Toutes les interfaces initialisées
    """
    # Configuration debug
    DEBUG_CAN_CHANGES_ONLY = True
    DEBUG_UNIFIED_LOGGER = True

    # UART_ASSERV et UART_AUTOM can't be true at the same time.
    UART_ASSERV  =True
    UART_AUTOM = False

     # Attendre que can0 soit prêt AVANT de créer le bus
    if not wait_for_can0(timeout=10):
        raise RuntimeError("can0 interface not available - cannot start robot")


    # Initialiser bus CAN
    logger.log_info("Init", "Attempting to connect to CAN bus...")
    #avec le usb to can qui a le firmware canable on utilise  cette commande pour le bus : 
    # il y a un dev rule pour fixer le nom du port serie car le nom du port peut changer.
    #bus = can.interface.Bus(bustype='slcan', channel='/dev/canable', bitrate=500000)
    
    #avec le usb to can qui a le firmware PCAN on utilise cette commande pour le bus :
    # il y a une dev rule pour configurer et activer l'interace can0 à chaque branchement de usb to can. 
    bus = can.interface.Bus(
        interface='socketcan',
        channel='can0',
        bitrate=500000
    )
    logger.log_info("Init", "Connected to CAN network")

    # Configuration debug CAN
    canopen_wrapper.DEBUG_CAN_CHANGES_ONLY = DEBUG_CAN_CHANGES_ONLY

    # Démarrer le unified logger (UART + CAN)
    if DEBUG_UNIFIED_LOGGER:
        if (UART_AUTOM):
            module_unified_logger.unified_logger = module_unified_logger.UnifiedLogger(
                uart_port="/dev/ttyS6",
                uart_baudrate=1000000,
                log_dir="log"
            )
        else:
            module_unified_logger.unified_logger = module_unified_logger.UnifiedLogger(
                uart_port="/dev/ttyS2",
                uart_baudrate=1000000,
                log_dir="log"
            )

        module_unified_logger.unified_logger.start()
        logger.log_info("Init", "Unified logger (UART+CAN) started")

    # Créer le wrapper CANopen
    canopen_wrapper.instance = canopen_wrapper.CanopenWrapper(bus)

    # Créer les nodes CAN
    node_autom = None
    try:
        node_autom = comm_autom.CanAutomNode(bus, 2)
    except Exception as e:
        logger.log_error("Init", f"Cannot create autom node: {e}")

    node_asserv = None
    try:
        node_asserv = comm_asserv.CanAsservNode(bus, 1)
    except Exception as e:
        logger.log_error("Init", f"Cannot create asserv node: {e}")

    # GPIO prêt (aucune initialisation nécessaire avec gpiofind/gpioget)
    logger.log_info("Init", "GPIO ready")

    # Retourner toutes les interfaces
    return InterfacesContext(
        bus=bus,
        node_autom=node_autom,
        node_asserv=node_asserv,
        read_gpio_tirette=read_gpio_tirette,
        read_gpio_couleur=read_gpio_couleur
    )
