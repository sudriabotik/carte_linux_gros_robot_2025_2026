
from core.interface.can import comm_asserv, comm_autom
from core.interface.log_management import logger

# Type hints pour l'autocomplétion IDE
from core.interface.can.comm_asserv import CanAsservNode
from core.interface.can.comm_autom import CanAutomNode
from core.robot.function_strat import FunctStrat
from core.robot.robot import Robot

from strategy.parallel_executor import ParallelExecutor

def run(funct:FunctStrat , robot_state:Robot ):
    logger.log_info("strat_final"," debut execution fonction run fichier strat_final")

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
    asserv.action_set_linear_speed_accel(0.7,0.8)
    couleur = funct.wait_and_read_team_color()
    
    # ======================
    # 2. CALAGE DE DÉPART
    # ======================
    funct.calage_depart(couleur)
    #asserv.set_couleur(couleur) # il faut que la couleur soit et aprés le callage pour l'asserv. 
    autom.action_couleur_equipe(couleur)
    asserv.action_lookat(450,800,comm_asserv.Face.FACE_ARRIERE)
    funct.wait_debut_match()
    asserv.action_set_linear_speed_accel(0.8,1.2)
    logger.set_time_origin()

    asserv.action_evitement_on_off(True)
    
    #asserv.action_translation(-255) # pour sortie du nids 

    #autom.action_ready_to_grap()
    asserv.action_goto_xy(450,800,comm_asserv.Face.FACE_ARRIERE)
    parallel_autom(
        lambda: autom.action_ready_to_grap(),
        lambda: autom.action_open_pince(),
    )
    #asserv.action_goto_xy(700,800,comm_asserv.Face.FACE_AVANT)
    #autom.action_open_pince()
    asserv.action_orientation(0)
    
    #attrape tas 3
    asserv.action_goto_xy(1150,800,comm_asserv.Face.FACE_AVANT,90,60)
    #funct.node_autom.enable_auto_wait()
    funct.wait_asserv()
    autom.action_grab()
    funct.wait_autom()
    
    parallel_autom(
        lambda: autom.action_deposit(),
        lambda: autom.action_safe_position_ascenseur(),
        lambda: autom.action_fermer_porte_rentrer_ax_caca()
    )

    asserv.action_goto_xy(1500,250,comm_asserv.Face.FACE_ARRIERE)

    asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_Y,comm_asserv.Face.FACE_ARRIERE)
    asserv.action_goto_xy(0,200)
    asserv.action_goto_xy(2050,200,comm_asserv.Face.FACE_ARRIERE) # pousse tas pour fair chier advs

    wait_parallel_autom()
    funct.open_cursor()
    autom.action_open_pince()
    x = funct.get_pos_cursor_x()
    asserv.action_goto_xy(x + 100,200,comm_asserv.Face.FACE_AVANT,50,65)
    funct.ejecter_rouler_x(1600,2)
    autom.action_fermer_porte_rentrer_ax_caca()
    funct.wait_asserv()
    asserv.action_orientation(180)
    autom.action_grab_pince()
    asserv.action_goto_xy(x,200,comm_asserv.Face.FACE_AVANT,60,65)
    funct.close_cursor()

    autom.action_grab()
    funct.wait_autom() #peut-etre rajouter wait. 
    autom.action_deposit() # trop long en temps 3 s et il reste encore 2 élement
    funct.wait_autom()

    asserv.action_orientation(160)
    asserv.action_translation(70)

    #asserv.action_goto_xy(600,300)
    asserv.action_orientation(90)
    funct.wait_asserv()
    autom.action_ejecter(1)
    funct.wait_autom()
    asserv.action_translation(60)
    funct.wait_asserv()
    autom.action_ejecter(1)
    funct.wait_autom()
    asserv.action_translation(100)

    autom.action_deposit()

    asserv.action_goto_xy(200,800,comm_asserv.Face.FACE_ARRIERE,100,80)
    asserv.action_orientation(-90)
    autom.action_open_pince()
    asserv.action_goto_xy(0,400,comm_asserv.Face.FACE_AVANT,70,50)
    autom.action_grab()
    autom.action_deposit()
    asserv.action_goto_xy(200,800,comm_asserv.Face.FACE_AVANT, 40,40)
    autom.action_pos_ax_caca_calage()
    asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_X,comm_asserv.Face.FACE_ARRIERE)

    # on commence à faire le tour du terrain. 
    asserv.action_set_linear_speed_accel(0.6,0.8)
    autom.action_fermer_porte_rentrer_ax_caca()
    funct.wait_autom()
    asserv.action_goto_xy(1725,800,comm_asserv.Face.FACE_AVANT,70,70)
    funct.ejecter_rouler_x(825,1)
    funct.ejecter_rouler_x(1525,1)
    autom.action_fermer_porte_rentrer_ax_caca()
    asserv.action_goto_xy(2000,200)
    asserv.action_goto_xy(2350,200)
    autom.action_ejecter(1)

    funct.wait_autom()
    asserv.action_goto_xy(2550,200)
    #funct.ejecter_rouler_x(2350,1)
    autom.action_pos_ax_caca_calage()
    asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_Y,comm_asserv.Face.FACE_ARRIERE)
    asserv.action_translation(100)
    asserv.action_goto_xy(2800,500)
    asserv.action_goto_xy(2800,900)
    funct.ejecter_rouler_y(850,1)
    asserv.action_goto_xy(2500,1350)


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
    asserv.action_translation(150)
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
    asserv.action_translation(60)
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
    asserv.action_evitement_on_off(False)

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
    asserv.action_goto_xy(200,870)

    funct.wait_asserv()
    autom.action_ejecter(1)
    funct.wait_autom()
    asserv.action_translation(50)
    funct.wait_asserv()
    autom.action_ejecter(1)
    funct.wait_autom()
    asserv.action_translation(50)
    funct.wait_asserv()
    autom.action_ejecter(1)
    funct.wait_autom()
    asserv.action_translation(50)
    funct.wait_asserv()
    autom.action_ejecter(1)

    asserv.action_orientation(90)
    autom.action_grab_pince()
    autom.action_pos_ax_caca_calage()
    autom.action_safe_position_ascenseur()

    funct.wait_time_match(97)
    asserv.action_goto_xy(200,1720,comm_asserv.Face.FACE_AVANT,90,90)
    autom.action_open_pince()

     """
    






    




