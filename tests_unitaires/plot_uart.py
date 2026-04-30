###!/usr/bin/env python3
"""
Script pour parser les logs UART et afficher des graphiques interactifs avec matplotlib.

Usage:
    python plot_uart.py <fichier_log.txt>
    python plot_uart.py  # demande le fichier interactivement

Fonctionnalités:
- Parsing automatique de toutes les variables entre ===LOOP_START=== et ===LOOP_END===
- Graphique interactif avec légende cliquable pour masquer/afficher les courbes
- Différenciation moteur R et L
- Sauvegarde optionnelle en PNG
"""

import sys
import re
import os
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')  # Backend interactif

def parse_uart_log(filepath):
    """
    Parse un fichier log UART et extrait toutes les variables de manière générique.

    Supporte deux formats de délimiteurs :
    - Ancien format : ===LOOP_START=== / ===LOOP_END===
    - Nouveau format : __START_LOOP__ / __END_LOOP__

    Détecte automatiquement les zones moteur :
    - debut config moteur Right: / fin config moteur Right:
    - debut config moteur Left: / fin config moteur Left:

    :param filepath: Chemin vers le fichier log
    :return: Dictionnaire {variable_name: {'time': [], 'values': []}}
    """
    # CLAUDE: Stockage des données par variable
    data = defaultdict(lambda: {'time': [], 'values': []})

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    def clean_line(line):
        """
        CLAUDE: Nettoie une ligne en enlevant les marqueurs de log UART parasites.
        Exemple: ">> [INFO] [timestamp] [UART_ASSERV] : P_contribution =9.490"
        devient: "P_contribution =9.490"
        """
        # Enlever le préfixe >> [INFO] [timestamp] [UART_ASSERV] :
        line = re.sub(r'^>>\s*\[INFO\]\s*\[.*?\]\s*\[.*?\]\s*\[UART_ASSERV\]\s*:\s*', '', line)
        return line.strip()

    i = 0
    while i < len(lines):
        raw_line = lines[i].strip()
        line = clean_line(raw_line)

        # CLAUDE: Détection du début d'une boucle (support des deux formats)
        if '__START_LOOP__' in line or '===LOOP_START===' in line:
            current_time = None
            current_zone = 'global'  # Peut être 'global', 'Right', 'Left'

            # Parser toutes les lignes jusqu'à __END_LOOP__ ou ===LOOP_END===
            i += 1

            while i < len(lines):
                raw_line = lines[i].strip()
                line = clean_line(raw_line)

                # Détection de la fin de la boucle
                if '__END_LOOP__' in line or '===LOOP_END===' in line:
                    break

                # CLAUDE: Détection du temps (peut être sur une ligne séparée)
                time_match = re.search(r'\btime\s*=\s*([\d.]+)', line)
                if time_match:
                    time_ms = float(time_match.group(1))
                    current_time = time_ms / 1000.0  # Convertir en secondes

                # CLAUDE: Détection des zones moteur (Light → Left corrigé)
                if 'debut config moteur Right:' in line or 'debut config moteur R:' in line:
                    current_zone = 'Right'
                    i += 1
                    continue
                elif 'fin config moteur Right:' in line or 'fin config moteur R:' in line:
                    current_zone = 'global'
                    i += 1
                    continue
                elif 'debut config moteur Left:' in line or 'debut config moteur L:' in line:
                    current_zone = 'Left'
                    i += 1
                    continue
                elif 'fin config moteur Left:' in line or 'fin config moteur L:' in line:
                    current_zone = 'global'
                    i += 1
                    continue

                # CLAUDE: Parser TOUTES les variables au format "nom = valeur"
                # Regex pour capturer nom = valeur (avec espaces autour du =)
                # Le nom doit avoir au moins 2 caractères
                var_matches = re.findall(r'\b(\w{2,})\s*=\s*([+-]?[\d.]+%?)', line)

                for var_name, var_value in var_matches:
                    # Ignorer la variable "time" (déjà traitée séparément)
                    if var_name == 'time':
                        continue

                    # Retirer le % si présent pour avoir une valeur numérique
                    var_value_clean = var_value.replace('%', '')

                    try:
                        value = float(var_value_clean)

                        # CLAUDE: Créer une clé avec préfixe selon la zone
                        if current_zone == 'global':
                            key = var_name
                        else:
                            key = f"{current_zone}_{var_name}"

                        # CLAUDE: Stocker la valeur avec le timestamp
                        if current_time is not None:
                            data[key]['time'].append(current_time)
                            data[key]['values'].append(value)

                    except ValueError:
                        pass  # Ignorer les valeurs non numériques

                i += 1

        i += 1

    return data


def plot_data(data, log_filename):
    """
    Affiche 3 graphiques séparés avec légendes interactives cliquables :
    1. Variables globales
    2. Variables moteur Right
    3. Variables moteur Left

    :param data: Dictionnaire de données retourné par parse_uart_log()
    :param log_filename: Nom du fichier log (pour le titre)
    :return: Liste des figures créées
    """
    if not data:
        print("❌ Aucune donnée à afficher !")
        return []

    # CLAUDE: Filtrer les variables qui ont moins de 10 points (probablement des parasites)
    MIN_POINTS = 10
    data_filtered = {k: v for k, v in data.items() if len(v['time']) >= MIN_POINTS}

    if not data_filtered:
        print(f"❌ Aucune donnée valide à afficher (toutes les variables ont moins de {MIN_POINTS} points) !")
        print("Variables rejetées :")
        for var_name, values in sorted(data.items()):
            print(f"   - {var_name} : {len(values['time'])} points (< {MIN_POINTS})")
        return []

    # CLAUDE: Afficher les variables rejetées pour info
    rejected = {k: v for k, v in data.items() if len(v['time']) < MIN_POINTS}
    if rejected:
        print(f"\n⚠️  Variables ignorées (moins de {MIN_POINTS} points - probablement des parasites) :")
        for var_name, values in sorted(rejected.items()):
            print(f"   - {var_name} : {len(values['time'])} points")

    # CLAUDE: Séparer les données en 3 catégories
    data_global = {k: v for k, v in data_filtered.items() if not k.startswith('Right_') and not k.startswith('Left_')}
    data_right = {k.replace('Right_', ''): v for k, v in data_filtered.items() if k.startswith('Right_')}
    data_left = {k.replace('Left_', ''): v for k, v in data_filtered.items() if k.startswith('Left_')}

    # CLAUDE: Couleurs pour différencier les courbes
    colors = plt.cm.tab20.colors  # 20 couleurs différentes

    figures = []

    def create_subplot(data_dict, title, fig_number):
        """Crée un graphique interactif pour un ensemble de données"""
        if not data_dict:
            print(f"⚠️  Aucune donnée pour {title}")
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

        # Configuration de la légende interactive
        leg = ax.legend(loc='upper left', fontsize=8, ncol=2)

        # Rendre la légende interactive (cliquer pour masquer/afficher)
        lined = {}  # Map entre légende et ligne
        for legline, origline in zip(leg.get_lines(), lines):
            legline.set_picker(5)  # Zone cliquable de 5 pixels
            lined[legline] = origline

        def on_pick(event):
            """Callback pour masquer/afficher une courbe quand on clique sur la légende"""
            legline = event.artist
            origline = lined[legline]
            visible = not origline.get_visible()
            origline.set_visible(visible)
            # Changer l'opacité de la légende pour indiquer l'état
            legline.set_alpha(1.0 if visible else 0.2)
            fig.canvas.draw()

        fig.canvas.mpl_connect('pick_event', on_pick)

        # Labels et titre
        ax.set_xlabel('Temps (s)', fontsize=12)
        ax.set_ylabel('Valeur', fontsize=12)
        ax.set_title(f'{title} - {log_filename}\n(Cliquer sur la légende pour masquer/afficher les courbes)', fontsize=14)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    # CLAUDE: Créer les 3 graphiques séparés
    print(f"\n📊 Création des graphiques :")
    print(f"   - Variables globales : {len(data_global)} variables")
    print(f"   - Variables moteur Right : {len(data_right)} variables")
    print(f"   - Variables moteur Left : {len(data_left)} variables")

    fig1 = create_subplot(data_global, "Variables globales", 1)
    if fig1:
        figures.append(fig1)

    fig2 = create_subplot(data_right, "Moteur Right", 2)
    if fig2:
        figures.append(fig2)

    fig3 = create_subplot(data_left, "Moteur Left", 3)
    if fig3:
        figures.append(fig3)

    return figures


def main():
    """Point d'entrée principal du script"""

    # Gestion des arguments de ligne de commande
    if len(sys.argv) > 1:
        log_file = sys.argv[1]
    else:
        log_file = input("📂 Entrer le chemin du fichier log (ex: log/2026-04-22_16:43:05:138/log_34899.txt): ").strip()

    # Vérifier que le fichier existe
    if not os.path.exists(log_file):
        print(f"❌ Erreur : Le fichier '{log_file}' n'existe pas !")
        sys.exit(1)

    print(f"📊 Parsing du fichier : {log_file}")

    # Parser les données
    data = parse_uart_log(log_file)

    if not data:
        print("❌ Aucune donnée trouvée dans le fichier !")
        sys.exit(1)

    # Afficher un résumé des données
    print(f"✅ {len(data)} variables détectées :")
    for var_name, values in sorted(data.items()):
        print(f"   - {var_name} : {len(values['time'])} points")

    # Afficher les graphiques
    log_filename = os.path.basename(log_file)
    figures = plot_data(data, log_filename)

    if not figures:
        print("❌ Aucun graphique à afficher !")
        sys.exit(1)

    print(f"\n📈 {len(figures)} graphique(s) affiché(s) ! Cliquez sur les légendes pour masquer/afficher les courbes.")
    plt.show()

    # Demander si l'utilisateur veut sauvegarder
    save = input("\n💾 Voulez-vous sauvegarder les graphiques en PNG ? (o/n): ").strip().lower()

    if save in ['o', 'oui', 'y', 'yes']:
        # CLAUDE: Sauvegarder chaque figure séparément
        base_output = log_file.replace('.txt', '')
        titles = ['global', 'right', 'left']

        for i, fig in enumerate(figures):
            output_file = f"{base_output}_plot_{titles[i]}.png"
            fig.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✅ Graphique sauvegardé : {output_file}")
    else:
        print("❌ Graphiques non sauvegardés.")


if __name__ == "__main__":
    main()
