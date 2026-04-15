"""
Moteur de stratégie dynamique
Prend les décisions en fonction de l'état du robot et exécute le match complet
"""
from core.interface.can import canopen_wrapper
from core.interface.log_management import logger

from strategy.generate_path_V2 import generate_path, generate_path_to_deposit_caca
from strategy.coordonner_strat import TAS_COORDS, DEPOSE_COORDS  # claude diane — ajout DEPOSE_COORDS

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
        self.zone_depose_utiliser = []  # zones de dépôt déjà utilisées (deviennent interdites)
        self.tas_attraper = []          # tas déjà ramassés
        logger.log_info("StratDynamique", "Moteur de stratégie dynamique initialisé")

    def run_strat(self):
        """
        Exécute TOUTE la stratégie du match
        """
        canopen_wrapper.unified_logger.log_python("StratDynamique", "=== DÉBUT DU MATCH ===")

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

        # Sauvegarder la position de départ (après calage, dépend de la couleur)
        self.position_depart = self.robot.get_position_x_y()

        # ======================
        # 3. STRATÉGIE DE JEU
        # ======================
        # 1. tas_1 → depot d3 → depot d4 + catch tas_3
        self.go_and_catch_tas('tas_1')
        self.available_tas.remove('tas_1')
        self.go_and_caca('d3', 4)
        self.go_caca_and_catch('d4', 4, 'tas_3')     # claude diane — d4 puis enchaîne tas_3
        self.available_tas.remove('tas_3')

        # 3. tas_4 → depot d5 → depot d9 + catch tas_6 → depot d8
        self.go_and_catch_tas('tas_4')
        self.available_tas.remove('tas_4')
        self.go_and_caca('d5', 4)
        self.go_caca_and_catch('d9', 4, 'tas_6')     # claude diane — d9 puis enchaîne tas_6 via t6_b
        self.available_tas.remove('tas_6')
        self.go_and_caca('d8', 4)

        # 5. Retour zone de départ
        self.funct.follow_path([self.robot.get_position_x_y(), self.position_depart], type_cible=2)

        logger.log_info("StratDynamique", f"Position finale du robot: {self.robot}")

        # ======================
        # 4. FIN DU MATCH
        # ======================
        canopen_wrapper.unified_logger.log_python("StratDynamique", "=== FIN DU MATCH ===")

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
            self.available_tas,              # Liste des tas disponibles
            self.zone_depose_utiliser        # claude diane — zones de dépôt déjà utilisées (interdites)
        )

        canopen_wrapper.unified_logger.log_python("StratDynamique", f" path : {path}")

        # 2. Suivre le chemin généré (type_cible=1 pour catch)
        self.funct.follow_path(path, type_cible=1)

        # 3. Attraper le tas à sa position centrale
        self.tas_attraper.append(target_tas)
        centre_tas = TAS_COORDS[target_tas]
        self.funct.catch_tas(centre_tas)

    def go_and_caca(self, target_zone_depose: str, num_element_ejecter: int):
        '''
        Cette fonction regroupe la génération de trajectoire
        et l'action de l'autom pour déposer des éléments (méthode caca)

        Args:
            target_zone_depose: Nom de la zone de dépôt (ex: 'd5')
            num_element_ejecter: Nombre d'éléments à éjecter
        '''
        # 1. Générer le chemin vers la zone de dépôt
        path = generate_path_to_deposit_caca(
            self.robot.get_position_x_y(),  # Position actuelle du robot
            target_zone_depose,              # Zone de dépôt cible
            self.robot_adv,                  # Position adversaire
            self.available_tas,              # Liste des tas disponibles
            self.zone_depose_utiliser        # Zones déjà utilisées (interdites)
        )

        canopen_wrapper.unified_logger.log_python("StratDynamique", f" path : {path}")

        # 2. Suivre le chemin généré
        self.funct.follow_path(path, type_cible=2)

        # 3. Orienter face arrière vers le centre du dépôt puis éjecter
        depot_center = DEPOSE_COORDS[target_zone_depose]              # claude diane
        self.funct.depose_caca_oriented(num_element_ejecter, depot_center)  # claude diane

        # 4. Marquer la zone comme utilisée (devient interdite pour les prochains chemins)
        self.zone_depose_utiliser.append(target_zone_depose)

    def go_caca_and_catch(self, target_zone_depose: str, num_element_ejecter: int, target_tas: str):  # claude diane
        '''
        Combine go_and_caca + go_and_catch_tas en un seul mouvement.
        Utiliser quand un dépôt est suivi d'un catch de tas proche pour
        éviter les allers-retours inutiles.

        Args:
            target_zone_depose: Zone de dépôt (ex: 'd3')
            num_element_ejecter: Nombre d'éléments à éjecter
            target_tas: Tas à attraper juste après (ex: 'tas_5')
        '''
        # 1. Chemin vers le dépôt
        path = generate_path_to_deposit_caca(
            self.robot.get_position_x_y(),
            target_zone_depose,
            self.robot_adv,
            self.available_tas,
            self.zone_depose_utiliser
        )

        canopen_wrapper.unified_logger.log_python("StratDynamique", f" caca_and_catch path depot: {path}")

        # 2. Suivre le chemin vers le dépôt (type_cible=2, pas de ready_to_grap)
        self.funct.follow_path(path, type_cible=2)

        # 3. Éjecter (orienté vers le dépôt) + enchaîner directement avec le catch
        depot_center = DEPOSE_COORDS[target_zone_depose]              # claude diane
        centre_tas = TAS_COORDS[target_tas]
        self.funct.caca_and_catch(num_element_ejecter, depot_center, centre_tas)  # claude diane

        # 4. Mise à jour état
        self.zone_depose_utiliser.append(target_zone_depose)
        self.tas_attraper.append(target_tas)
    # claude diane