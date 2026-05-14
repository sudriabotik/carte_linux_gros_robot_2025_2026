#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de plotting simplifié pour les logs UART de debug rotation.

Affiche UNE SEULE courbe : consigne vs mesure de rotation.
Adapté pour le nouveau code C qui print moins de variables.

Usage:
    import debug.plotter_rotation as plotter_rotation

    # Plot le dernier log automatiquement
    plotter_rotation.plot_last_log()

    # Plot un fichier specifique
    plotter_rotation.plot_log_file("log/2026-04-28_12:34:56:789/log_123456.txt")
"""

import os
import re
import glob
import matplotlib
import matplotlib.pyplot as plt

# Backend pour VNC (bureau deporte)
matplotlib.use('TkAgg')


def find_latest_log():
    """
    Trouve automatiquement le dernier fichier log cree.

    Cherche dans log/YYYY-MM-DD_HH:MM:SS:mmm/log_XXXXXX.txt
    et retourne le fichier log le plus recent.

    :return: Chemin vers le dernier fichier log, ou None si aucun trouve
    """
    log_dir = "log"

    if not os.path.exists(log_dir):
        print(f"[PLOTTER_ROTATION] Le dossier '{log_dir}' n'existe pas !")
        return None

    # Trouver tous les dossiers de logs (format YYYY-MM-DD_HH:MM:SS:mmm)
    log_folders = glob.glob(os.path.join(log_dir, "*"))
    log_folders = [f for f in log_folders if os.path.isdir(f)]

    if not log_folders:
        print(f"[PLOTTER_ROTATION] Aucun dossier de log trouve dans '{log_dir}' !")
        return None

    # Trier par date de modification (le plus recent en premier)
    log_folders.sort(key=os.path.getmtime, reverse=True)
    latest_folder = log_folders[0]

    # Trouver tous les fichiers log_*.txt dans le dossier le plus recent
    log_files = glob.glob(os.path.join(latest_folder, "log_*.txt"))

    if not log_files:
        print(f"[PLOTTER_ROTATION] Aucun fichier log trouve dans '{latest_folder}' !")
        return None

    # Trier par taille de fichier (le plus gros en premier)
    # Le fichier avec les logs UART de debug rotation est toujours le plus volumineux
    log_files.sort(key=os.path.getsize, reverse=True)
    latest_log = log_files[0]

    return latest_log


def parse_rotation_log(filepath, start_line=0):
    """
    Parse un fichier log UART de debug rotation (version simplifiee).

    Extrait uniquement les 3 variables essentielles du nouveau code C:
    - T = XXX (temps en secondes)
    - target_deg = XXX (consigne de rotation)
    - actual_deg = XXX (rotation mesuree)

    :param filepath: Chemin vers le fichier log
    :param start_line: Ligne de depart (0 = debut du fichier)
    :return: Tuple (time_data, target_data, actual_data, last_line_number)
    """
    time_data = []
    target_data = []
    actual_data = []

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)

    def clean_line(line):
        """
        Nettoie une ligne en enlevant les marqueurs de log UART parasites.
        Exemple: ">> [INFO] [timestamp] [UART_ASSERV] : T = 0.5000"
        devient: "T = 0.5000"
        """
        # Enlever le prefixe >> [INFO] [timestamp] [UART_ASSERV] :
        line = re.sub(r'^>>\s*\[INFO\]\s*\[.*?\]\s*\[.*?\]\s*\[UART_ASSERV\]\s*:\s*', '', line)
        return line.strip()

    # Commencer a la ligne start_line (skip les lignes precedentes)
    i = start_line
    while i < len(lines):
        raw_line = lines[i].strip()
        line = clean_line(raw_line)

        # Detection du debut d'une boucle
        if '__START_LOOP__' in line:
            current_time = None
            current_target = None
            current_actual = None

            # Parser toutes les lignes jusqu'a __END_LOOP__
            i += 1

            while i < len(lines):
                raw_line = lines[i].strip()
                line = clean_line(raw_line)

                # Detection de la fin de la boucle
                if '__END_LOOP__' in line:
                    # Enregistrer les donnees si toutes les 3 variables sont presentes
                    if current_time is not None and current_target is not None and current_actual is not None:
                        time_data.append(current_time)
                        target_data.append(current_target)
                        actual_data.append(current_actual)
                    break

                # Parser les 3 variables essentielles
                # Format: T = 0.5000
                time_match = re.search(r'\bT\s*=\s*([\d.]+)', line)
                if time_match:
                    current_time = float(time_match.group(1))

                # Format: target_deg = 90.000
                target_match = re.search(r'\btarget_deg\s*=\s*([+-]?[\d.]+)', line)
                if target_match:
                    current_target = float(target_match.group(1))

                # Format: actual_deg = 45.123
                actual_match = re.search(r'\bactual_deg\s*=\s*([+-]?[\d.]+)', line)
                if actual_match:
                    current_actual = float(actual_match.group(1))

                i += 1

        i += 1

    # Retourner les donnees et le numero de la derniere ligne lue
    return time_data, target_data, actual_data, total_lines


def plot_rotation_data(time_data, target_data, actual_data, log_filename, save_png=False, show_plot=True):
    """
    Affiche UN SEUL graphique : consigne vs mesure de rotation.

    :param time_data: Liste des timestamps
    :param target_data: Liste des consignes de rotation (target_deg)
    :param actual_data: Liste des rotations mesurees (actual_deg)
    :param log_filename: Nom du fichier log (pour le titre)
    :param save_png: Si True, sauvegarde le graphique en PNG
    :param show_plot: Si True, affiche le graphique (plt.show())
    :return: Figure creee
    """
    if not time_data or not target_data or not actual_data:
        print("[PLOTTER_ROTATION] Aucune donnee a afficher !")
        return None

    if len(time_data) < 10:
        print(f"[PLOTTER_ROTATION] Trop peu de donnees ({len(time_data)} points). Minimum 10 requis.")
        return None

    # Creer le graphique
    fig, ax = plt.subplots(figsize=(14, 8))

    # Tracer les deux courbes
    line_target, = ax.plot(time_data, target_data, label='Consigne (target_deg)',
                           color='blue', linewidth=2, linestyle='--')

    line_actual, = ax.plot(time_data, actual_data, label='Mesure (actual_deg)',
                           color='red', linewidth=2, marker='o', markersize=3)

    # Calculer l'erreur finale
    if len(target_data) > 0 and len(actual_data) > 0:
        final_error = abs(target_data[-1] - actual_data[-1])
        ax.text(0.02, 0.98, f'Erreur finale: {final_error:.2f}°',
                transform=ax.transAxes, fontsize=12, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # Configuration de la legende interactive
    leg = ax.legend(loc='upper left', fontsize=12)

    # Rendre la legende interactive (cliquer pour masquer/afficher)
    lines = [line_target, line_actual]
    lined = {}  # Map entre legende et ligne
    for legline, origline in zip(leg.get_lines(), lines):
        legline.set_picker(5)  # Zone cliquable de 5 pixels
        lined[legline] = origline

    def on_pick(event):
        """Callback pour masquer/afficher une courbe quand on clique sur la legende"""
        legline = event.artist
        origline = lined[legline]
        visible = not origline.get_visible()
        origline.set_visible(visible)
        # Changer l'opacite de la legende pour indiquer l'etat
        legline.set_alpha(1.0 if visible else 0.2)
        fig.canvas.draw()

    fig.canvas.mpl_connect('pick_event', on_pick)

    # Labels et titre
    ax.set_xlabel('Temps (s)', fontsize=14)
    ax.set_ylabel('Angle (degrés)', fontsize=14)
    ax.set_title(f'Debug Rotation - {log_filename}\n(Cliquer sur la legende pour masquer/afficher)',
                fontsize=16, fontweight='bold')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Sauvegarder en PNG si demande
    if save_png:
        output_file = log_filename.replace('.txt', '_rotation.png')
        fig.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"[PLOTTER_ROTATION] Graphique sauvegarde : {output_file}")

    # Afficher le graphique
    if show_plot:
        print(f"[PLOTTER_ROTATION] Graphique affiche ! {len(time_data)} points traces.")
        plt.show()

    return fig


def plot_log_file(filepath, save_png=False, show_plot=True, start_line=0):
    """
    Parse et plot un fichier log specifique.

    :param filepath: Chemin vers le fichier log
    :param save_png: Si True, sauvegarde le graphique en PNG
    :param show_plot: Si True, affiche le graphique (plt.show())
    :param start_line: Ligne de depart pour parsing incrementiel (0 = debut)
    :return: Tuple (figure, last_line) - Figure et numero de derniere ligne lue
    """
    if not os.path.exists(filepath):
        print(f"[PLOTTER_ROTATION] Erreur : Le fichier '{filepath}' n'existe pas !")
        return None, 0

    if start_line > 0:
        print(f"[PLOTTER_ROTATION] Parsing incrementiel du fichier : {filepath} (depuis ligne {start_line})")
    else:
        print(f"[PLOTTER_ROTATION] Parsing du fichier : {filepath}")

    # Parser les donnees
    time_data, target_data, actual_data, last_line = parse_rotation_log(filepath, start_line=start_line)

    if not time_data:
        print("[PLOTTER_ROTATION] Aucune donnee trouvee dans le fichier !")
        return None, last_line

    # Afficher le graphique
    log_filename = os.path.basename(filepath)
    figure = plot_rotation_data(time_data, target_data, actual_data, log_filename,
                               save_png=save_png, show_plot=show_plot)

    return figure, last_line


def plot_last_log(save_png=False, show_plot=True):
    """
    Trouve et plot automatiquement le dernier fichier log cree.

    Utilise pour l'auto-plot apres un mouvement de debug rotation.
    Supporte le parsing incrementiel : si le meme fichier a deja ete parse,
    seules les nouvelles donnees sont parsees.

    :param save_png: Si True, sauvegarde le graphique en PNG
    :param show_plot: Si True, affiche le graphique (plt.show())
    :return: Figure creee
    """
    import debug  # Import pour acceder aux bookmarks

    latest_log = find_latest_log()

    if latest_log is None:
        print("[PLOTTER_ROTATION] Impossible de trouver un fichier log a afficher !")
        return None

    # Verifier si on a deja parse ce fichier (bookmark existe)
    start_line = debug.log_bookmarks.get(latest_log, 0)

    # Parser (incrementiel si bookmark existe)
    figure, last_line = plot_log_file(latest_log, save_png=save_png, show_plot=show_plot,
                                     start_line=start_line)

    # Sauvegarder la position pour le prochain parsing
    debug.log_bookmarks[latest_log] = last_line

    return figure
