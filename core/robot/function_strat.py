import time
from core.interface.can import comm_autom
from core.interface.can import comm_asserv
from core.interface.log_management import logger
from core.interface.can import constants as const
from core.interface.can import canopen_wrapper
from core.interface.gpio.gpio import read_gpio_tirette, read_gpio_couleur

from core.interface.can.comm_asserv import CanAsservNode # Type hint uniquement (pour Ctrl+Click IDE)
from core.interface.can.comm_autom import CanAutomNode #  Type hint uniquement (pour Ctrl+Click IDE)
from core.robot.robot import Robot  # Type hint uniquement (pour Ctrl+Click IDE)

class FunctStrat:
    def __init__(self, node_autom: "CanAutomNode", node_asserv: "CanAsservNode", robot_state: "Robot"):
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
        canopen_wrapper.unified_logger.log_python("FunctStrat", "En attente de l'insertion de la tirette")
        while read_gpio_tirette() == const.ABSENCE_TIRETTE:
            time.sleep(0.05)

        # Lecture de la couleur
        couleur = read_gpio_couleur()
        canopen_wrapper.unified_logger.log_python(
            "FunctStrat",
            f" Tirette insérer Couleur équipe {couleur} ({'BLEU' if couleur == const.BLEU else 'JAUNE'})"
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

    def wait_debut_match(self):
        '''
        On attend que la tirette soit retiré.
        '''

        while read_gpio_tirette() == const.PRESENCE_TIRETTE:
            time.sleep(0.05)

        canopen_wrapper.unified_logger.log_python("Stratégie", "DEBUT DU MATCH, tirette retirer")

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


    def follow_path (self, path: "List[Tuple[float, float]]",type_cible:int):
        #type_cible = 1 --> catch
        #type_cible = 2 --> deposite
        for i, point in enumerate(path):
            #print(f"  {i+1}. {point}")
            if ((i == len(path)-2) and (type_cible == 1) ):
                #pour l'avant dernière trajectoire on prépare l'autom catch
                if ( not(self.node_autom.is_busy)):
                    self.node_autom.action_ready_to_grap()

            self.wait_asserv()
            x = point[0]
            y = point[1]
            self.node_asserv.action_goto_xy(x, y, comm_asserv.Face.FACE_AVANT)
            self.wait_asserv()

    def catch_tas(self, centre_tas: tuple):
        x = centre_tas[0]
        y = centre_tas[1]

        canopen_wrapper.unified_logger.log_python("Stratégie", f"catch_tas x={x}, y={y}")
        self.node_asserv.action_lookat(x, y, comm_asserv.Face.FACE_AVANT)
        self.wait_asserv()
        self.node_autom.action_open_pince()
        self.wait_autom()
        self.node_asserv.action_goto_xy(x, y, comm_asserv.Face.FACE_AVANT)
        self.wait_asserv()
        self.node_autom.action_grab()
        self.wait_autom()
        self.node_autom.action_deposit()

