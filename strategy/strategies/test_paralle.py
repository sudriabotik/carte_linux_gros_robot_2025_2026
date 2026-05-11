"""Stratégie d'homologation"""
from core.interface.can import comm_asserv, comm_autom
from core.interface.log_management import logger

# Type hints pour l'autocomplétion IDE
from core.interface.can.comm_asserv import CanAsservNode
from core.interface.can.comm_autom import CanAutomNode
from core.robot.function_strat import FunctStrat
from core.robot.robot import Robot

from strategy.parallel_executor import ParallelExecutor

def run(funct, robot_state):
    """
    Exécute la stratégie d'homologation
    
    Args:
        funct: Instance de FunctStrat
        robot_state: Instance de Robot
    """
    # Raccourcis pour simplifier l'écriture
    asserv: CanAsservNode = funct.node_asserv
    autom: CanAutomNode = funct.node_autom
    
    parallel = ParallelExecutor(autom, asserv)

    # Créer des raccourcis pour simplifier l'écriture
    parallel_autom = parallel.parallel_autom
    wait_parallel_autom = parallel.wait_parallel_autom
    
    # ======================
    # 1. ATTENTE DÉPART
    # ======================
    funct.wait_heartbeat_all_node()
    autom.action_homing()

    couleur = funct.wait_and_read_team_color()
    
    autom.action_couleur_equipe(couleur)
    autom.action_close_pince()
    
    # ======================
    # 2. CALAGE DE DÉPART
    # ======================
    funct.calage_depart(couleur)

    funct.wait_debut_match()
    logger.set_time_origin()

    asserv.action_evitement_on_off(True)
    
    parallel_autom(
        lambda: autom.action_open_pince(),
        lambda: autom.action_grab(),
        lambda: autom.action_deposit(),
        lambda: autom.action_ready_to_grap(),
        lambda: autom.action_deposit(),
        lambda: autom.action_close_pince()
    )

    asserv.action_goto_xy(400,1000)
    asserv.action_goto_xy(1000,1300)
    wait_parallel_autom()
    asserv.action_goto_xy(2000,600)
    asserv.action_goto_xy(500,600)
    asserv.action_orientation(0)


