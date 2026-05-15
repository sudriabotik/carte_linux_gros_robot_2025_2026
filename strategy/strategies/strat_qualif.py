"""Stratégie d'homologation"""
from core.interface.can import comm_asserv, comm_autom
from core.interface.log_management import logger

# Type hints pour l'autocomplétion IDE
from core.interface.can.comm_asserv import CanAsservNode
from core.interface.can.comm_autom import CanAutomNode
from core.robot.function_strat import FunctStrat
from core.robot.robot import Robot

from strategy.parallel_executor import ParallelExecutor

def run(funct:FunctStrat , robot_state:Robot ):
    logger.log_info("strat_qualif"," debut execution fonction run fichier strat_qualif")
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
    autom.action_close_pince()
    asserv.action_set_linear_speed_accel(0.7,0.9)
    couleur = funct.wait_and_read_team_color()
    
    # ======================
    # 2. CALAGE DE DÉPART
    # ======================
    funct.calage_depart(couleur)
    #asserv.set_couleur(couleur) # il faut que la couleur soit et aprés le callage pour l'asserv. 
    autom.action_couleur_equipe(couleur)

    funct.wait_debut_match()
    logger.set_time_origin()

    asserv.action_evitement_on_off(True)
    
    #asserv.action_translation(-255) # pour sortie du nids 
    #funct.node_autom.disable_auto_wait()
    asserv.action_goto_xy(0,1450,comm_asserv.Face.FACE_ARRIERE)
    autom.action_ready_to_grap()
    asserv.action_goto_xy(700,800,comm_asserv.Face.FACE_ARRIERE)
    asserv.action_orientation(0)
    autom.action_open_pince()

    #attrape tas 3
    asserv.action_goto_xy(1150,800,comm_asserv.Face.FACE_AVANT,70,40)
    #funct.node_autom.enable_auto_wait()
    funct.wait_asserv()
    autom.action_grab()
    funct.wait_autom()
    autom.action_deposit()
    """ 
    asserv.action_goto_xy(1650,1300,comm_asserv.Face.FACE_ARRIERE)
    funct.wait_autom()
    autom.action_ejecter(1) #depose zone 2
    funct.wait_autom()
    asserv.action_translation(60)
    funct.wait_asserv()
    autom.action_ejecter(1)
    autom.action_fermer_porte_rentrer_ax_caca()
    asserv.action_translation(60)
    """
    asserv.action_goto_xy(1500,650)
    asserv.action_orientation(-90)
    funct.wait_asserv()
    autom.action_ejecter(1)
    funct.wait_autom()
    asserv.action_translation(60)
    funct.wait_asserv()
    autom.action_ejecter(1)
    funct.wait_autom()
    asserv.action_translation(60)

    asserv.action_goto_xy(1500,400)
    autom.action_pos_ax_caca_calage()
    autom.action_safe_position_ascenseur()
    asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_Y, comm_asserv.Face.FACE_ARRIERE)
    #asserv.action_goto_xy(1500,200)
    asserv.action_translation(52) #200 - 147.5
    asserv.action_orientation(180)
    #autom.action_open_cursor()
    funct.wait_asserv()
    funct.open_cursor()
    autom.action_open_pince()
    asserv.action_translation(150)

    #ejecte 
    autom.action_ejecter(1)
    funct.wait_autom()
    asserv.action_translation(60)
    funct.wait_asserv()
    autom.action_ejecter(1)
    funct.wait_autom()

    autom.action_ready_to_grap()
    asserv.action_goto_xy(1150,200,comm_asserv.Face.FACE_AVANT,80,50)
    funct.wait_autom()
    funct.wait_asserv()
    autom.action_grab_pince()
    funct.wait_autom()
    asserv.action_translation(150,40,20)
    funct.wait_asserv()
    autom.action_grab()
    autom.action_deposit()
    x_cursor = funct.get_pos_cursor_x()
    asserv.action_goto_xy(x_cursor,200)
    funct.wait_asserv()
    #autom.action_close_cursor()
    funct.close_cursor()
    funct.wait_autom()
    asserv.action_orientation(160)
    asserv.action_translation(70)

    #asserv.action_goto_xy(600,300)
    asserv.action_orientation(90)
    funct.wait_asserv()
    autom.action_ejecter(1)
    funct.wait_autom()
    asserv.action_translation(60,200,200)
    funct.wait_asserv()
    autom.action_ejecter(1)
    funct.wait_autom()
    asserv.action_translation(100)

    asserv.action_goto_xy(700,800,comm_asserv.Face.FACE_AVANT)
    asserv.action_orientation(180)

    funct.wait_asserv()
    autom.action_ejecter(1)
    funct.wait_autom()
    asserv.action_translation(60)
    funct.wait_asserv()
    autom.action_ejecter(1)
    autom.action_close_pince()

    autom.action_safe_position_ascenseur()
    asserv.action_goto_xy(200,800)
    asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_X, comm_asserv.Face.FACE_AVANT)
    asserv.action_translation(-85)
    asserv.action_orientation(-90)
    funct.wait_asserv()
    autom.action_open_pince()
    asserv.action_goto_xy(200,500,comm_asserv.Face.FACE_AVANT, 70,50)
    asserv.action_orientation(-90)
    funct.wait_asserv()
    #autom.action_grab_pince()
    asserv.action_translation(130)
    funct.wait_asserv()
    autom.action_grab()
    autom.action_deposit()
    asserv.action_orientation(-70)
    asserv.action_orientation(90)
    funct.wait_asserv()
    autom.action_open_pince()
    asserv.action_goto_xy(200,900)

    funct.wait_asserv()
    autom.action_ejecter(1)
    funct.wait_autom()
    asserv.action_translation(55)
    funct.wait_asserv()
    autom.action_ejecter(1)
    funct.wait_autom()
    asserv.action_translation(55)
    funct.wait_asserv()
    autom.action_ejecter(1)
    funct.wait_autom()
    asserv.action_translation(55)
    funct.wait_asserv()
    autom.action_ejecter(1)

    asserv.action_orientation(90)
    autom.action_pos_ax_caca_calage()
    autom.action_safe_position_ascenseur()


    funct.wait_time_match(97)
    asserv.action_goto_xy(200,1710)


    






    




