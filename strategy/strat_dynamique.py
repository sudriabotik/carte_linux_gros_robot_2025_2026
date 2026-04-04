"""
Moteur de stratégie dynamique
Prend les décisions en fonction de l'état du robot et exécute le match complet
"""
from core.interface.can import canopen_wrapper
from core.interface.log_management import logger


class StratDynamique:
    """
    Moteur de stratégie dynamique qui orchestre le déroulement complet du match
    """

    def __init__(self, funct_strat, robot_state):
        """
        Initialise le moteur de stratégie dynamique

        Args:
            funct_strat: Instance de FunctStrat (pour envoyer toutes les commandes au robot)
            robot_state: État du robot (position, couleur, vitesse, etc.)
        """
        self.funct = funct_strat
        self.robot = robot_state
        logger.log_info("StratDynamique", "Moteur de stratégie dynamique initialisé")

    def run_strat(self):
        """
        Exécute TOUTE la stratégie du match

        Cette méthode unique orchestre :
        1. Attente du départ et lecture de la couleur
        2. Calage de départ
        3. Stratégie de jeu (actions, décisions dynamiques, etc.)
        4. Fin du match
        """
        canopen_wrapper.unified_logger.log_python("StratDynamique", "=== DÉBUT DU MATCH ===")

        # ======================
        # 1. ATTENTE DÉPART
        # ======================
        couleur = self.funct.wait_and_read_team_color()

        # ======================
        # 2. CALAGE DE DÉPART
        # ======================
        self.funct.calage_depart(couleur)

        # ======================
        # 3. STRATÉGIE DE JEU
        # ======================
        # TODO: Ici vous ajouterez toute votre logique de jeu
        # Exemple de boucle infinie pour stratégie dynamique :
        # while True:
        #     if self.robot.position_x > 1500:
        #         self.funct.attraper_un_tas()
        #     # ... autres décisions basées sur robot_state

        logger.log_info("StratDynamique", f"Position finale du robot: {self.robot}")

        # ======================
        # 4. FIN DU MATCH
        # ======================
        canopen_wrapper.unified_logger.log_python("StratDynamique", "=== FIN DU MATCH ===")
