#!/usr/bin/env python3
"""
Script de debug REPL pour tester les commandes du robot ligne par ligne

Usage: python3 -i debug_repl.py

Ce script initialise tout le matériel et crée des variables globales
pour permettre l'exécution de commandes individuelles avec Shift+Enter
"""

# Imports nécessaires
from core.init_core import initialize_all
from strategy.strat_dynamique import StratDynamique
from core.interface.can import comm_asserv, comm_autom
from core.robot import constants as const
import core.interface.log_management.logger as logger
import time


from core.robot.function_strat import FunctStrat
from core.interface.can.comm_asserv import CanAsservNode # Type hint uniquement (pour Ctrl+Click IDE)
from core.interface.can.comm_autom import CanAutomNode #  Type hint uniquement (pour Ctrl+Click IDE)
from core.robot.robot import Robot  # Type hint uniquement (pour Ctrl+Click IDE)


# Import du module debug
from debug.functions_debug import *  # Importe toutes les fonctions de debug

print("=" * 60)
print("🔧 INITIALISATION DU ROBOT...")
print("=" * 60)

# Initialisation complète du robot
hw = initialize_all()

# Type hints pour l'IDE
asserv: CanAsservNode
autom: CanAutomNode
robot: Robot
funct: FunctStrat

# Créer des variables globales pour accès direct dans le REPL
asserv = hw.node_asserv
autom = hw.node_autom
robot = hw.robot_state
funct = hw.strat
bus = hw.bus

# Initialiser les variables globales du module debug
debug.node_asserv = hw.node_asserv
debug.node_autom = hw.node_autom
debug.robot = hw.robot_state
debug.funct = hw.strat
debug.bus = hw.bus

print("\n" + "=" * 60)
print("✅ DEBUG REPL READY!")
print("=" * 60)

print("\n📋 VARIABLES DISPONIBLES:")
print("  • node_asserv  → Commandes asservissement (déplacement)")
print("  • node_autom   → Commandes automation (actionneurs)")
print("  • robot        → État du robot (position, couleur)")
print("  • funct        → Fonctions stratégie complètes")
print("  • bus          → Bus CAN")

print("\n🎮 FONCTIONS DE DEBUG RAPIDES:")
print("  • faire_carre(taille=300)         → Fait un carré")
print("  • test_rotation(angle=45)         → Test rotation")
print("  • info_robot()                    → Affiche infos robot")
print("  • aide()                          → Liste toutes les fonctions")

print("\n💡 EXEMPLES DE COMMANDES:")
print("  # Commandes asservissement")
print("  >>> node_asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_X, comm_asserv.Face.FACE_ARRIERE)")
print("  >>> node_asserv.action_goto_xy(1000, 500, comm_asserv.Face.FACE_AVANT)")
print("  >>> node_asserv.action_translation(100, 10, 10)")
print()
print("  # Commandes automation")
print("  >>> node_autom.action_open_pince()")
print("  >>> node_autom.action_grab()")
print()
print("  # Fonctions stratégie")
print("  >>> funct.calage_depart(const.JAUNE)")
print("  >>> funct.wait_asserv()")
print("  >>> funct.wait_and_read_team_color()")
print()
print("  # État du robot")
print("  >>> robot.get_position()")
print("  >>> robot.couleur_equipe")

print("\n🎯 UTILISATION AVEC SHIFT+ENTER:")
print("  Dans function_strat.py, remplace:")
print("    self.node_asserv → node_asserv")
print("    self.node_autom  → node_autom")
print("    self.wait_asserv() → funct.wait_asserv()")

print("\n N'OUBLIE PAS:")
print("  Pour quitter: Ctrl+D ou exit()")
print("  Pour arrêter proprement: unified_logger.stop()")
print("=" * 60 + "\n")


""" 
========== TOUTES LES FONCTIONS NODE_AUTOM ==========

autom.action_homing(speed_v_percent=13, speed_h_percent=13)
autom.action_grab()
autom.action_deposit()
autom.action_pos_elevator_h(pos_mm=-100)
autom.action_pos_elevator_v(pos_mm=-200)
autom.action_pos_ax(id_ax=2, pos_ax=200)
autom.action_pump_on_off(on_off=True)
autom.action_open_pince()
autom.action_close_pince()
autom.action_ejecter(num_element=1)
autom.action_i2c_servo(channel=0, position=1500)
autom.action_ready_to_grap()
autom.action_safe_position_ascenseur()
autom.action_couleur_equipe(couleur_equipe=0)
autom.action_fermer_porte_rentrer_ax_caca()
autom.action_pos_vitesse_ax(6,500,100)
autom.action_pos_ax_caca_calage()
autom.action_open_cursor()
autom.action_close_cursor()
autom.action_open_cursor_2()
autom.action_close_cursor_2()
autom.action_grab_pince()
autom.action_start_match()
autom.action_emergency_stop()
"""
""" 
#========== TOUTES LES FONCTIONS NODE_ASSERV ==========

asserv.action_set_linear_speed_accel(speed=100, acceleration=50)
asserv.action_set_angular_speed_accel(speed=100, acceleration=50)
asserv.action_evitement_on_off(enable=True)
asserv.action_debug_on_off(enable=True)

asserv.action_set_pid_hold(kp=1.5, ki=0.5, kd=0.1, max_output=100.0, i_lim=50.0, min_output=-100.0)
asserv.action_set_pid_vitesse(kp=0.23, ki=0.4, kd=20.0, kff=0.0, i_lim=50.0, max_output=100.0)
asserv.action_set_pid_translation(kp=0.1, ki=0, kd=0, max_output=1.0)
asserv.action_set_pid_rotation(kp=0.1, ki=0, kd=0, max_output=360.0)

asserv.action_start_match()
asserv.action_emergency_stop()

asserv.action_translation(distance_mm=-1500, speed_percent=100, accel_percent=50)
asserv.action_rotation(angle_deg=(360*10), speed_percent=100, accel_percent=50)
asserv.action_goto_xy(x_mm=1000, y_mm=1500, face=comm_asserv.Face.FACE_AVANT)
asserv.action_recalibration(facing=comm_asserv.Facing.NEGATIVE_X, face=comm_asserv.Face.FACE_ARRIERE)
asserv.action_recalibration(facing=comm_asserv.Facing.POSITIVE_X, face=comm_asserv.Face.FACE_AVANT)
asserv.action_recalibration(facing=comm_asserv.Facing.POSITIVE_Y, face=comm_asserv.Face.FACE_ARRIERE)
asserv.action_moveto(x_mm=800, y_mm=1200, face=comm_asserv.Face.FACE_AVANT)
asserv.action_lookat(x_mm=1500, y_mm=1000, face=comm_asserv.Face.FACE_AVANT)
asserv.action_orientation(target_angle_deg=0, face=comm_asserv.Face.FACE_AVANT, speed_percent=100, accel_percent=100)
""" 


calage()
hold_debug(3)
translation_debug(-50,90,70)
translation_debug(-1500,100,60)
rotation_debug(90)

# PID VITESSE
funct.wait_asserv()
asserv.action_set_pid_vitesse(kp=0.3, ki=1, kd=0.0, kff=0.1, i_lim=5.0 )
#PID POSITION
funct.wait_asserv()
asserv.action_set_pid_translation(kp=15, ki=0, kd=0, max_output=1)
funct.wait_asserv()
asserv.action_set_pid_rotation(kp=0.1, ki=0, kd=0 )

