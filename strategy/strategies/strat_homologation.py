"""Stratégie d'homologation"""
from core.interface.can import comm_asserv, comm_autom
from core.interface.log_management import logger

# Type hints pour l'autocomplétion IDE
from core.interface.can.comm_asserv import CanAsservNode
from core.interface.can.comm_autom import CanAutomNode
from core.robot.function_strat import FunctStrat
from core.robot.robot import Robot

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
    
    # ======================
    # 3. PARCOURS HOMOLOGATION
    # ======================
    asserv.action_set_linear_speed_accel(0.4,0.5)
    asserv.action_translation(300)
    asserv.action_goto_xy(700,800,comm_asserv.Face.FACE_AVANT)
    asserv.action_goto_xy(1400,800,comm_asserv.Face.FACE_AVANT)
    """ 
    asserv.action_goto_xy(175, 1500, comm_asserv.Face.FACE_AVANT)
    asserv.action_goto_xy(175, 900, comm_asserv.Face.FACE_AVANT)
    asserv.action_goto_xy(175, 1300, comm_asserv.Face.FACE_ARRIERE)
    asserv.action_goto_xy(900, 800, comm_asserv.Face.FACE_AVANT)
    asserv.action_goto_xy(1350, 800, comm_asserv.Face.FACE_AVANT)
    """
    logger.log_info("Strat_homologation", f"Position finale du robot: {robot_state}")
    logger.log_info("Strat_homologation", "=== FIN DU MATCH ===")