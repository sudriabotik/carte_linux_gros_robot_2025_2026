import time
import os
import sys

from core.interface.can import comm_autom
from core.interface.can import comm_asserv
from core.interface.log_management import logger
from core.interface.can import constants as const
from core.interface.gpio.gpio import read_gpio_tirette, read_gpio_couleur
from core.robot.auto_wait_wrapper import AutoWaitWrapper

from core.interface.can.comm_asserv import CanAsservNode # Type hint uniquement (pour Ctrl+Click IDE)
from core.interface.can.comm_autom import CanAutomNode #  Type hint uniquement (pour Ctrl+Click IDE)
from core.robot.robot import Robot  # Type hint uniquement (pour Ctrl+Click IDE)

class FunctStrat:
    def __init__(self, node_autom: "CanAutomNode", node_asserv: "CanAsservNode", robot_state: "Robot"):

        # Enveloppe les nodes avec AutoWaitWrapper pour attente automatique
        # avant chaque action_* (élimine les wait manuels dans le code stratégie)
        self.node_autom :CanAutomNode  = AutoWaitWrapper(node_autom, self.wait_autom)
        self.node_asserv : CanAsservNode = AutoWaitWrapper(node_asserv, self.wait_asserv)

        #self.node_autom = node_autom
        #self.node_asserv = node_asserv
        self.robot_state = robot_state
        self.heartbeat_ON_OFF = True  


    def wait_asserv(self):  # CLAUDE
        while (self.node_asserv.is_busy()) :
            self.verifing_asserv_heartbeat_or_reset()  # CLAUDE: Only check asserv
            time.sleep(0.05)

    def wait_autom(self):  # CLAUDE
        while (self.node_autom.is_busy()) :
            self.verifing_autom_heartbeat_or_reset()  # CLAUDE: Only check autom
            time.sleep(0.05)

    def verifing_asserv_heartbeat_or_reset(self):  # CLAUDE: Check only asserv heartbeat
        if self.heartbeat_ON_OFF == False :
            return

        if (not self.node_asserv.check_heartbeat(4)):  # CLAUDE: Only asserv
            logger.log_error("FunctStrat", "HEARTBEAT TIMEOUT: node_asserv ne repond plus !")  # CLAUDE
            logger.log_error("FunctStrat", "REDEMARRAGE AUTOMATIQUE DU PROGRAMME...")  # CLAUDE
            time.sleep(1)  # CLAUDE: Attendre 1 seconde pour voir les logs
            os.execv(sys.executable, [sys.executable] + sys.argv)  # CLAUDE: Restart program

    def verifing_autom_heartbeat_or_reset(self):  # CLAUDE: Check only autom heartbeat
        if self.heartbeat_ON_OFF == False :
            return

        if (not self.node_autom.check_heartbeat(4)):  # CLAUDE: Only autom
            logger.log_error("FunctStrat", "HEARTBEAT TIMEOUT: node_autom ne repond plus !")  # CLAUDE
            logger.log_error("FunctStrat", "REDEMARRAGE AUTOMATIQUE DU PROGRAMME...")  # CLAUDE
            time.sleep(1)  # CLAUDE: Attendre 1 seconde pour voir les logs
            os.execv(sys.executable, [sys.executable] + sys.argv)  # CLAUDE: Restart program

    def verifing_all_node_heartbeat_or_reset(self):  # CLAUDE: Keep for other uses
        if self.heartbeat_ON_OFF == False :
            return

        if ((not self.node_autom.check_heartbeat(4)) or (not self.node_asserv.check_heartbeat(4))):  # CLAUDE
            logger.log_error("FunctStrat", "HEARTBEAT TIMEOUT: node_autom or node_asserv ne repond plus !")  # CLAUDE
            logger.log_error("FunctStrat", "REDEMARRAGE AUTOMATIQUE DU PROGRAMME...")  # CLAUDE
            time.sleep(1)  # CLAUDE: Attendre 1 seconde pour voir les logs
            os.execv(sys.executable, [sys.executable] + sys.argv)  # CLAUDE: Restart program

    def wait_heartbeat_all_node(self):  # CLAUDE: Wait for all CANopen nodes to be alive
        """
        Attend que tous les noeuds CANopen soient vivants (heartbeat OK).

        Verifie les heartbeats de:
        - node_asserv (carte asservissement)
        - node_autom (carte automation)
        """
        logger.log_info("FunctStrat", "Attente des heartbeats de tous les noeuds CAN...")  # CLAUDE

        while (not self.node_asserv.check_heartbeat(4)) or (not self.node_autom.check_heartbeat(4)):  # CLAUDE
            time.sleep(0.1)  # CLAUDE: Check every 100ms

        logger.log_info("FunctStrat", "Tous les noeuds CAN sont vivants !")  # CLAUDE

    def get_pos_cursor_x(self):
        if (self.robot_state.couleur_equipe == const.BLEU):
            return 650
        else:
            return 750

    def open_cursor(self):

        if (self.robot_state.couleur_equipe == const.BLEU):
            self.node_autom.action_open_cursor_2()
        else :
            self.node_autom.action_open_cursor()
    
    def close_cursor(self):
        if (self.robot_state.couleur_equipe == const.BLEU):
            self.node_autom.action_close_cursor_2()
        else:
            self.node_autom.action_close_cursor()


    def wait_and_read_team_color(self):
        """
        Attend que la tirette soit retirée et lit la couleur de l'équipe

        Returns:
            int: Couleur de l'équipe (const.BLEU ou const.JAUNE)
        """
        # Attente de la tirette
        logger.log_info("FunctStrat", "En attente de l'insertion de la tirette")
        while read_gpio_tirette() == const.ABSENCE_TIRETTE:
            self.verifing_all_node_heartbeat_or_reset()
            time.sleep(0.05)

        # Lecture de la couleur
        couleur = read_gpio_couleur()
        logger.log_info(
            "FunctStrat",
            f" Tirette insérer Couleur équipe {couleur} ({'BLEU' if couleur == const.BLEU else 'JAUNE'})"
        )

        # Mise à jour de l'état du robot
        self.robot_state.update_couleur_equipe(couleur)

        return couleur

    def wait_time_match(self, target_seconds: float):
        """
        Attend que le temps de match atteigne un certain nombre de secondes.
        
        :param target_seconds: Temps cible en secondes depuis le début du match (ex: 90)
        """
        
        if logger.initial_time == -1:
            logger.log_warning("wait_time_match", "Match time not started yet!")
            return
        
        while True:
            elapsed = time.time() - logger.initial_time
            if elapsed >= target_seconds:
                break
            time.sleep(0.1)  # Attendre 100ms avant de revérifier

    def calage_depart(self, couleur_equipe):

        logger.log_info("Stratégie", "Début du calage de départ")

        comm_asserv
        self.wait_autom()
        self.node_autom.action_safe_position_ascenseur()

        if (couleur_equipe == const.BLEU):
            logger.log_info("Stratégie", "Début du calage bleu")
            self.wait_asserv()
            self.node_asserv.action_recalibration(comm_asserv.Facing.POSITIVE_X, comm_asserv.Face.FACE_AVANT)

            self.wait_asserv()
            self.node_asserv.action_translation(-290) #410-115
            

        if (couleur_equipe == const.JAUNE):
            logger.log_info("Stratégie", "Début du calage JAUNE")
            
            self.wait_asserv()
            self.node_asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_X, comm_asserv.Face.FACE_ARRIERE)

            self.wait_asserv()
            self.node_asserv.action_translation(263) #410-147.5

        self.wait_asserv()
        self.node_asserv.action_recalibration(comm_asserv.Facing.POSITIVE_Y, comm_asserv.Face.FACE_AVANT)

        self.wait_asserv()
        #self.node_asserv.action_translation(-135) # 280 - 115.5 // #250 - 115
        self.node_asserv.action_goto_xy(0,1750, comm_asserv.Face.FACE_ARRIERE)

        self.wait_asserv()
        self.node_asserv.set_couleur(couleur_equipe)
        logger.log_info("Stratégie", "Fin du calage de départ")

    def wait_debut_match(self):
        '''
        On attend que la tirette soit retiré.
        '''

        while read_gpio_tirette() == const.PRESENCE_TIRETTE:
            self.verifing_all_node_heartbeat_or_reset()
            time.sleep(0.05)

        self.heartbeat_ON_OFF = False
        self.node_asserv.action_start_match()
        self.node_autom.action_start_match()
        logger.log_info("Stratégie", "DEBUT DU MATCH, tirette retirer")

    def attraper_un_tas(self):

        #orienter le robot vers le tas en question

        self.wait_autom()
        self.node_autom.action_open_pince()

        self.wait_asserv()
        self.node_asserv.action_translation(100, 20, 20)

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

        logger.log_info("Stratégie", f"catch_tas x={x}, y={y}")
        self.node_asserv.action_lookat(x, y, comm_asserv.Face.FACE_AVANT)
        self.wait_asserv()
        self.node_autom.action_open_pince()
        self.wait_autom()
        self.node_asserv.action_goto_xy(x, y, comm_asserv.Face.FACE_AVANT)
        self.wait_asserv()
        self.node_autom.action_grab()
        self.wait_autom()
        self.node_autom.action_deposit()


    def depose_element_zone(self,pos_cible:tuple,num_element_depose):

        #peut-être plusieurs pos cible
        logger.log_info("Stratégie", f"depose_element_zone x={x}, y={y}")

        # là comment on gère les mouvements.

        self.wait_autom()
        self.node_autom.action_ejecter(1) # pour l'instant seulement l'ejection d'un seul element fonctione

