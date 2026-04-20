"""
Moteur de stratégie dynamique
Prend les décisions en fonction de l'état du robot et exécute le match complet
"""

from core.interface.log_management import logger

from strategy.generate_path_V2 import generate_path
from strategy.coordonner_strat import TAS_COORDS
from core.interface.can import comm_autom  
from core.interface.can import comm_asserv
from core.interface.can.constants import *

from core.robot.function_strat import FunctStrat  # Type hint uniquement (pour Ctrl+Click IDE)
from core.robot.robot import Robot  # Type hint uniquement (pour Ctrl+Click IDE)



class StratDynamique:
    """
    Moteur de stratégie dynamique qui orchestre le déroulement complet du match
    """

    def __init__(self, funct_strat: FunctStrat, robot_state: Robot, robot_adv: tuple, available_tas: list):
        """
        Initialise le moteur de stratégie dynamique

        Args:
            funct_strat: Instance de FunctStrat (pour envoyer toutes les commandes au robot)
            robot_state: État du robot (position, couleur, vitesse, etc.)
            robot_adv: Position de l'adversaire (x, y)
            available_tas: Liste des tas disponibles (ex: ['tas_1', 'tas_2', ...])
        """
        self.funct = funct_strat
        self.robot = robot_state
        self.robot_adv = robot_adv
        self.available_tas = available_tas
        self.tas_attraper = []
        self.zone_depose_utiliser = []
        logger.log_info("StratDynamique", "Moteur de stratégie dynamique initialisé")


    def run_homologation(self):
        logger.log_info("Strat_homologation", "=== DÉBUT DU MATCH ===")

        # ======================
        # 1. ATTENTE DÉPART
        # ======================
        couleur = self.funct.wait_and_read_team_color()
        
        self.funct.wait_autom
        self.funct.node_autom.action_couleur_equipe(couleur)
        self.funct.wait_autom
        self.funct.node_autom.action_close_pince()
        self.funct.wait_autom
        # ======================
        # 2. CALAGE DE DÉPART
        # ======================

        self.funct.calage_depart(couleur)

        self.funct.wait_debut_match()

        self.funct.node_asserv.action_evitement_on_off(True)
        self.funct.wait_asserv()

        if (couleur == JAUNE):
            module_unified_logger.unified_logger.log_python("Strat_homologation", " COULEUR JAUNE")
            self.funct.wait_asserv()
            self.funct.node_asserv.action_goto_xy(175,1500, comm_asserv.Face.FACE_AVANT )

            self.funct.wait_asserv()
            self.funct.node_asserv.action_goto_xy(175,950, comm_asserv.Face.FACE_AVANT )

            self.funct.wait_asserv()
            self.funct.node_asserv.action_goto_xy(175,1200, comm_asserv.Face.FACE_ARRIERE )

            self.funct.wait_asserv()
            self.funct.node_asserv.action_goto_xy(1500,1200, comm_asserv.Face.FACE_AVANT )

            self.funct.wait_asserv()
            logger.log_info("Strat_homologation", f"Position finale du robot: {self.robot}")

        if (couleur == BLEU):
            module_unified_logger.unified_logger.log_python("Strat_homologation", " COULEUR BLEU")
            self.funct.wait_asserv()
            self.funct.node_asserv.action_goto_xy((3000-175),1500, comm_asserv.Face.FACE_AVANT )

            self.funct.wait_asserv()
            self.funct.node_asserv.action_goto_xy((3000-175),950, comm_asserv.Face.FACE_AVANT )

            self.funct.wait_asserv()
            self.funct.node_asserv.action_goto_xy((3000-175),1200, comm_asserv.Face.FACE_ARRIERE )

            self.funct.wait_asserv()
            self.funct.node_asserv.action_goto_xy(1500,1200, comm_asserv.Face.FACE_AVANT )

            self.funct.wait_asserv()
            logger.log_info("Strat_homologation", f"Position finale du robot: {self.robot}")

        module_unified_logger.unified_logger.log_python("Strat_homologation", "=== FIN DU MATCH ===")

    def run_strat(self):
        """
        Exécute TOUTE la stratégie du match
        """
        module_unified_logger.unified_logger.log_python("StratDynamique", "=== DÉBUT DU MATCH ===")

        asserv = self.funct.node_asserv
        autom  = self.funct.node_autom
        wait_a = self.funct.wait_asserv
        wait_m = self.funct.wait_autom

            # 1. ATTENTE DÉPART
        # ======================
        couleur = self.funct.wait_and_read_team_color()
        
        self.funct.wait_autom
        self.funct.node_autom.action_couleur_equipe(couleur)
        self.funct.wait_autom
        self.funct.node_autom.action_close_pince()
        self.funct.wait_autom
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
        asserv.action_goto_xy(175, 840, comm_asserv.Face.FACE_AVANT)
        wait_a()

        # Ouvrir les pinces avant de déposer
        autom.action_open_pince()
        wait_m()

        # Éjecter 1 élément, avancer 60mm, 4 fois
        # y = 840 → 780 → 720 → 660
        for i in range(4):
            autom.action_ejecter(1)
            wait_m()
            if i < 3:  # pas d'avance après le dernier
                asserv.action_translation(60, 10, 10)  # -60 car le robot avance vers y négatif
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
        autom.action_close_pince
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
        asserv.action_translation(-60, 10, 10)  # s'éloigner du mur
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

    def go_and_catch_tas(self, target_tas: str):
        '''
        Cette fonction regroupe la generation de trajectoire
        et l'action de l'autom pour attraper le tas

        Args:
            target_tas: Nom du tas à attraper (ex: 'tas_4')
        '''
        # 1. Générer le chemin vers le tas
        path = generate_path(
            self.robot.get_position_x_y(),  # Position actuelle du robot
            target_tas,                      # Tas cible
            self.robot_adv,                  # Position adversaire
            self.available_tas,               # Liste des tas disponibles
            self.tas_attraper,
        )

        logger.log_info("StratDynamique", f" path : {path}")

        # 2. Suivre le chemin généré (type_cible=1 pour catch)
        self.funct.follow_path(path, type_cible=1)

        # 3. Attraper le tas à sa position centrale
        self.tas_attraper.append(target_tas)
        centre_tas = TAS_COORDS[target_tas]
        self.funct.catch_tas(centre_tas)

    def go_and_caca(self,target_zone_depose,num_element_ejecter):

                # 1. Générer le chemin vers le tas
        path = generate_path(
            self.robot.get_position_x_y(),  # Position actuelle du robot
            target_zone_depose,                      # Tas cible
            self.robot_adv,                  # Position adversaire
            self.available_tas,               # Liste des tas disponibles
            self.tas_attraper
        )

        logger.log_info("StratDynamique", f" path : {path}")

        # 2. Suivre le chemin généré (type_cible=1 pour catch)
        self.funct.follow_path(path, type_cible=1)
        self.zone_depose_utiliser.append(target_zone_depose)
        
        # determiner les point cible pour les passer en parametre à la fonction 

        self.funct.depose_element_zone()




