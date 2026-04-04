import time
from core.interface.can import comm_autom
from core.interface.can import comm_asserv
from core.interface.log_management import logger
from core.robot import constants as const
from core.interface.can import canopen_wrapper
from core.interface.gpio.gpio import read_gpio_tirette, read_gpio_couleur

class FunctStrat:
    def __init__(self, node_autom, node_asserv, robot_state):
        self.node_autom = node_autom
        self.node_asserv = node_asserv
        self.robot_state = robot_state

    def wait_asserv(self):
        while (self.node_asserv.is_busy()) :
            time.sleep(0.05)

    def wait_autom(self):
        while (self.node_autom.is_busy()) :
            time.sleep(0.05)

    def wait_and_read_team_color(self):
        """
        Attend que la tirette soit retirée et lit la couleur de l'équipe

        Returns:
            int: Couleur de l'équipe (const.BLEU ou const.JAUNE)
        """
        # Attente de la tirette
        canopen_wrapper.unified_logger.log_python("FunctStrat", "En attente de la tirette...")
        while read_gpio_tirette() == const.ABSENCE_TIRETTE:
            time.sleep(0.05)

        canopen_wrapper.unified_logger.log_python("FunctStrat", "Tirette retirée")

        # Lecture de la couleur
        couleur = read_gpio_couleur()
        canopen_wrapper.unified_logger.log_python(
            "FunctStrat",
            f"Couleur équipe {couleur} ({'BLEU' if couleur == const.BLEU else 'JAUNE'})"
        )

        # Mise à jour de l'état du robot
        self.robot_state.update_couleur_equipe(couleur)

        return couleur

    def calage_depart(self, couleur_equipe):

        canopen_wrapper.unified_logger.log_python("Stratégie", "Début du calage de départ")

        self.wait_autom()
        self.node_autom.action_safe_position_ascenseur()

        if (couleur_equipe == const.BLEU):
            canopen_wrapper.unified_logger.log_python("Stratégie", "Début du calage bleu")
            self.wait_asserv()
            self.node_asserv.action_recalibration(comm_asserv.Facing.POSITIVE_X, comm_asserv.Face.FACE_AVANT)

            self.wait_asserv()
            self.node_asserv.action_translation(-50, 10, 10)

        if (couleur_equipe == const.JAUNE):
            canopen_wrapper.unified_logger.log_python("Stratégie", "Début du calage JAUNE")
            self.wait_asserv()
            self.node_asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_X, comm_asserv.Face.FACE_ARRIERE)

            self.wait_asserv()
            self.node_asserv.action_translation(50, 10, 10)

        canopen_wrapper.unified_logger.log_python("Stratégie", " calage suite")
        self.wait_asserv()
        self.node_asserv.action_recalibration(comm_asserv.Facing.POSITIVE_Y, comm_asserv.Face.FACE_ARRIERE)

        self.wait_asserv()
        self.node_asserv.action_translation(50, 10, 10)

        self.wait_asserv()
        canopen_wrapper.unified_logger.log_python("Stratégie", "Fin du calage de départ")

    def attraper_un_tas(self):

        #orienter le robot vers le tas en question

        self.wait_autom()
        self.node_autom.action_open_pince()

        self.wait_asserv()
        self.node_asserv.action_translation(100, 10, 10)

        self.wait_autom()
        self.wait_asserv()
        self.node_autom.action_grab()

        self.wait_autom()
        self.node_autom.action_deposit()


