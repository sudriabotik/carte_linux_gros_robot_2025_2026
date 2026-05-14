#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fonctions de debug reutilisables pour tester le robot

Ces fonctions utilisent les variables globales definies dans debug.__init__
"""

import time
import debug  # Import du module pour acceder aux variables globales
from core.interface.can import comm_asserv
from core.interface.gpio.gpio import read_gpio_tirette, read_gpio_couleur
from core.robot import constants as const


from core.interface.can.comm_asserv import CanAsservNode # Type hint uniquement (pour Ctrl+Click IDE)
from core.interface.can.comm_autom import CanAutomNode #  Type hint uniquement (pour Ctrl+Click IDE)
from core.robot.robot import Robot  # Type hint uniquement (pour Ctrl+Click IDE)

# ============================================================================
# MOUVEMENTS GEOMETRIQUES
# ============================================================================

def calage ():
    debug.node_asserv.action_recalibration(comm_asserv.Facing.POSITIVE_X,comm_asserv.Face.FACE_ARRIERE)
    debug.funct.wait_asserv()
    debug.node_asserv.action_translation(1500)
    debug.funct.wait_asserv()
    debug.node_asserv.action_recalibration(comm_asserv.Facing.NEGATIVE_Y,comm_asserv.Face.FACE_ARRIERE)
    debug.funct.wait_asserv()
    debug.node_asserv.action_translation(52)
    debug.node_asserv.action_orientation(0)

def faire_carre(taille=200, vitesse=10, accel=10):
    """
    Fait un carre de la taille donnee

    :param taille: Taille du cote en mm (defaut: 200)
    :param vitesse: Vitesse en mm/s (defaut: 10)
    :param accel: Acceleration en mm/s^2 (defaut: 10)
    """
    print(f"[CARRE] Faire un carre de {taille}mm a {vitesse}mm/s...")

    for i in range(4):
        print(f"  Cote {i+1}/4...")
        debug.node_asserv.action_translation(taille, vitesse, accel)
        debug.funct.wait_asserv()

        print(f"  Rotation 90deg...")
        debug.node_asserv.action_rotation(90, vitesse, accel)
        debug.funct.wait_asserv()

    print("[OK] Carre termine !")



def faire_aller_retour(distance=200, vitesse=10, accel=10):
    """
    Fait un aller-retour lineaire

    :param distance: Distance en mm (defaut: 200)
    :param vitesse: Vitesse en mm/s (defaut: 10)
    :param accel: Acceleration en mm/s^2 (defaut: 10)
    """
    print(f"[ALLER-RETOUR] {distance}mm...")

    print(f"  Aller...")
    debug.node_asserv.action_translation(distance, vitesse, accel)
    debug.funct.wait_asserv()

    print(f"  Retour...")
    debug.node_asserv.action_translation(-distance, vitesse, accel)
    debug.funct.wait_asserv()

    print("[OK] Aller-retour termine !")

# ============================================================================
# MOUVEMENT AVEC DEBUG PRINT ON
# ============================================================================

def translation_debug(distance_mm, vitesse=100, accel=100, auto_plot=None):
    """
    Execute une translation avec debug UART active.

    :param distance_mm: Distance de translation en mm
    :param vitesse: Vitesse en pourcentage (0-100, defaut: 100)
    :param accel: Acceleration en pourcentage (0-100, defaut: 100)
    :param auto_plot: Si True, affiche automatiquement les graphiques apres le mouvement.
                      Si None, utilise la valeur de debug.auto_plot_enabled.
                      Si False, pas de plot.
    """
    debug.funct.heartbeat_ON_OFF = False
    debug.node_asserv.action_debug_on_off(enable=True)
    debug.funct.wait_asserv()
    debug.node_asserv.action_translation(distance_mm, vitesse, accel)
    debug.funct.wait_asserv()
    debug.node_asserv.action_debug_on_off(enable=False)

    # Auto-plot si demande - utilise le nouveau plotter generique
    should_plot = auto_plot if auto_plot is not None else debug.auto_plot_enabled
    if should_plot:
        time.sleep(0.5)  # Attendre que les logs soient bien ecrits
        import debug.plotter_generic as plotter_generic
        plotter_generic.plot_last_log()

def rotation_debug(degrés, vitesse=100, accel=100, auto_plot=None):
    """
    Execute une rotation avec debug UART active.

    :param degrés: Angle de rotation en degrés
    :param vitesse: Vitesse en pourcentage (0-100, defaut: 100)
    :param accel: Acceleration en pourcentage (0-100, defaut: 100)
    :param auto_plot: Si True, affiche automatiquement les graphiques apres le mouvement.
                      Si None, utilise la valeur de debug.auto_plot_enabled.
                      Si False, pas de plot.
    """
    debug.funct.heartbeat_ON_OFF = False
    debug.node_asserv.action_debug_on_off(enable=True)
    debug.funct.wait_asserv()
    debug.node_asserv.action_rotation(degrés, vitesse, accel)
    debug.funct.wait_asserv()
    debug.node_asserv.action_debug_on_off(enable=False)

    # Auto-plot si demande - utilise le nouveau plotter generique
    should_plot = auto_plot if auto_plot is not None else debug.auto_plot_enabled
    if should_plot:
        time.sleep(0.5)  # Attendre que les logs soient bien ecrits
        import debug.plotter_generic as plotter_generic
        plotter_generic.plot_last_log()


def hold_debug(time_debug_sec, auto_plot=None):
    """
    Active le debug UART pendant un certain temps.

    :param time_debug_sec: Duree en secondes
    :param auto_plot: Si True, affiche automatiquement les graphiques apres.
                      Si None, utilise la valeur de debug.auto_plot_enabled.
                      Si False, pas de plot.
    """
    debug.node_asserv.action_debug_on_off(enable=True)
    time.sleep(time_debug_sec)
    debug.node_asserv.action_debug_on_off(enable=False)

    # Auto-plot si demande
    should_plot = auto_plot if auto_plot is not None else debug.auto_plot_enabled
    if should_plot:
        time.sleep(0.5)  # Attendre que les logs soient bien ecrits
        debug.plotter.plot_last_log(plot_mode=debug.plot_mode)

def move_to_debug(x_mm, y_mm, face : comm_asserv.Face, auto_plot=None):
    """
    Execute un moveto avec debug UART active.

    :param x_mm: Coordonnee X en mm
    :param y_mm: Coordonnee Y en mm
    :param face: Face a utiliser (FACE_AVANT ou FACE_ARRIERE)
    :param auto_plot: Si True, affiche automatiquement les graphiques apres le mouvement.
                      Si None, utilise la valeur de debug.auto_plot_enabled.
                      Si False, pas de plot.
    """
    debug.node_asserv.action_debug_on_off(enable=True)
    debug.funct.wait_asserv()
    debug.node_asserv.action_moveto(x_mm, y_mm, face)
    debug.funct.wait_asserv()
    debug.node_asserv.action_debug_on_off(enable=False)

    # Auto-plot si demande
    should_plot = auto_plot if auto_plot is not None else debug.auto_plot_enabled
    if should_plot:
        time.sleep(0.5)  # Attendre que les logs soient bien ecrits
        debug.plotter.plot_last_log(plot_mode=debug.plot_mode)

# ============================================================================
# TESTS CALIBRATION & GPIO
# ============================================================================

def calibrer_tirette():
    """
    Test de lecture de la tirette
    """
    print("[GPIO] Test tirette...")

    etat = read_gpio_tirette()

    if etat == const.PRESENCE_TIRETTE:
        print("  [OK] Tirette PRESENTE")
    else:
        print("  [!] Tirette ABSENTE")

    return etat


def calibrer_couleur():
    """
    Test de lecture de la couleur
    """
    print("[GPIO] Test couleur...")

    couleur = read_gpio_couleur()

    if couleur == 0:
        print("  [BLEU] Equipe BLEUE")
    else:
        print("  [JAUNE] Equipe JAUNE")

    return couleur


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def attendre_tirette():
    """
    Attend que la tirette soit retiree
    """
    print("[ATTENTE] En attente du retrait de la tirette...")

    while read_gpio_tirette() == const.PRESENCE_TIRETTE:
        time.sleep(0.1)

    print("[GO] Tirette retiree ! GO !")


def info_robot():
    """
    Affiche les informations du robot (couleur, tirette)
    """
    print("\n" + "=" * 50)
    print("INFORMATIONS ROBOT")
    print("=" * 50)

    # Couleur
    couleur = read_gpio_couleur()
    if couleur == 0:
        print("Couleur : BLEU")
    else:
        print("Couleur : JAUNE")

    # Tirette
    tirette = read_gpio_tirette()
    if tirette == const.PRESENCE_TIRETTE:
        print("Tirette : PRESENTE")
    else:
        print("Tirette : ABSENTE")

    print("=" * 50 + "\n")

