##!/usr/bin/env python3
"""
Script pour parser les logs UART de debug TRANSLATION et afficher des graphiques interactifs.

Usage:
    python plot_uart_translation.py <fichier_log.txt>
    python plot_uart_translation.py  # demande le fichier interactivement

Fonctionnalites:
- Parsing automatique des variables de debug translation
- Detection des zones PID (Translation, Rotation, Vitesse Moteur R/L)
- 6 graphiques separes avec legendes cliquables
- Utilise time_in_sec comme axe X
- Sauvegarde optionnelle en PNG
"""

import sys
import re
import os
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')  # Backend interactif


def parse_uart_translation_log(filepath):
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
    :return: Dictionnaire {variable_name: {'time': [], 'values': []}}
    """
    data = defaultdict(lambda: {'time': [], 'values': []})

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    def clean_line(line):
        """
        Nettoie une ligne en enlevant les marqueurs de log UART parasites.
        Exemple: ">> [INFO] [timestamp] [UART_ASSERV] : P =9.490"
        devient: "P =9.490"
        """
        # Enlever le prefixe >> [INFO] [timestamp] [UART_ASSERV] :
        line = re.sub(r'^>>\s*\[INFO\]\s*\[.*?\]\s*\[.*?\]\s*\[UART_ASSERV\]\s*:\s*', '', line)
        return line.strip()

    i = 0
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
                # \w+ accepte les noms de 1+ caractères (incluant P, I, D)
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

    return data


def plot_translation_data(data, log_filename):
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
    :return: Liste des figures creees
    """
    if not data:
        print("❌ Aucune donnee a afficher !")
        return []

    # Filtrer les variables qui ont moins de 50 points (probablement des parasites)
    MIN_POINTS = 50
    data_filtered = {k: v for k, v in data.items() if len(v['time']) >= MIN_POINTS}

    if not data_filtered:
        print(f"❌ Aucune donnee valide a afficher (toutes les variables ont moins de {MIN_POINTS} points) !")
        print("Variables rejetees :")
        for var_name, values in sorted(data.items()):
            print(f"   - {var_name} : {len(values['time'])} points (< {MIN_POINTS})")
        return []

    # Afficher les variables rejetees pour info
    rejected = {k: v for k, v in data.items() if len(v['time']) < MIN_POINTS}
    if rejected:
        print(f"\n⚠️  Variables ignorees (moins de {MIN_POINTS} points - probablement des parasites) :")
        for var_name, values in sorted(rejected.items()):
            print(f"   - {var_name} : {len(values['time'])} points")

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
            print(f"⚠️  Aucune donnee pour {title}")
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

    # Creer les 6 graphiques separes
    print(f"\n📊 Creation des graphiques :")
    print(f"   - Variables globales : {len(data_global)} variables")
    print(f"   - PID Translation : {len(data_translation)} variables")
    print(f"   - PID Rotation : {len(data_rotation)} variables")
    print(f"   - RPM : {len(data_rpm)} variables")
    print(f"   - PID Vitesse Moteur R : {len(data_mot_r)} variables")
    print(f"   - PID Vitesse Moteur L : {len(data_mot_l)} variables")

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

    return figures


def main():
    """Point d'entree principal du script"""

    # Gestion des arguments de ligne de commande
    if len(sys.argv) > 1:
        log_file = sys.argv[1]
    else:
        log_file = input("📂 Entrer le chemin du fichier log (ex: log/2026-04-28_12:50:57:496/log_310801.txt): ").strip()

    # Verifier que le fichier existe
    if not os.path.exists(log_file):
        print(f"❌ Erreur : Le fichier '{log_file}' n'existe pas !")
        sys.exit(1)

    print(f"📊 Parsing du fichier : {log_file}")

    # Parser les donnees
    data = parse_uart_translation_log(log_file)

    if not data:
        print("❌ Aucune donnee trouvee dans le fichier !")
        sys.exit(1)

    # Afficher un resume des donnees
    print(f"✅ {len(data)} variables detectees :")
    for var_name, values in sorted(data.items()):
        print(f"   - {var_name} : {len(values['time'])} points")

    # Afficher les graphiques
    log_filename = os.path.basename(log_file)
    figures = plot_translation_data(data, log_filename)

    if not figures:
        print("❌ Aucun graphique a afficher !")
        sys.exit(1)

    print(f"\n📈 {len(figures)} graphique(s) affiche(s) ! Cliquez sur les legendes pour masquer/afficher les courbes.")
    plt.show()

    # Demander si l'utilisateur veut sauvegarder
    save = input("\n💾 Voulez-vous sauvegarder les graphiques en PNG ? (o/n): ").strip().lower()

    if save in ['o', 'oui', 'y', 'yes']:
        # Sauvegarder chaque figure separement
        base_output = log_file.replace('.txt', '')
        titles = ['global', 'pid_translation', 'pid_rotation', 'rpm', 'pid_motor_r', 'pid_motor_l']

        for i, fig in enumerate(figures):
            output_file = f"{base_output}_plot_{titles[i]}.png"
            fig.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✅ Graphique sauvegarde : {output_file}")
    else:
        print("❌ Graphiques non sauvegardes.")


if __name__ == "__main__":
    main()
