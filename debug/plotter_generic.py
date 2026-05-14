#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de plotting générique pour les logs UART de debug (rotation ET translation).

Affiche 4 graphiques :
1. Position : consigne vs mesure (target vs actual)
2. Vitesse : RPM moteurs (consignes et mesures pour L et R)
3. PID Position : P, I, D, FF, out du PID rotation/translation
4. PID Vitesse : P, I, D, FF, out du PID vitesse moteur

Adapté pour le nouveau code C générique avec debug PID.

Usage:
    import debug.plotter_generic as plotter_generic

    # Plot le dernier log automatiquement
    plotter_generic.plot_last_log()

    # Plot un fichier specifique
    plotter_generic.plot_log_file("log/2026-04-28_12:34:56:789/log_123456.txt")
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

    :return: Chemin vers le dernier fichier log, ou None si aucun trouve
    """
    log_dir = "log"

    if not os.path.exists(log_dir):
        print(f"[PLOTTER_GENERIC] Le dossier '{log_dir}' n'existe pas !")
        return None

    log_folders = glob.glob(os.path.join(log_dir, "*"))
    log_folders = [f for f in log_folders if os.path.isdir(f)]

    if not log_folders:
        print(f"[PLOTTER_GENERIC] Aucun dossier de log trouve dans '{log_dir}' !")
        return None

    log_folders.sort(key=os.path.getmtime, reverse=True)
    latest_folder = log_folders[0]

    log_files = glob.glob(os.path.join(latest_folder, "log_*.txt"))

    if not log_files:
        print(f"[PLOTTER_GENERIC] Aucun fichier log trouve dans '{latest_folder}' !")
        return None

    log_files.sort(key=os.path.getsize, reverse=True)
    latest_log = log_files[0]

    return latest_log


def parse_generic_log(filepath, start_line=0):
    """
    Parse un fichier log UART de debug (rotation ou translation).

    Extrait les variables generiques du nouveau code C avec PID debug:
    - T, target, actual (position)
    - rpm_r_target, rpm_r, rpm_l_target, rpm_l (vitesse)
    - P, I, D, FF, out (PID position - 1er ensemble)
    - P, I, D, FF, out (PID vitesse - 2eme ensemble)

    :param filepath: Chemin vers le fichier log
    :param start_line: Ligne de depart (0 = debut du fichier)
    :return: Tuple (time_data, target_data, actual_data, rpm_r_target_data, rpm_r_data,
                   rpm_l_target_data, rpm_l_data, pid_pos_p, pid_pos_i, pid_pos_d,
                   pid_pos_ff, pid_pos_out, pid_vel_p, pid_vel_i, pid_vel_d, pid_vel_ff,
                   pid_vel_out, last_line_number)
    """
    time_data = []
    target_data = []
    actual_data = []
    rpm_r_target_data = []
    rpm_r_data = []
    rpm_l_target_data = []
    rpm_l_data = []

    # PID Position (rotation ou translation)
    pid_pos_p = []
    pid_pos_i = []
    pid_pos_d = []
    pid_pos_ff = []
    pid_pos_out = []

    # PID Vitesse (moteur)
    pid_vel_p = []
    pid_vel_i = []
    pid_vel_d = []
    pid_vel_ff = []
    pid_vel_out = []

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)

    def clean_line(line):
        """Nettoie une ligne en enlevant les marqueurs de log UART parasites."""
        line = re.sub(r'^>>\s*\[INFO\]\s*\[.*?\]\s*\[.*?\]\s*\[UART_ASSERV\]\s*:\s*', '', line)
        return line.strip()

    # Commencer a la ligne start_line
    i = start_line
    while i < len(lines):
        raw_line = lines[i].strip()
        line = clean_line(raw_line)

        # Detection du debut d'une boucle
        if '__START_LOOP__' in line:
            current_time = None
            current_target = None
            current_actual = None
            current_rpm_r_target = None
            current_rpm_r = None
            current_rpm_l_target = None
            current_rpm_l = None

            # PID Position (premier ensemble P, I, D, FF, out rencontre)
            pid_pos_p_val = None
            pid_pos_i_val = None
            pid_pos_d_val = None
            pid_pos_ff_val = None
            pid_pos_out_val = None

            # PID Vitesse (deuxieme ensemble P, I, D, FF, out rencontre)
            pid_vel_p_val = None
            pid_vel_i_val = None
            pid_vel_d_val = None
            pid_vel_ff_val = None
            pid_vel_out_val = None

            # Flag pour savoir si on a deja vu un ensemble PID (position)
            first_pid_seen = False

            # Parser toutes les lignes jusqu'a __END_LOOP__
            i += 1

            while i < len(lines):
                raw_line = lines[i].strip()
                line = clean_line(raw_line)

                # Detection de la fin de la boucle
                if '__END_LOOP__' in line:
                    # Enregistrer les donnees si au moins temps + position sont presentes
                    if current_time is not None and current_target is not None and current_actual is not None:
                        time_data.append(current_time)
                        target_data.append(current_target)
                        actual_data.append(current_actual)

                        # RPM sont optionnels
                        rpm_r_target_data.append(current_rpm_r_target if current_rpm_r_target is not None else 0)
                        rpm_r_data.append(current_rpm_r if current_rpm_r is not None else 0)
                        rpm_l_target_data.append(current_rpm_l_target if current_rpm_l_target is not None else 0)
                        rpm_l_data.append(current_rpm_l if current_rpm_l is not None else 0)

                        # PID Position
                        pid_pos_p.append(pid_pos_p_val if pid_pos_p_val is not None else 0)
                        pid_pos_i.append(pid_pos_i_val if pid_pos_i_val is not None else 0)
                        pid_pos_d.append(pid_pos_d_val if pid_pos_d_val is not None else 0)
                        pid_pos_ff.append(pid_pos_ff_val if pid_pos_ff_val is not None else 0)
                        pid_pos_out.append(pid_pos_out_val if pid_pos_out_val is not None else 0)

                        # PID Vitesse
                        pid_vel_p.append(pid_vel_p_val if pid_vel_p_val is not None else 0)
                        pid_vel_i.append(pid_vel_i_val if pid_vel_i_val is not None else 0)
                        pid_vel_d.append(pid_vel_d_val if pid_vel_d_val is not None else 0)
                        pid_vel_ff.append(pid_vel_ff_val if pid_vel_ff_val is not None else 0)
                        pid_vel_out.append(pid_vel_out_val if pid_vel_out_val is not None else 0)
                    break

                # Parser les variables de position
                time_match = re.search(r'\bT\s*=\s*([\d.]+)', line)
                if time_match:
                    current_time = float(time_match.group(1))

                target_match = re.search(r'\btarget\s*=\s*([+-]?[\d.]+)', line)
                if target_match:
                    current_target = float(target_match.group(1))

                actual_match = re.search(r'\bactual\s*=\s*([+-]?[\d.]+)', line)
                if actual_match:
                    current_actual = float(actual_match.group(1))

                # Parser les variables RPM
                rpm_r_target_match = re.search(r'\brpm_r_target\s*=\s*([+-]?[\d.]+)', line)
                if rpm_r_target_match:
                    current_rpm_r_target = float(rpm_r_target_match.group(1))

                rpm_r_match = re.search(r'\brpm_r\s*=\s*([+-]?[\d.]+)', line)
                if rpm_r_match:
                    current_rpm_r = float(rpm_r_match.group(1))

                rpm_l_target_match = re.search(r'\brpm_l_target\s*=\s*([+-]?[\d.]+)', line)
                if rpm_l_target_match:
                    current_rpm_l_target = float(rpm_l_target_match.group(1))

                rpm_l_match = re.search(r'\brpm_l\s*=\s*([+-]?[\d.]+)', line)
                if rpm_l_match:
                    current_rpm_l = float(rpm_l_match.group(1))

                # Parser les variables PID (format: "P =XXX I =XXX D =XXX FF =XXX out=XXX")
                # Cette ligne peut apparaitre 2 fois : PID position puis PID vitesse
                # On detecte les 5 valeurs sur la meme ligne
                p_match = re.search(r'\bP\s*=([+-]?[\d.]+)', line)
                i_match = re.search(r'\bI\s*=([+-]?[\d.]+)', line)
                d_match = re.search(r'\bD\s*=([+-]?[\d.]+)', line)
                ff_match = re.search(r'\bFF\s*=([+-]?[\d.]+)', line)
                out_match = re.search(r'\bout\s*=([+-]?[\d.]+)', line)

                # Si on detecte au moins P, I, D, c'est une ligne PID
                if p_match and i_match and d_match:
                    p_val = float(p_match.group(1))
                    i_val = float(i_match.group(1))
                    d_val = float(d_match.group(1))
                    ff_val = float(ff_match.group(1)) if ff_match else 0
                    out_val = float(out_match.group(1)) if out_match else 0

                    # Premier PID rencontre = PID Position
                    if not first_pid_seen:
                        pid_pos_p_val = p_val
                        pid_pos_i_val = i_val
                        pid_pos_d_val = d_val
                        pid_pos_ff_val = ff_val
                        pid_pos_out_val = out_val
                        first_pid_seen = True
                    # Deuxieme PID rencontre = PID Vitesse
                    else:
                        pid_vel_p_val = p_val
                        pid_vel_i_val = i_val
                        pid_vel_d_val = d_val
                        pid_vel_ff_val = ff_val
                        pid_vel_out_val = out_val

                i += 1

        i += 1

    # Retourner toutes les donnees
    return (time_data, target_data, actual_data, rpm_r_target_data, rpm_r_data,
            rpm_l_target_data, rpm_l_data, pid_pos_p, pid_pos_i, pid_pos_d,
            pid_pos_ff, pid_pos_out, pid_vel_p, pid_vel_i, pid_vel_d, pid_vel_ff,
            pid_vel_out, total_lines)


def plot_generic_data(time_data, target_data, actual_data, rpm_r_target_data, rpm_r_data,
                     rpm_l_target_data, rpm_l_data, pid_pos_p, pid_pos_i, pid_pos_d,
                     pid_pos_ff, pid_pos_out, pid_vel_p, pid_vel_i, pid_vel_d, pid_vel_ff,
                     pid_vel_out, log_filename, save_png=False, show_plot=True):
    """
    Affiche 4 graphiques :
    1. Position : consigne vs mesure
    2. Vitesse : RPM moteurs (L et R, consignes et mesures)
    3. PID Position : P, I, D, FF, out
    4. PID Vitesse : P, I, D, FF, out

    Returns: Figure creee
    """
    if not time_data or not target_data or not actual_data:
        print("[PLOTTER_GENERIC] Aucune donnee a afficher !")
        return None

    if len(time_data) < 10:
        print(f"[PLOTTER_GENERIC] Trop peu de donnees ({len(time_data)} points). Minimum 10 requis.")
        return None

    # Detecter le type de mouvement (rotation ou translation) selon l'ordre de grandeur
    avg_value = sum([abs(v) for v in target_data]) / len(target_data)
    if avg_value > 100:
        movement_type = "Translation"
        unit = "mm"
    else:
        movement_type = "Rotation"
        unit = "deg"

    # Creer une figure avec 4 sous-graphiques (2x2)
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    # ========== GRAPHIQUE 1 : POSITION ==========
    ax1.plot(time_data, target_data, label='Consigne (target)',
            color='blue', linewidth=2, linestyle='--')
    ax1.plot(time_data, actual_data, label='Mesure (actual)',
            color='red', linewidth=2, marker='o', markersize=2)

    # Calculer l'erreur finale
    if len(target_data) > 0 and len(actual_data) > 0:
        final_error = abs(target_data[-1] - actual_data[-1])
        ax1.text(0.02, 0.98, f'Erreur finale: {final_error:.2f}{unit}',
                transform=ax1.transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax1.set_xlabel('Temps (s)', fontsize=11)
    ax1.set_ylabel(f'Position ({unit})', fontsize=11)
    ax1.set_title(f'{movement_type} - Position (Consigne vs Mesure)',
                 fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left', fontsize=9)

    # ========== GRAPHIQUE 2 : VITESSE (RPM) ==========
    ax2.plot(time_data, rpm_r_target_data, label='Consigne RPM Right',
            color='blue', linewidth=2, linestyle='--')
    ax2.plot(time_data, rpm_r_data, label='Mesure RPM Right',
            color='blue', linewidth=1.5, marker='o', markersize=1)
    ax2.plot(time_data, rpm_l_target_data, label='Consigne RPM Left',
            color='red', linewidth=2, linestyle='--')
    ax2.plot(time_data, rpm_l_data, label='Mesure RPM Left',
            color='red', linewidth=1.5, marker='o', markersize=1)

    ax2.set_xlabel('Temps (s)', fontsize=11)
    ax2.set_ylabel('Vitesse (RPM)', fontsize=11)
    ax2.set_title('Vitesse Moteurs - RPM', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper left', fontsize=9)

    # ========== GRAPHIQUE 3 : PID POSITION ==========
    ax3.plot(time_data, pid_pos_p, label='P (Proportionnel)',
            color='red', linewidth=1.5)
    ax3.plot(time_data, pid_pos_i, label='I (Intégral)',
            color='green', linewidth=1.5)
    ax3.plot(time_data, pid_pos_d, label='D (Dérivé)',
            color='blue', linewidth=1.5)
    ax3.plot(time_data, pid_pos_ff, label='FF (Feedforward)',
            color='orange', linewidth=1.5)
    ax3.plot(time_data, pid_pos_out, label='Out (Sortie)',
            color='purple', linewidth=2, linestyle='--')

    ax3.set_xlabel('Temps (s)', fontsize=11)
    ax3.set_ylabel('Valeur', fontsize=11)
    ax3.set_title(f'PID {movement_type} - Termes P, I, D, FF, Out', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='upper left', fontsize=9)

    # ========== GRAPHIQUE 4 : PID VITESSE ==========
    ax4.plot(time_data, pid_vel_p, label='P (Proportionnel)',
            color='red', linewidth=1.5)
    ax4.plot(time_data, pid_vel_i, label='I (Intégral)',
            color='green', linewidth=1.5)
    ax4.plot(time_data, pid_vel_d, label='D (Dérivé)',
            color='blue', linewidth=1.5)
    ax4.plot(time_data, pid_vel_ff, label='FF (Feedforward)',
            color='orange', linewidth=1.5)
    ax4.plot(time_data, pid_vel_out, label='Out (Sortie)',
            color='purple', linewidth=2, linestyle='--')

    ax4.set_xlabel('Temps (s)', fontsize=11)
    ax4.set_ylabel('Valeur', fontsize=11)
    ax4.set_title('PID Vitesse Moteur Right - Termes P, I, D, FF, Out', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend(loc='upper left', fontsize=9)

    plt.suptitle(f'Debug {movement_type} - {log_filename}', fontsize=14, fontweight='bold')
    plt.tight_layout()

    # Sauvegarder en PNG si demande
    if save_png:
        output_file = log_filename.replace('.txt', '_debug.png')
        fig.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"[PLOTTER_GENERIC] Graphiques sauvegardes : {output_file}")

    # Afficher les graphiques
    if show_plot:
        print(f"[PLOTTER_GENERIC] {len(time_data)} points traces. Type detecte: {movement_type}")
        plt.show()

    return fig


def plot_log_file(filepath, save_png=False, show_plot=True, start_line=0):
    """
    Parse et plot un fichier log specifique.

    :return: Tuple (figure, last_line) - Figure et numero de derniere ligne lue
    """
    if not os.path.exists(filepath):
        print(f"[PLOTTER_GENERIC] Erreur : Le fichier '{filepath}' n'existe pas !")
        return None, 0

    if start_line > 0:
        print(f"[PLOTTER_GENERIC] Parsing incrementiel du fichier : {filepath} (depuis ligne {start_line})")
    else:
        print(f"[PLOTTER_GENERIC] Parsing du fichier : {filepath}")

    # Parser les donnees
    (time_data, target_data, actual_data, rpm_r_target_data, rpm_r_data,
     rpm_l_target_data, rpm_l_data, pid_pos_p, pid_pos_i, pid_pos_d,
     pid_pos_ff, pid_pos_out, pid_vel_p, pid_vel_i, pid_vel_d, pid_vel_ff,
     pid_vel_out, last_line) = parse_generic_log(filepath, start_line=start_line)

    if not time_data:
        print("[PLOTTER_GENERIC] Aucune donnee trouvee dans le fichier !")
        return None, last_line

    # Afficher les graphiques
    log_filename = os.path.basename(filepath)
    figure = plot_generic_data(time_data, target_data, actual_data, rpm_r_target_data, rpm_r_data,
                              rpm_l_target_data, rpm_l_data, pid_pos_p, pid_pos_i, pid_pos_d,
                              pid_pos_ff, pid_pos_out, pid_vel_p, pid_vel_i, pid_vel_d, pid_vel_ff,
                              pid_vel_out, log_filename, save_png=save_png, show_plot=show_plot)

    return figure, last_line


def plot_last_log(save_png=False, show_plot=True):
    """
    Trouve et plot automatiquement le dernier fichier log cree.

    :return: Figure creee
    """
    import debug  # Import pour acceder aux bookmarks

    latest_log = find_latest_log()

    if latest_log is None:
        print("[PLOTTER_GENERIC] Impossible de trouver un fichier log a afficher !")
        return None

    # Verifier si on a deja parse ce fichier (bookmark existe)
    start_line = debug.log_bookmarks.get(latest_log, 0)

    # Parser (incrementiel si bookmark existe)
    figure, last_line = plot_log_file(latest_log, save_png=save_png, show_plot=show_plot,
                                     start_line=start_line)

    # Sauvegarder la position pour le prochain parsing
    debug.log_bookmarks[latest_log] = last_line

    return figure
