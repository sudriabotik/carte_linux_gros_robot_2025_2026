#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de debug pour le robot

Ce module stocke les variables globales et importe toutes les fonctions de debug.

Usage dans debug_repl.py:
    import debug
    from debug import *

    # Initialiser les variables globales
    debug.node_asserv = hw.node_asserv
    debug.node_autom = hw.node_autom
    # ...

    # Utiliser les fonctions directement
    faire_carre(taille=300)
    test_rotation(angle=45)
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Imports utilises uniquement pour les type hints (pas au runtime)
    from core.interface.can.comm_asserv import CanAsservNode
    from core.interface.can.comm_autom import CanAutomNode
    from core.robot.robot import Robot
    from core.robot.function_strat import FunctStrat
    import can

# ============================================================================
# VARIABLES GLOBALES DU DEBUG
# Initialisees par debug_repl.py apres initialize_all()
# ============================================================================

node_asserv: 'CanAsservNode | None' = None
node_autom: 'CanAutomNode | None' = None
robot: 'Robot | None' = None
funct: 'FunctStrat | None' = None
bus: 'can.Bus | None' = None

# Variable de configuration pour l'auto-plot
# Si True, les fonctions de debug afficheront automatiquement les graphiques
auto_plot_enabled: bool = True

# Mode de plot pour l'auto-plot
# 'all' : Affiche les 6 graphiques (Global, PID Translation, PID Rotation, RPM, PID Mot R, PID Mot L)
# 'essential' : Affiche uniquement les 2 graphiques les plus importants (Global + RPM)
plot_mode: str = 'all'  # Defaut : mode essential (plus leger pour la Rock 5C)

# Dictionnaire pour stocker la derniere ligne lue de chaque fichier log
# Format: {filepath: last_line_number}
# Permet de ne parser que les nouvelles donnees lors de mouvements successifs
log_bookmarks: dict[str, int] = {}

# ============================================================================
# IMPORTS DES FONCTIONS DE DEBUG
# Rend toutes les fonctions accessibles via "from debug import *"
# ============================================================================

from debug.functions_debug import *

# Import du module plotter pour auto-plot
import debug.plotter as plotter

def reset_log_bookmarks():
    """
    Reinitialise tous les bookmarks de logs.

    Utile si on veut re-parser tous les logs depuis le debut
    apres avoir fait plusieurs mouvements successifs.

    Usage:
        debug.reset_log_bookmarks()
        translation_debug(300)  # Re-parse tout depuis le debut
    """
    log_bookmarks.clear()
    print("[DEBUG] Bookmarks de logs reinitialises")


__all__ = [
    # Variables globales
    'node_asserv',
    'node_autom',
    'robot',
    'funct',
    'bus',
    'auto_plot_enabled',
    'plot_mode',
    'log_bookmarks',
    # Modules
    'plotter',
    # Fonctions importees depuis debug.functions
    'faire_carre',
    'faire_rectangle',
    'faire_aller_retour',
    'faire_rotation_360',
    'test_translation',
    'test_rotation',
    'test_vitesse_progressive',
    'calibrer_tirette',
    'calibrer_couleur',
    'recalibrer_position',
    'attendre_tirette',
    'info_robot',
    'aide',
    'reset_log_bookmarks',
]
