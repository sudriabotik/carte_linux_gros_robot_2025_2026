"""
Moteur de stratégie dynamique
Prend les décisions en fonction de l'état du robot et exécute le match complet
"""

import core.interface.log_management.unified_logger as module_unified_logger
from core.interface.log_management import logger

from strategy.generate_path_V2 import generate_path
from strategy.coordonner_strat import TAS_COORDS

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

    def run_strat(self):
        """
        Exécute TOUTE la stratégie du match
        """
        module_unified_logger.unified_logger.log_python("StratDynamique", "=== DÉBUT DU MATCH ===")

        # ======================
        # 1. ATTENTE DÉPART
        # ======================
        couleur = self.funct.wait_and_read_team_color()
        
        self.funct.node_autom.action_couleur_equipe(couleur)
        # ======================
        # 2. CALAGE DE DÉPART
        # ======================
        self.funct.calage_depart(couleur)

        self.funct.wait_debut_match()

        self.funct.node_asserv.action_evitement_on_off(False)
        # ======================
        # 3. STRATÉGIE DE JEU
        # ======================
        # TODO: Ici vous ajouterez toute votre logique de jeu
        # Exemple de boucle infinie pour stratégie dynamique :
        # il faut prendre en compte l'état du robot s'il a des elements de jeux ou pas. 
        # à partir d'un bibliothèque de choix de differente action possible : 
        # - attraper des elements de jeux
        # - deposer des elements de jeux
        # - aller un tas_d'elements de jeux
        # - pousser un tas d'element de jeux
        self.go_and_catch_tas('tas_1')
        self.go_and_catch_tas('tas_5')

        logger.log_info("StratDynamique", f"Position finale du robot: {self.robot}")

        # ======================
        # 4. FIN DU MATCH
        # ======================
        module_unified_logger.unified_logger.log_python("StratDynamique", "=== FIN DU MATCH ===")

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

        module_unified_logger.unified_logger.log_python("StratDynamique", f" path : {path}")

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

        module_unified_logger.unified_logger.log_python("StratDynamique", f" path : {path}")

        # 2. Suivre le chemin généré (type_cible=1 pour catch)
        self.funct.follow_path(path, type_cible=1)
        self.zone_depose_utiliser.append(target_zone_depose)
        
        # determiner les point cible pour les passer en parametre à la fonction 

        self.funct.depose_element_zone()
