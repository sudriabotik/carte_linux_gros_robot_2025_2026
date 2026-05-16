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

from strategy.strategies import strat_homologation
from strategy.strategies import strat_test_autom
from strategy.strategies import strat_1
from strategy.strategies import strat_2
from strategy.strategies import test_paralle
from strategy.strategies import strat_qualif
from strategy.strategies import strat_final_test
from strategy.strategies import strat_final

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
        """Exécute la stratégie d'homologation"""
        strat_homologation.run(self.funct, self.robot)

    def run_strat_1(self):
        strat_1.run(self.funct, self.robot)

    def run_test_autom(self):
        strat_test_autom.run(self.funct, self.robot)

    def run_strat_2(self):
        strat_2.run(self.funct, self.robot)

    def run_test_parallel(self):
        test_paralle.run(self.funct, self.robot)

    def run_strat_qualif(self):
        strat_qualif.run(self.funct, self.robot)
    
    def run_strat_final_test(self):
        strat_final_test.run(self.funct, self.robot)

    def run_strat_final(self):
        strat_final.run(self.funct, self.robot)

    #### fonction intelligente #### 

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




