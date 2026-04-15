import serialusM2M as s
import fonction_deplacement as fdd
import fonction_PID as pid
import fonction_Pos_Calage as pos
import Fonction_AX as AX
import FonctionAutom as fa
import time
import threading
from communication_wifi.comm_wifi import get_tas_available
from strat_dynamique.generate_path import generate_path_to_next_tas
import adv_tracker # lidar

#adv_tracker.init_tracker(update_hz=100)  

def strat_intelligente(couleur, handle, start_time, UART):
    BLEU=0
    JAUNE=1
    
    ser=UART[0]
    serv=UART[1]
    A=UART[2]
    B=UART[3]
        
    try:
        x,y,t=pos.get_pos(ser)
        print("position robot",x,y,t)
#        fdd.rejoindre("1200","0800","1","050",ser)
#        fdd.orienter("000","050",ser)

        #adv_tracker.set_robot_pos(1200, 800, 0) # how to get la position de notre robot ?
        
        #time.sleep(2)
        #pos_adversaire = adv_tracker.get_adversary_pos()
        #print("pos_adversire",adv_tracker.get_adversary_pos())
        pos_adversaire = (2500,600)
        tas_available = get_tas_available(handle,start_time)
        list_points, orientation_objectif, callage_x, callage_y, sens = generate_path_to_next_tas((float(x), float(y)), pos_adversaire, tas_available)
        # on doit rajouter : orientation_objectif, face_choisir (si la face b quel acion), calage ou pas
        for point in list_points:
            # avant la dernière valeur de point, on va faire un mouvement
            if point == list_points[-2]:
                # avant le dernier point on lance le thread de la futur autom.
                Approch_A_thread = threading.Thread(target=fa.Approch_A, args=(A,serv))
                Approch_A_thread.start()
            fdd.rejoindre(point[0],point[1],"1","080",ser)

        fdd.orienter(orientation_objectif,"050",ser)
        # par attraper un tas j'ai besoin de savoir : 
        # - si on fait un callage
        # s'il y a un callage en x ou y + sens 0 ou 1
        # quel fonction choisir entre Approch_A ou Approch_B

        if callage_x:
            pos.Callage_X("0208","000",sens,"008",ser)
        elif callage_y:
            pos.Callage_Y("0208","270",sens,"008",ser)
        else:
            fdd.avancer("0208","050",ser)

        fa.Grab_A(A, serv)
        construct_thread_A = threading.Thread(target=fa.Construct_A, args=(A,))
        construct_thread_A.start()
        construct_thread_A.join()

        # what to do after the construction ?


    except KeyboardInterrupt:
        ser.close()
        A.close()
        B.close()
        ser.close()

    finally:
        ser.close()
        A.close()
        B.close()
        ser.close()    

