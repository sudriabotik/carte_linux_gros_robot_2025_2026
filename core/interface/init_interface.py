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
from core.interface.log_management import unified_logger
from core.interface.gpio.gpio import init_gpio, read_gpio_couleur, read_gpio_tirette

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

    # Initialiser bus CAN
    logger.log_info("Init", "Attempting to connect to CAN bus...")
    bus = can.interface.Bus(bustype='slcan', channel='/dev/canable', bitrate=500000)
    logger.log_info("Init", "Connected to CAN network")

    # Configuration debug CAN
    canopen_wrapper.DEBUG_CAN_CHANGES_ONLY = DEBUG_CAN_CHANGES_ONLY

    # Démarrer le unified logger (UART + CAN)
    if DEBUG_UNIFIED_LOGGER:
        canopen_wrapper.unified_logger = unified_logger.UnifiedLogger(
            uart_port="/dev/ttyS2",
            uart_baudrate=1000000,
            log_dir="log"
        )
        canopen_wrapper.unified_logger.start()
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

    # Initialiser GPIO
    init_gpio()
    logger.log_info("Init", "GPIO initialized")

    # Retourner toutes les interfaces
    return InterfacesContext(
        bus=bus,
        node_autom=node_autom,
        node_asserv=node_asserv,
        read_gpio_tirette=read_gpio_tirette,
        read_gpio_couleur=read_gpio_couleur
    )
