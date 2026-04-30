#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de plotting automatique pour les logs UART de debug translation.

Utilise matplotlib avec backend TkAgg pour affichage via VNC.
Reutilise la logique de tests_unitaires/plot_uart_translation.py.

Usage:
    import debug.plotter as plotter

    # Plot le dernier log automatiquement
    plotter.plot_last_log()

    # Plot un fichier specifique
    plotter.plot_log_file("log/2026-04-28_12:34:56:789/log_123456.txt")
"""

import os
import re
import glob
from collections import defaultdict
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
        print(f"[PLOTTER] Le dossier '{log_dir}' n'existe pas !")
        return None

    # Trouver tous les dossiers de logs (format YYYY-MM-DD_HH:MM:SS:mmm)
    log_folders = glob.glob(os.path.join(log_dir, "*"))
    log_folders = [f for f in log_folders if os.path.isdir(f)]

    if not log_folders:
        print(f"[PLOTTER] Aucun dossier de log trouve dans '{log_dir}' !")
        return None

    # Trier par date de modification (le plus recent en premier)
    log_folders.sort(key=os.path.getmtime, reverse=True)
    latest_folder = log_folders[0]

    # Trouver tous les fichiers log_*.txt dans le dossier le plus recent
    log_files = glob.glob(os.path.join(latest_folder, "log_*.txt"))

    if not log_files:
        print(f"[PLOTTER] Aucun fichier log trouve dans '{latest_folder}' !")
        return None

    # Trier par taille de fichier (le plus gros en premier)
    # Le fichier avec les logs UART de debug translation est toujours le plus volumineux
    log_files.sort(key=os.path.getsize, reverse=True)
    latest_log = log_files[0]

    return latest_log


def parse_uart_translation_log(filepath, start_line=0):
    """
    Parse un fichier log UART de debug translation.

    Detecte automatiquement les zones:
    - Global (variables avant tout marqueur)
    - __BEGIN_PID_TRANSLATION__ / __END_PID_TRANSLATION__
    - __BEGIN_PID_ROTATION__ / __END_PID_ROTATION__
    - __BEGIN_RPM__ / __END_RPM__
    - __BEGIN_PID_VITESSE_MOT_R__ / __END_PID_VITESSE_MOT_R__
    - __BEGIN_PID_VITESSE_MOT_L__ / __END_PID_VITESSE_MOT_L__

    :param filepath: Chemin vers le fichier log
    :param start_line: Ligne de depart (0 = debut du fichier). Permet de ne parser que les nouvelles donnees.
    :return: Tuple (data, last_line_number) - Dictionnaire de donnees et numero de la derniere ligne lue
    """
    data = defaultdict(lambda: {'time': [], 'values': []})

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)

    def clean_line(line):
        """
        Nettoie une ligne en enlevant les marqueurs de log UART parasites.
        Exemple: ">> [INFO] [timestamp] [UART_ASSERV] : P =9.490"
        devient: "P =9.490"
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
            current_zone = 'Global'  # Peut etre: Global, Translation, Rotation, RPM, MotR, MotL

            # Parser toutes les lignes jusqu'a __END_LOOP__
            i += 1

            while i < len(lines):
                raw_line = lines[i].strip()
                line = clean_line(raw_line)

                # Detection de la fin de la boucle
                if '__END_LOOP__' in line:
                    break

                # Detection du temps (axe X)
                time_match = re.search(r'\btime_in_sec\s*=\s*([\d.]+)', line)
                if time_match:
                    current_time = float(time_match.group(1))

                # Detection des zones PID
                if '__BEGIN_PID_TRANSLATION__' in line:
                    current_zone = 'Translation'
                    i += 1
                    continue
                elif '__END_PID_TRANSLATION__' in line:
                    current_zone = 'Global'
                    i += 1
                    continue
                elif '__BEGIN_PID_ROTATION__' in line:
                    current_zone = 'Rotation'
                    i += 1
                    continue
                elif '__END_PID_ROTATION__' in line:
                    current_zone = 'Global'
                    i += 1
                    continue
                elif '__BEGIN_RPM__' in line:
                    current_zone = 'RPM'
                    i += 1
                    continue
                elif '__END_RPM__' in line:
                    current_zone = 'Global'
                    i += 1
                    continue
                elif '__BEGIN_PID_VITESSE_MOT_R__' in line:
                    current_zone = 'MotR'
                    i += 1
                    continue
                elif '__END_PID_VITESSE_MOT_R__' in line:
                    current_zone = 'Global'
                    i += 1
                    continue
                elif '__BEGIN_PID_VITESSE_MOT_L__' in line:
                    current_zone = 'MotL'
                    i += 1
                    continue
                elif '__END_PID_VITESSE_MOT_L__' in line:
                    current_zone = 'Global'
                    i += 1
                    continue

                # Parser TOUTES les variables au format "nom = valeur"
                # Regex pour capturer nom = valeur (avec espaces autour du =)
                # \w+ accepte les noms de 1+ caracteres (incluant P, I, D)
                var_matches = re.findall(r'\b(\w+)\s*=\s*([+-]?[\d.]+)', line)

                for var_name, var_value in var_matches:
                    # Ignorer la variable "time_in_sec" (deja traitee separement)
                    if var_name == 'time_in_sec':
                        continue

                    try:
                        value = float(var_value)

                        # Creer une cle avec prefixe selon la zone
                        if current_zone == 'Global' or current_zone == 'RPM':
                            key = var_name
                        else:
                            # Prefixer les variables P, I, D, pid_out selon la zone
                            key = f"{current_zone}_{var_name}"

                        # Stocker la valeur avec le timestamp
                        if current_time is not None:
                            data[key]['time'].append(current_time)
                            data[key]['values'].append(value)

                    except ValueError:
                        pass  # Ignorer les valeurs non numeriques

                i += 1

        i += 1

    # Retourner les donnees et le numero de la derniere ligne lue
    return data, total_lines


def plot_translation_data(data, log_filename, save_png=False, show_plot=True, plot_mode='all'):
    """
    Affiche 6 graphiques separes avec legendes interactives cliquables :
    1. Variables globales (position, consigne)
    2. PID Translation
    3. PID Rotation
    4. RPM (targets + mesures)
    5. PID Vitesse Moteur R
    6. PID Vitesse Moteur L

    :param data: Dictionnaire de donnees retourne par parse_uart_translation_log()
    :param log_filename: Nom du fichier log (pour le titre)
    :param save_png: Si True, sauvegarde les graphiques en PNG
    :param show_plot: Si True, affiche les graphiques (plt.show())
    :param plot_mode: Mode de plot - 'all' (tous les 6), 'essential' (Global + RPM uniquement)
    :return: Liste des figures creees
    """
    if not data:
        print("[PLOTTER] Aucune donnee a afficher !")
        return []

    # Filtrer les variables qui ont moins de 50 points (probablement des parasites)
    MIN_POINTS = 50
    data_filtered = {k: v for k, v in data.items() if len(v['time']) >= MIN_POINTS}

    if not data_filtered:
        print(f"[PLOTTER] Aucune donnee valide a afficher (toutes les variables ont moins de {MIN_POINTS} points) !")
        return []

    # Separer les donnees en 6 categories
    data_global = {k: v for k, v in data_filtered.items()
                   if not k.startswith('Translation_')
                   and not k.startswith('Rotation_')
                   and not k.startswith('MotR_')
                   and not k.startswith('MotL_')
                   and k not in ['motor_r_rpm_target', 'motor_l_rpm_target', 'current_rpm_R', 'current_rpm_L']}

    data_translation = {k.replace('Translation_', ''): v for k, v in data_filtered.items() if k.startswith('Translation_')}
    data_rotation = {k.replace('Rotation_', ''): v for k, v in data_filtered.items() if k.startswith('Rotation_')}

    data_rpm = {k: v for k, v in data_filtered.items()
                if k in ['motor_r_rpm_target', 'motor_l_rpm_target', 'current_rpm_R', 'current_rpm_L']}

    data_mot_r = {k.replace('MotR_', ''): v for k, v in data_filtered.items() if k.startswith('MotR_')}
    data_mot_l = {k.replace('MotL_', ''): v for k, v in data_filtered.items() if k.startswith('MotL_')}

    # Couleurs pour differencier les courbes
    colors = plt.cm.tab20.colors  # 20 couleurs differentes

    figures = []

    def create_subplot(data_dict, title, fig_number):
        """Cree un graphique interactif pour un ensemble de donnees"""
        if not data_dict:
            return None

        fig, ax = plt.subplots(figsize=(14, 8), num=fig_number)
        lines = []

        # Tracer toutes les courbes
        for i, (var_name, values) in enumerate(sorted(data_dict.items())):
            time = values['time']
            vals = values['values']

            color = colors[i % len(colors)]
            line, = ax.plot(time, vals, label=var_name, color=color, linewidth=1.5, marker='o', markersize=2)
            lines.append(line)

        # Configuration de la legende interactive
        leg = ax.legend(loc='upper left', fontsize=8, ncol=2)

        # Rendre la legende interactive (cliquer pour masquer/afficher)
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
        ax.set_xlabel('Temps (s)', fontsize=12)
        ax.set_ylabel('Valeur', fontsize=12)
        ax.set_title(f'{title} - {log_filename}\n(Cliquer sur la legende pour masquer/afficher les courbes)', fontsize=14)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    # Creer les graphiques selon le mode choisi
    if plot_mode == 'essential':
        print(f"[PLOTTER] Mode ESSENTIAL - Creation de 2 graphiques pour {log_filename}")

        # Mode essential : uniquement Global + RPM (les plus importants)
        fig1 = create_subplot(data_global, "Variables globales (Position & Consigne)", 1)
        if fig1:
            figures.append(fig1)

        fig4 = create_subplot(data_rpm, "RPM (Targets & Current)", 4)
        if fig4:
            figures.append(fig4)

    else:  # plot_mode == 'all'
        print(f"[PLOTTER] Mode ALL - Creation de 6 graphiques pour {log_filename}")

        # Mode all : tous les 6 graphiques
        fig1 = create_subplot(data_global, "Variables globales (Position & Consigne)", 1)
        if fig1:
            figures.append(fig1)

        fig2 = create_subplot(data_translation, "PID Translation", 2)
        if fig2:
            figures.append(fig2)

        fig3 = create_subplot(data_rotation, "PID Rotation", 3)
        if fig3:
            figures.append(fig3)

        fig4 = create_subplot(data_rpm, "RPM (Targets & Current)", 4)
        if fig4:
            figures.append(fig4)

        fig5 = create_subplot(data_mot_r, "PID Vitesse Moteur Right", 5)
        if fig5:
            figures.append(fig5)

        fig6 = create_subplot(data_mot_l, "PID Vitesse Moteur Left", 6)
        if fig6:
            figures.append(fig6)

    # Sauvegarder en PNG si demande
    if save_png and figures:
        base_output = log_filename.replace('.txt', '')
        titles = ['global', 'pid_translation', 'pid_rotation', 'rpm', 'pid_motor_r', 'pid_motor_l']

        for i, fig in enumerate(figures):
            output_file = f"{base_output}_plot_{titles[i]}.png"
            fig.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"[PLOTTER] Graphique sauvegarde : {output_file}")

    # Afficher les graphiques
    if show_plot and figures:
        print(f"[PLOTTER] {len(figures)} graphique(s) affiches ! Cliquez sur les legendes pour masquer/afficher les courbes.")
        plt.show()

    return figures


def plot_log_file(filepath, save_png=False, show_plot=True, plot_mode='all', start_line=0):
    """
    Parse et plot un fichier log specifique.

    :param filepath: Chemin vers le fichier log
    :param save_png: Si True, sauvegarde les graphiques en PNG
    :param show_plot: Si True, affiche les graphiques (plt.show())
    :param plot_mode: Mode de plot - 'all' (tous les 6), 'essential' (Global + RPM uniquement)
    :param start_line: Ligne de depart pour parsing incrementiel (0 = debut)
    :return: Tuple (figures, last_line) - Liste des figures et numero de derniere ligne lue
    """
    if not os.path.exists(filepath):
        print(f"[PLOTTER] Erreur : Le fichier '{filepath}' n'existe pas !")
        return [], 0

    if start_line > 0:
        print(f"[PLOTTER] Parsing incrementiel du fichier : {filepath} (depuis ligne {start_line})")
    else:
        print(f"[PLOTTER] Parsing du fichier : {filepath}")

    # Parser les donnees
    data, last_line = parse_uart_translation_log(filepath, start_line=start_line)

    if not data:
        print("[PLOTTER] Aucune donnee trouvee dans le fichier !")
        return [], last_line

    # Afficher les graphiques
    log_filename = os.path.basename(filepath)
    figures = plot_translation_data(data, log_filename, save_png=save_png, show_plot=show_plot, plot_mode=plot_mode)

    return figures, last_line


def plot_last_log(save_png=False, show_plot=True, plot_mode='all'):
    """
    Trouve et plot automatiquement le dernier fichier log cree.

    Utilise pour l'auto-plot apres un mouvement de debug.
    Supporte le parsing incrementiel : si le meme fichier a deja ete parse,
    seules les nouvelles donnees sont parsees.

    :param save_png: Si True, sauvegarde les graphiques en PNG
    :param show_plot: Si True, affiche les graphiques (plt.show())
    :param plot_mode: Mode de plot - 'all' (tous les 6), 'essential' (Global + RPM uniquement)
    :return: Liste des figures creees
    """
    import debug  # Import pour acceder aux bookmarks

    latest_log = find_latest_log()

    if latest_log is None:
        print("[PLOTTER] Impossible de trouver un fichier log a afficher !")
        return []

    # Verifier si on a deja parse ce fichier (bookmark existe)
    start_line = debug.log_bookmarks.get(latest_log, 0)

    # Parser (incrementiel si bookmark existe)
    figures, last_line = plot_log_file(latest_log, save_png=save_png, show_plot=show_plot,
                                       plot_mode=plot_mode, start_line=start_line)

    # Sauvegarder la position pour le prochain parsing
    debug.log_bookmarks[latest_log] = last_line

    return figures
