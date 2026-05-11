"""Stratégie de test automation"""
from core.interface.can import comm_asserv, comm_autom
from core.interface.log_management import logger

# Type hints pour l'autocomplétion IDE
from core.interface.can.comm_asserv import CanAsservNode
from core.interface.can.comm_autom import CanAutomNode
from core.robot.function_strat import FunctStrat
from core.robot.robot import Robot

def run(funct: FunctStrat, robot_state: Robot):
    """
    Exécute la stratégie de test automation
    
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


    # ── 1. Aller à t1_a puis catch tas_1 ──
    asserv.action_goto_xy(175, 1600, comm_asserv.Face.FACE_AVANT)

    # lookat centre tas_1, ouvrir pinces, avancer, grab, deposit
    asserv.action_lookat(175, 1200, comm_asserv.Face.FACE_AVANT)
    autom.action_open_pince()
    asserv.action_goto_xy(175, 1200, comm_asserv.Face.FACE_AVANT, 100, 20)
    autom.action_grab()
    autom.action_deposit()

    # ── 2. Déposer en d3 : se placer à 240mm au-dessus de d3_b, éjecter 4× en avançant de 60mm ──
    # d3_b = (175, 600), donc départ y = 600 + 240 = 840
    # Le robot est à (175, 1200), orienté vers y négatif → descendre
    autom.action_safe_position_ascenseur()
    autom.action_open_pince()
    asserv.action_goto_xy(175, 720, comm_asserv.Face.FACE_AVANT)

    # Éjecter 1 élément, avancer 60mm, 4 fois
    # y = 840 → 780 → 720 → 660
    for i in range(4):
        autom.action_ejecter(1)
        if i < 3:  # pas d'avance après le dernier
            asserv.action_translation(55, 50, 50)  # -60 car le robot avance vers y négatif

    # Robot est maintenant à environ (175, 660), proche de d3_b (175, 600)

    # ── 3. Catch tas_5 : continuer vers le bas, pinces ouvertes, attraper ──
    asserv.action_lookat(175, 400, comm_asserv.Face.FACE_AVANT)
    autom.action_open_pince()
    asserv.action_goto_xy(175, 400, comm_asserv.Face.FACE_AVANT, 100, 20)
    autom.action_grab()
    autom.action_deposit()
    autom.action_close_pince()
    autom.action_pos_ax_caca_calage()

    # ── 4. Recalage : face avant vers y négatif, puis x négatif ──
    # Recalage Y négatif (mur bas à y=0), face avant
    asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_Y, comm_asserv.Face.FACE_AVANT)
    asserv.action_translation(-80)  # s'éloigner du mur

    # Recalage X négatif (mur gauche à x=0), face avant
    asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_X, comm_asserv.Face.FACE_ARRIERE)
    asserv.action_translation(60)  # s'éloigner du mur

    # ── 5. Déposer en d8 : se placer à 240mm avant d8_b, ouvrir pinces, éjecter ──
    # d8_b = (500, 175), le robot arrive par la gauche
    # Se placer à x = 500 - 240 = 260, y = 175
    asserv.action_goto_xy(500, 175, comm_asserv.Face.FACE_AVANT)
    asserv.action_goto_xy(780, 175, comm_asserv.Face.FACE_AVANT)
    
    for i in range(4):
        autom.action_ejecter(1)
        if i < 3:  # pas d'avance après le dernier
            asserv.action_translation(55, 20, 20)

    asserv.action_goto_xy(1000, 1000, comm_asserv.Face.FACE_AVANT)
    asserv.action_orientation(0)

    logger.log_info("StratDynamique", f"Position finale du robot: {robot_state}")

    # ======================
    # 4. FIN DU MATCH
    # ======================
    logger.log_info("StratDynamique", "=== FIN DU MATCH ===")