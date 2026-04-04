import time
import comm_autom
import comm_asserv
import logger
import constants as const
import canopen_wrapper

class Strategie:
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


