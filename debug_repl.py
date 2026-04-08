#!/usr/bin/env python3
"""
Script de debug REPL pour tester les commandes du robot ligne par ligne

Usage: python -i debug_repl.py

Ce script initialise tout le matériel et crée des variables globales
pour permettre l'exécution de commandes individuelles avec Shift+Enter
"""

# Imports nécessaires
from core.init_core import initialize_all
from strategy.strat_dynamique import StratDynamique
from core.interface.can import comm_asserv, comm_autom
from core.robot import constants as const
from core.interface.can import canopen_wrapper
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
print("  Pour arrêter proprement: canopen_wrapper.unified_logger.stop()")
print("=" * 60 + "\n")
