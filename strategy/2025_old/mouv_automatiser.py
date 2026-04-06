import serialusM2M as s
import fonction_deplacement as fdd
import fonction_PID as pid
import fonction_Pos_Calage as pos
import Fonction_AX as AX
import FonctionAutom as fa
import time
import threading
import adv_tracker # lidar

class Robot:
    def __init__(self):
        self.Face_A = True # True --> Empty of tas //  #False --> Full of tas,
        self.Face_B_bas = True
        self.Face_B_haut = True 

    def priority_face(self):
        if self.Face_A:
            return "A"
        elif self.Face_B_bas:
            return "B_bas"
        elif self.Face_B_haut:
            return "B_haut"
        else:
            return None
        
    

def face_A_automatique(UART, threading):
    
    ser=UART[0]
    serv=UART[1]
    A=UART[2]
    B=UART[3]



