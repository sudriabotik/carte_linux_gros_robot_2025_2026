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

    #module_unified_logger.unified_logger.log_python("StratDynamique", "=== DÉBUT DU MATCH ===")
    logger.log_info("StratDynamique", "=== DÉBUT DU MATCH ===")
    asserv = self.funct.node_asserv
    autom  = self.funct.node_autom
    wait_a = self.funct.wait_asserv
    wait_m = self.funct.wait_autom

        # 1. ATTENTE DÉPART
    # ======================
    couleur = self.funct.wait_and_read_team_color()
    
    self.funct.wait_autom()
    self.funct.node_autom.action_couleur_equipe(couleur)
    self.funct.wait_autom()
    self.funct.node_autom.action_close_pince()
    self.funct.wait_autom()
    # ======================
    # 2. CALAGE DE DÉPART
    # ======================

    self.funct.calage_depart(couleur)

    self.funct.wait_debut_match()

    self.funct.node_asserv.action_evitement_on_off(True)
    self.funct.wait_asserv()


# ── 1. Aller à t1_a puis catch tas_1 ──
    wait_a()
    asserv.action_goto_xy(175, 1600, comm_asserv.Face.FACE_AVANT)
    wait_a()

    asserv.action_lookat(175, 1200, comm_asserv.Face.FACE_AVANT)
    wait_a()
    autom.action_open_pince()
    wait_m()
    asserv.action_goto_xy(175, 1200, comm_asserv.Face.FACE_AVANT)
    wait_a()
    autom.action_grab()
    wait_m()
    autom.action_deposit()
    wait_m()

    # ── 2. Déposer en d3 : d3_a(175,1000) → centre d3(100,800) → d3_b(175,600) ──
    # Robot à (175, 1200), passer par d3_a, éjecter à partir du centre, sortir par d3_b
    asserv.action_goto_xy(175, 1000, comm_asserv.Face.FACE_AVANT)  # d3_a (passage)
    wait_a()
    asserv.action_goto_xy(175, 800, comm_asserv.Face.FACE_AVANT)  # centre d3 (y=800)
    wait_a()
    autom.action_open_pince()
    wait_m()
    # Éjecter 1 par 1, avancer 50mm vers d3_b (y décroissant)
    # y = 800 → 750 → 700 → 650
    for i in range(4):
        autom.action_ejecter(1)
        wait_m()
        if i < 3:
            asserv.action_translation(50, 10, 10)
            wait_a()
    # Aller au point d'approche opposé d3_b
    asserv.action_goto_xy(175, 600, comm_asserv.Face.FACE_AVANT)  # d3_b
    wait_a()

    # ── 3. Catch tas_5 : robot à ~(175, 660), descendre vers tas_5 (175, 400) ──
    asserv.action_lookat(175, 400, comm_asserv.Face.FACE_AVANT)
    wait_a()
    autom.action_open_pince()
    wait_m()
    asserv.action_goto_xy(175, 400, comm_asserv.Face.FACE_AVANT)
    wait_a()
    autom.action_grab()
    wait_m()
    autom.action_deposit()
    wait_m()

    # ── 4. Reculer à d3_b (175, 600) puis recalage X négatif face arrière ──
    # Robot à (175, 400), reculer assez loin du mur pour le recalage
    asserv.action_goto_xy(200, 550, comm_asserv.Face.FACE_AVANT)
    wait_a()

    # Recalage X négatif (mur gauche à x=0), face arrière
    asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_X, comm_asserv.Face.FACE_ARRIERE)
    wait_a()
    asserv.action_translation(-60, 10, 10)  # s'éloigner du mur
    wait_a()

    # ── 5. Déposer en d4 : d4_d(600,800) → centre d4(800,800) → d4_c(1000,800) ──
    # Passer par d4_d, éjecter à partir du centre, sortir par d4_c
    asserv.action_goto_xy(600, 800, comm_asserv.Face.FACE_AVANT)  # d4_d (passage)
    wait_a()
    asserv.action_goto_xy(800, 800, comm_asserv.Face.FACE_AVANT)  # centre d4
    wait_a()
    autom.action_open_pince()
    wait_m()
    # Éjecter 1 par 1 en avançant de 50mm vers d4_c (x croissant)
    # x = 800 → 850 → 900 → 950
    for i in range(4):
        autom.action_ejecter(1)
        wait_m()
        if i < 3:
            asserv.action_translation(50, 10, 10)
            wait_a()
    # Aller au point d'approche opposé d4_c
    asserv.action_goto_xy(1000, 800, comm_asserv.Face.FACE_AVANT)  # d4_c
    wait_a()

    
    asserv.action_lookat(1150, 800, comm_asserv.Face.FACE_AVANT)
    wait_a()
    autom.action_open_pince()
    wait_m()
    asserv.action_goto_xy(1150, 800, comm_asserv.Face.FACE_AVANT)  # centre tas_3
    wait_a()
    autom.action_grab()
    wait_m()
    autom.action_deposit()
    wait_m()

    # ── 7. Déposer en d5 : d5_d(1300,800) → centre d5(1500,800) → d5_c(1700,800) ──
    # Passer par d5_d (plus proche), éjecter à partir du centre, sortir par d5_c
    asserv.action_goto_xy(1300, 800, comm_asserv.Face.FACE_AVANT)  # d5_d (passage)
    wait_a()
    asserv.action_goto_xy(1500, 800, comm_asserv.Face.FACE_AVANT)  # centre d5
    wait_a()
    autom.action_open_pince()
    wait_m()
    # Éjecter 1 par 1 en avançant de 50mm vers d5_c (x croissant)
    # x = 1500 → 1550 → 1600 → 1650
    for i in range(4):
        autom.action_ejecter(1)
        wait_m()
        if i < 3:
            asserv.action_translation(50, 10, 10)
            wait_a()
    # Aller au point d'approche opposé d5_c
    asserv.action_goto_xy(1700, 800, comm_asserv.Face.FACE_AVANT)  # d5_c
    wait_a()

    # ── 8. Retour zone départ via P5 (1500, 1150) ──
    # Robot à ~(1700, 800), remonter via P5 puis retour zone jaune
    autom.action_close_pince()  # claude diane — fermer les pinces pour le retour
    asserv.action_goto_xy(1500, 1150, comm_asserv.Face.FACE_AVANT)  # P5
    wait_a()
    wait_m()
    asserv.action_goto_xy(self.position_depart[0], self.position_depart[1], comm_asserv.Face.FACE_AVANT)
    wait_a()