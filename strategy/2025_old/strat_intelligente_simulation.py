import time

try:
    from strat_dynamique.generate_path import generate_path
except ImportError:
    from generate_path import generate_path
    


position_notre_robot = (300,1500)

position_robot_adersaire = (1100,1400)

generate_path(position_notre_robot, position_robot_adersaire)



def Strategy(strat,couleur, handle, start_time):
    time.sleep(30)