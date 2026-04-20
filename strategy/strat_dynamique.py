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

        module_unified_logger.unified_logger.log_python("Strat_homologation", " COULEUR JAUNE")
        self.funct.wait_asserv()
        self.funct.node_asserv.action_goto_xy(175,1500, comm_asserv.Face.FACE_AVANT )

        self.funct.wait_asserv()
        self.funct.node_asserv.action_goto_xy(175,900, comm_asserv.Face.FACE_AVANT )

        self.funct.wait_asserv()
        self.funct.node_asserv.action_goto_xy(175,1300, comm_asserv.Face.FACE_ARRIERE )

        self.funct.wait_asserv()
        self.funct.node_asserv.action_goto_xy(900,800, comm_asserv.Face.FACE_AVANT )

        self.funct.wait_asserv()
        self.funct.node_asserv.action_goto_xy(1350,800, comm_asserv.Face.FACE_AVANT )

        self.funct.wait_asserv()
        logger.log_info("Strat_homologation", f"Position finale du robot: {self.robot}")

  
        module_unified_logger.unified_logger.log_python("Strat_homologation", "=== FIN DU MATCH ===")

    def run_strat(self):
        """
        Exécute TOUTE la stratégie du match
        """
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

    def run_strat_2(self):
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

    def run_strat_3(self):
        module_unified_logger.unified_logger.log_python("StratDynamique", "=== DÉBUT DU MATCH ===")

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

        asserv.action_translation(250,10,10)
        wait_a()
        asserv.action_goto_xy(500,1200) # intermediaire
        wait_a()
        asserv.action_goto_xy(1500,1200) 
        wait_a()
        asserv.action_goto_xy(1500,800) 
        wait_a()

        #poussee les 2 tas du milieu
        """ 
        asserv.action_goto_xy(2000,800) 
        wait_a()
        asserv.action_goto_xy(1000,800,comm_asserv.Face.FACE_ARRIERE) 
        wait_a()
        
        asserv.action_goto_xy(1500,800) 
        wait_a()
        """
        asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_Y, comm_asserv.Face.FACE_ARRIERE)
        wait_a()
        asserv.action_goto_xy(1500,175)
        wait_a()
        

        #ouvrir ax pour curseur
        autom.action_pos_ax(id_ax=5, pos_ax=820) 

        if (couleur == JAUNE):
            asserv.action_goto_xy(775,175) 
            wait_a()
        if (couleur == BLEU):
            asserv.action_goto_xy(775,175,comm_asserv.Face.FACE_ARRIERE)
            wait_a()

        autom.action_pos_ax(id_ax=5, pos_ax=495) 

        """ 
        asserv.action_goto_xy(1200,175,comm_asserv.Face.FACE_ARRIERE) 
        wait_a()
        asserv.action_goto_xy(200,800)
        wait_a()
         
        if (couleur == JAUNE):
            asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_X, comm_asserv.Face.FACE_ARRIERE)
        
        if (couleur == BLEU):
            asserv.action_recalibration(comm_asserv.Facing.POSITIVE_X, comm_asserv.Face.FACE_ARRIERE)
        """
        #wait_a()

        #asserv.action_goto_xy(200,800)
        #wait_a()
        #asserv.action_goto_xy(200,1700)
        #wait_a()




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




