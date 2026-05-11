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
    logger.set_time_origin()

    self.funct.node_asserv.action_evitement_on_off(True)
    self.funct.wait_asserv()


    # ── 1. Aller à t1_a puis catch tas_1 ──
    wait_a()
    asserv.action_goto_xy(175, 1600, comm_asserv.Face.FACE_AVANT)
    wait_a()

    # lookat centre tas_1, ouvrir pinces, avancer, grab, deposit
    asserv.action_lookat(175, 1200, comm_asserv.Face.FACE_AVANT)
    wait_a()
    autom.action_open_pince()
    wait_m()
    asserv.action_goto_xy(175, 1200, comm_asserv.Face.FACE_AVANT)
    wait_a()
    autom.action_grab()
    wait_m()
    autom.action_deposit()

    # ── 2. Déposer en d3 : se placer à 240mm au-dessus de d3_b, éjecter 4× en avançant de 60mm ──
    # d3_b = (175, 600), donc départ y = 600 + 240 = 840
    # Le robot est à (175, 1200), orienté vers y négatif → descendre
    wait_m()
    asserv.action_goto_xy(175, 860, comm_asserv.Face.FACE_AVANT)
    wait_a()

    # Ouvrir les pinces avant de déposer
    #autom.action_open_pince()
    #wait_m()

    # Éjecter 1 élément, avancer 60mm, 4 fois
    # y = 840 → 780 → 720 → 660
    for i in range(4):
        autom.action_ejecter(1)
        wait_m()
        if i < 3:  # pas d'avance après le dernier
            asserv.action_translation(55, 10, 10)  # -60 car le robot avance vers y négatif
            wait_a()

    # Robot est maintenant à environ (175, 660), proche de d3_b (175, 600)

    # ── 3. Catch tas_5 : continuer vers le bas, pinces ouvertes, attraper ──
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
    autom.action_close_pince()
    wait_m()

    # ── 4. Recalage : face avant vers y négatif, puis x négatif ──
    # Recalage Y négatif (mur bas à y=0), face avant
    asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_Y, comm_asserv.Face.FACE_AVANT)
    wait_a()
    asserv.action_translation(-80, 10, 10)  # s'éloigner du mur
    wait_a()

    # Recalage X négatif (mur gauche à x=0), face avant
    asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_X, comm_asserv.Face.FACE_ARRIERE)
    wait_a()
    asserv.action_translation(60, 10, 10)  # s'éloigner du mur
    wait_a()

    # ── 5. Déposer en d8 : se placer à 240mm avant d8_b, ouvrir pinces, éjecter ──
    # d8_b = (500, 175), le robot arrive par la gauche
    # Se placer à x = 500 - 240 = 260, y = 175
    asserv.action_goto_xy(260, 175, comm_asserv.Face.FACE_AVANT)
    wait_a()


    logger.log_info("StratDynamique", f"Position finale du robot: {self.robot}")

    # ======================
    # 4. FIN DU MATCH
    # ======================
    logger.log_info("StratDynamique", "=== FIN DU MATCH ===")