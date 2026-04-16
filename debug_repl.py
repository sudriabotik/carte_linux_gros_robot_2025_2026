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

print("=" * 60)
print("🔧 INITIALISATION DU ROBOT...")
print("=" * 60)

# Initialisation complète du robot
hw = initialize_all()

# Créer des variables globales pour accès direct dans le REPL
node_asserv = hw.node_asserv
node_autom = hw.node_autom
robot = hw.robot_state
funct = hw.strat
bus = hw.bus

print("\n" + "=" * 60)
print("✅ DEBUG REPL READY!")
print("=" * 60)

print("\n📋 VARIABLES DISPONIBLES:")
print("  • node_asserv  → Commandes asservissement (déplacement)")
print("  • node_autom   → Commandes automation (actionneurs)")
print("  • robot        → État du robot (position, couleur)")
print("  • funct        → Fonctions stratégie complètes")
print("  • bus          → Bus CAN")

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

node_autom.action_homing(speed_v_percent=10, speed_h_percent=10)
node_autom.action_grab()
node_autom.action_deposit()
node_autom.action_pos_elevator_h(pos_mm=100)
node_autom.action_pos_elevator_v(pos_mm=200)
node_autom.action_pos_ax(id_ax=2, pos_ax=200)
node_autom.action_pump_on_off(on_off=True)
node_autom.action_open_pince()
node_autom.action_close_pince()
node_autom.action_ejecter(num_element=1)
node_autom.action_i2c_servo(channel=0, position=1500)
node_autom.action_ready_to_grap()
node_autom.action_safe_position_ascenseur()
node_autom.action_couleur_equipe(couleur_equipe=0)
node_autom.action_fermer_porte_rentrer_ax_caca()
node_autom.action_pos_vitesse_ax(6,500,100)
"""



"""
========== TOUTES LES FONCTIONS NODE_ASSERV ==========

node_asserv.action_set_linear_speed_accel(speed=100, acceleration=50)
node_asserv.action_set_angular_speed_accel(speed=100, acceleration=50)
node_asserv.action_translation(distance_mm=-1500, speed=100, accel=50)
node_asserv.action_rotation(angle_deg=(360*10), speed=100, accel=50)
node_asserv.action_goto_xy(x_mm=1000, y_mm=1500, face=comm_asserv.Face.FACE_AVANT)
node_asserv.action_recalibration(facing=comm_asserv.Facing.NEGATIVE_X, face=comm_asserv.Face.FACE_ARRIERE)
node_asserv.action_moveto(x_mm=800, y_mm=1200, face=comm_asserv.Face.FACE_AVANT)
node_asserv.action_lookat(x_mm=1500, y_mm=1000, face=comm_asserv.Face.FACE_AVANT)
node_asserv.action_orientation(target_angle_deg=0, face=comm_asserv.Face.FACE_AVANT, speed_percent=100, accel_percent=100)
node_asserv.action_evitement_on_off(enable=True)
node_asserv.action_debug_on_off(enable=True)
"""
