'''
Module de génération de chemins pour la navigation du robot (Version 2026)

Ce module implémente un système de pathfinding basé sur l'algorithme A*
avec exclusion de zones carrées autour de l'adversaire.

Principales améliorations par rapport à 2025 :
- Exclusion carrée (500×500mm) au lieu de zones fixes
- Distance euclidienne au lieu de Manhattan
- Architecture modulaire et réutilisable
'''

import math
import heapq
from typing import List, Tuple, Dict, Optional
from strategy.coordonner_strat import (
    POINTS, GRAPH, TARGETS, PRIORITY_ORDER,
    TAS_COORDS,                                                   # claude diane
    TARGETS_DEPOT_CACA,                                           # claude diane
    # DEPOTS_CIRCULAIRE,  # plus utilisé — approche circulaire abandonnée
    ZONES_INTERDITES_TAS, ZONES_INTERDITES_DEPOT,                # claude diane
    # dist_depose, ROBOT_WIDTH, ROBOT_LENGTH, ZONE_INTERDITE,   # plus utilisés (approche circulaire abandonnée)
)


########
### FONCTIONS DE DISTANCE ET GÉOMÉTRIE
########

def dist_euclidean(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calcule la distance euclidienne entre deux points

    Args:
        p1: Premier point (x, y)
        p2: Deuxième point (x, y)

    Returns:
        Distance euclidienne entre p1 et p2
    """
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def is_in_exclusion_square(point: Tuple[float, float], center: Tuple[float, float], size: float = 500) -> bool:
    """
    Vérifie si un point est dans le carré d'exclusion centré sur l'adversaire

    Args:
        point: Point à vérifier (x, y)
        center: Centre du carré (position adversaire) (x, y)
        size: Taille du carré en mm (défaut: 500mm)

    Returns:
        True si le point est dans le carré d'exclusion, False sinon
    """
    half_size = size / 2
    dx = abs(point[0] - center[0])
    dy = abs(point[1] - center[1])

    # Le point est dans le carré si dx <= half_size ET dy <= half_size
    return dx <= half_size and dy <= half_size


########
### GESTION DU GRAPHE
########

# claude diane
def update_graph_depot_zones(graph: Dict[str, List[str]], deposited_zones: List[str]) -> Dict[str, List[str]]:
    """
    Retire du graphe les nœuds situés dans les zones de dépôt déjà utilisées.
    deposited_zones : liste des dépôts où le robot a déjà posé des objets (ex: ['d1', 'd5'])
    """
    nodes_to_remove = set()
    for node_name in list(graph.keys()):
        if node_name not in POINTS:
            continue
        px, py = POINTS[node_name]
        for depot in deposited_zones:
            x_min, x_max, y_min, y_max = ZONES_INTERDITES_DEPOT[depot]
            if x_min <= px <= x_max and y_min <= py <= y_max:
                nodes_to_remove.add(node_name)
                break

    graph_copy = {node: neighbors[:] for node, neighbors in graph.items()}
    for node in nodes_to_remove:
        del graph_copy[node]
    for node in graph_copy:
        graph_copy[node] = [n for n in graph_copy[node] if n not in nodes_to_remove]

    return graph_copy
# claude diane


# début diane
def update_graph_tas_zones(graph: Dict[str, List[str]], available_tas: List[str]) -> Dict[str, List[str]]:
    """
    Retire du graphe les nœuds dont la position est à l'intérieur de la zone
    d'un tas encore disponible (200mm × 150mm autour du centre du tas).
    Un tas ramassé n'est plus une zone interdite.
    """
    nodes_to_remove = set()
    for node_name in list(graph.keys()):
        if node_name not in POINTS:
            continue
        px, py = POINTS[node_name]
        for tas_name in available_tas:
            x_min, x_max, y_min, y_max = ZONES_INTERDITES_TAS[tas_name]
            if x_min <= px <= x_max and y_min <= py <= y_max:
                nodes_to_remove.add(node_name)
                break

    graph_copy = {node: neighbors[:] for node, neighbors in graph.items()}
    for node in nodes_to_remove:
        del graph_copy[node]
    for node in graph_copy:
        graph_copy[node] = [n for n in graph_copy[node] if n not in nodes_to_remove]

    return graph_copy
# fin diane


def update_graph_available_tas(available_tas: List[str]) -> Dict[str, List[str]]:
    """
    Crée une copie du graphe en retirant les nœuds d'approche des tas non disponibles

    Args:
        available_tas: Liste des tas encore disponibles (ex: ['tas_1', 'tas_3', 'tas_4'])

    Returns:
        Graphe modifié sans les nœuds d'approche des tas indisponibles
    """
    # Créer une copie profonde du graphe
    graph_copy = {node: neighbors[:] for node, neighbors in GRAPH.items()}

    # Identifier les tas indisponibles
    all_tas = set(TARGETS.keys())
    unavailable_tas = all_tas - set(available_tas)

    # Pour chaque tas indisponible, retirer ses points d'approche
    nodes_to_remove = set()
    for tas in unavailable_tas:
        approach_points = TARGETS[tas]
        nodes_to_remove.update(approach_points)

    # Retirer les nœuds du graphe
    for node in nodes_to_remove:
        if node in graph_copy:
            del graph_copy[node]

    # Nettoyer les références dans les listes d'adjacence
    for node in graph_copy:
        graph_copy[node] = [neighbor for neighbor in graph_copy[node] if neighbor not in nodes_to_remove]

    return graph_copy


def update_graph_exclusion(graph: Dict[str, List[str]],
                           adversary_pos: Tuple[float, float],
                           robot_pos: Tuple[float, float]) -> Tuple[Dict[str, List[str]], str]:
    """
    Applique l'exclusion carrée autour de l'adversaire et insère la position du robot

    Args:
        graph: Graphe de base (déjà filtré par available_tas)
        adversary_pos: Position de l'adversaire (x, y)
        robot_pos: Position actuelle du robot (x, y)

    Returns:
        Tuple (graphe_modifié, nom_noeud_robot)
        - graphe_modifié: Graphe avec exclusion appliquée et robot inséré
        - nom_noeud_robot: Nom du nœud représentant le robot (ex: 'robot_start')
    """
    # Créer une copie du graphe
    graph_copy = {node: neighbors[:] for node, neighbors in graph.items()}

    # 1. Retirer les nœuds dans la zone d'exclusion
    nodes_to_remove = set()
    for node_name in list(graph_copy.keys()):
        node_pos = POINTS[node_name]
        if is_in_exclusion_square(node_pos, adversary_pos, size=500):
            nodes_to_remove.add(node_name)

    # Retirer les nœuds bloqués
    for node in nodes_to_remove:
        del graph_copy[node]

    # Nettoyer les références
    for node in graph_copy:
        graph_copy[node] = [neighbor for neighbor in graph_copy[node] if neighbor not in nodes_to_remove]

    # 2. Insérer le robot dans le graphe
    robot_node = 'robot_start'

    # Trouver les nœuds à connecter au robot
    # Option 1: Nœuds dans un carré de 200mm autour du robot
    nearby_nodes = []
    for node_name, node_pos in POINTS.items():
        if node_name in graph_copy:  # Seulement les nœuds non bloqués
            dx = abs(node_pos[0] - robot_pos[0])
            dy = abs(node_pos[1] - robot_pos[1])
            if dx <= 200 and dy <= 200:  # Carré de 200×200mm (±100mm)
                nearby_nodes.append(node_name)

    # Option 2: Si aucun nœud proche, prendre le plus proche hors zone d'exclusion
    if not nearby_nodes:
        min_dist = float('inf')
        nearest_node = None
        for node_name, node_pos in POINTS.items():
            if node_name in graph_copy:
                dist = dist_euclidean(robot_pos, node_pos)
                if dist < min_dist:
                    min_dist = dist
                    nearest_node = node_name
        if nearest_node:
            nearby_nodes = [nearest_node]

    # Ajouter le nœud robot au graphe
    graph_copy[robot_node] = nearby_nodes

    # Ajouter les connexions inverses
    for node in nearby_nodes:
        if robot_node not in graph_copy[node]:
            graph_copy[node].append(robot_node)

    return graph_copy, robot_node


########
### ALGORITHME A*
########

def astar(start: str, goal: str, graph: Dict[str, List[str]]) -> Optional[List[str]]:
    """
    Algorithme A* pour trouver le chemin le plus court entre start et goal

    Args:
        start: Nom du nœud de départ
        goal: Nom du nœud d'arrivée
        graph: Graphe avec les connexions entre nœuds

    Returns:
        Liste des noms de nœuds formant le chemin, ou None si aucun chemin trouvé
    """
    # Vérifier que start et goal existent dans le graphe
    if start not in graph or goal not in graph:
        return None

    # Files de priorité : (f_score, node_name)
    open_set = []
    heapq.heappush(open_set, (0, start))

    # Dictionnaires de suivi
    came_from = {}  # Pour reconstruire le chemin
    g_score = {node: float('inf') for node in graph}  # Coût depuis le départ
    g_score[start] = 0

    f_score = {node: float('inf') for node in graph}  # g_score + heuristique
    f_score[start] = dist_euclidean(POINTS.get(start, (0, 0)), POINTS.get(goal, (0, 0)))

    # Ensemble des nœuds déjà visités
    closed_set = set()

    while open_set:
        # Récupérer le nœud avec le plus petit f_score
        current_f, current = heapq.heappop(open_set)

        # Si on a atteint le but, reconstruire le chemin
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        closed_set.add(current)

        # Explorer les voisins
        for neighbor in graph.get(current, []):
            if neighbor in closed_set:
                continue

            # Calculer le g_score tentatif
            current_pos = POINTS.get(current, (0, 0))
            neighbor_pos = POINTS.get(neighbor, (0, 0))
            tentative_g_score = g_score[current] + dist_euclidean(current_pos, neighbor_pos)

            # Si ce chemin est meilleur
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score

                # Calculer f_score avec heuristique euclidienne
                goal_pos = POINTS.get(goal, (0, 0))
                h_score = dist_euclidean(neighbor_pos, goal_pos)
                f_score[neighbor] = tentative_g_score + h_score

                # Ajouter à open_set si pas déjà présent
                if neighbor not in [item[1] for item in open_set]:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    # Aucun chemin trouvé
    return None


########
### SÉLECTION DE CIBLE
########

def select_target_tas(available_tas: List[str], priority_order: List[str] = PRIORITY_ORDER) -> Optional[str]:
    """
    Sélectionne le tas cible selon l'ordre de priorité

    Args:
        available_tas: Liste des tas encore disponibles
        priority_order: Ordre de priorité des tas (défaut: PRIORITY_ORDER)

    Returns:
        Nom du tas sélectionné, ou None si aucun tas disponible
    """
    for tas in priority_order:
        if tas in available_tas:
            return tas
    return None


########
### OPTIMISATION DU CHEMIN
########

def optimize_path(path: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Optimise un chemin en supprimant les points intermédiaires alignés

    Cette fonction simplifie le chemin en ne gardant que les points où la direction change.
    Les segments alignés (horizontaux ou verticaux) sont réduits à leurs extrémités.

    Args:
        path: Liste de coordonnées formant le chemin [(x1,y1), (x2,y2), ...]

    Returns:
        Chemin optimisé avec moins de points mais même distance totale

    Exemple:
        Entrée:  [(400,1700), (175,1400), (175,1000), (700,1150), (950,1150), (1700,1150), (1650,800)]
        Sortie:  [(400,1700), (175,1400), (175,1000), (1700,1150), (1650,800)]
    """
    # Si le chemin est trop court, pas d'optimisation possible
    if len(path) < 3:
        return path

    optimized = [path[0]]  # Toujours garder le premier point

    for i in range(1, len(path) - 1):
        prev_point = path[i - 1]
        current_point = path[i]
        next_point = path[i + 1]

        # Vérifier si le point courant est aligné avec le précédent et le suivant
        # Alignement horizontal : même Y entre prev->current ET current->next
        horizontal_aligned = (prev_point[1] == current_point[1] == next_point[1])

        # Alignement vertical : même X entre prev->current ET current->next
        vertical_aligned = (prev_point[0] == current_point[0] == next_point[0])

        # Si le point n'est pas aligné, c'est un changement de direction → on le garde
        if not (horizontal_aligned or vertical_aligned):
            optimized.append(current_point)

    # Toujours garder le dernier point
    optimized.append(path[-1])

    return optimized


########
### FONCTIONS PRINCIPALES
########

# claude diane
def _get_opposite_approach(arrived_node: str, approach_nodes: List[str]) -> Optional[str]:
    """
    Retourne le point d'approche opposé selon la convention de nommage :
        _a ↔ _b  (axe vertical : haut ↔ bas)
        _c ↔ _d  (axe horizontal : droite ↔ gauche)
    Si la convention ne s'applique pas, retourne le premier nœud différent.
    """
    opposite_map = {'_a': '_b', '_b': '_a', '_c': '_d', '_d': '_c'}
    for suffix, opp_suffix in opposite_map.items():
        if arrived_node.endswith(suffix):
            candidate = arrived_node[:-len(suffix)] + opp_suffix
            if candidate in approach_nodes:
                return candidate
    # fallback : premier nœud différent
    for node in approach_nodes:
        if node != arrived_node:
            return node
    return None
# claude diane


def generate_path(robot_pos: Tuple[float, float],
                  target_tas: str,
                  adversary_pos: Tuple[float, float],
                  available_tas: List[str],
                  deposited_zones: List[str] = None) -> Optional[List[Tuple[float, float]]]:
    """
    Génère un chemin pour atteindre un tas cible en évitant l'adversaire.

    Args:
        robot_pos: Position actuelle du robot (x, y)
        target_tas: Nom du tas cible (ex: 'tas_4')
        adversary_pos: Position de l'adversaire (x, y)
        available_tas: Liste des tas encore disponibles
        deposited_zones: Zones de dépôt déjà utilisées (interdites)

    Returns:
        Liste de coordonnées [(x1, y1), ...] ou None si aucun chemin trouvé
        Chemin : robot → points de passage → point d'approche → centre du tas
    """
    if target_tas not in TARGETS:
        return None
    if target_tas not in available_tas:
        return None

    graph = update_graph_available_tas(available_tas)
    graph = update_graph_tas_zones(graph, available_tas)
    if deposited_zones:
        graph = update_graph_depot_zones(graph, deposited_zones)
    # Retirer les points d'approche dépôt (d*_a, d*_b...) — inutiles pour aller à un tas, perturbent A*
    depot_approach = {k for k in graph if k.startswith('d') and '_' in k}
    graph = {k: [n for n in v if n not in depot_approach] for k, v in graph.items() if k not in depot_approach}
    graph, robot_node = update_graph_exclusion(graph, adversary_pos, robot_pos)

    approach_nodes = TARGETS[target_tas]
    best_path = None
    best_dist = float('inf')

    for ap_node in approach_nodes:
        if ap_node not in graph:
            continue
        path_nodes = astar(robot_node, ap_node, graph)
        if path_nodes is None:
            continue
        coords = [robot_pos] + [POINTS[n] for n in path_nodes[1:]]
        total = sum(dist_euclidean(coords[i], coords[i + 1]) for i in range(len(coords) - 1))
        if total < best_dist:
            best_dist = total
            best_path = coords

    if best_path is None:
        return None

    # Avancer jusqu'au centre du tas pour attraper les éléments
    best_path.append(TAS_COORDS[target_tas])
    return optimize_path(best_path)


def generate_path_to_deposit_caca(robot_pos: Tuple[float, float],          # claude diane
                                   target_deposit: str,
                                   adversary_pos: Tuple[float, float],
                                   available_tas: List[str] = None,
                                   deposited_zones: List[str] = None) -> Optional[List[Tuple[float, float]]]:
    """
    Génère un chemin vers une zone de dépôt (méthode caca).

    Args:
        robot_pos: Position actuelle du robot (x, y)
        target_deposit: Nom de la zone de dépôt (ex: 'd5')
        adversary_pos: Position de l'adversaire (x, y)
        available_tas: Liste des tas encore présents (zones interdites actives)
        deposited_zones: Zones de dépôt déjà utilisées (interdites)

    Returns:
        Liste de coordonnées [(x1, y1), ...] ou None si aucun chemin trouvé
        Chemin : robot → points de passage → point d'approche proche → point d'approche opposé
    """
    if target_deposit not in TARGETS_DEPOT_CACA:
        return None

    graph = {node: neighbors[:] for node, neighbors in GRAPH.items()}
    if available_tas:
        graph = update_graph_tas_zones(graph, available_tas)
    if deposited_zones:
        graph = update_graph_depot_zones(graph, deposited_zones)
    graph, robot_node = update_graph_exclusion(graph, adversary_pos, robot_pos)

    approach_nodes = TARGETS_DEPOT_CACA[target_deposit]
    best_path    = None
    best_dist    = float('inf')
    best_ap_node = None

    for ap_node in approach_nodes:
        if ap_node not in graph:
            continue
        path_nodes = astar(robot_node, ap_node, graph)
        if path_nodes is None:
            continue
        coords = [robot_pos] + [POINTS[n] for n in path_nodes[1:]]
        total = sum(dist_euclidean(coords[i], coords[i + 1]) for i in range(len(coords) - 1))
        if total < best_dist:
            best_dist    = total
            best_path    = coords
            best_ap_node = ap_node

    if best_path is None:
        return None

    # Traverser la zone : point d'approche proche → point d'approche OPPOSÉ
    opposite = _get_opposite_approach(best_ap_node, approach_nodes)
    if opposite:
        best_path.append(POINTS[opposite])

    return optimize_path(best_path)
# claude diane


########
### TEST
########

if __name__ == "__main__":
    # Valeurs de test
    ROBOT = (400, 1700)
    ROBOT_ADV = (2600, 1200)
    available_tas = ['tas_1', 'tas_2', 'tas_3', 'tas_4', 'tas_5', 'tas_6', 'tas_7', 'tas_8']

    # Test 1: Sélectionner le tas prioritaire
    print("=== Test 1: Sélection du tas prioritaire ===")
    target_tas = select_target_tas(available_tas)
    print(f"Tas sélectionné: {target_tas}")

    # Test 2: Générer un chemin vers ce tas
    print(f"\n=== Test 2: Génération du chemin vers {target_tas} ===")
    print(f"Robot: {ROBOT}")
    print(f"Adversaire: {ROBOT_ADV}")
    print(f"Tas disponibles: {available_tas}")

    path = generate_path(ROBOT, target_tas, ROBOT_ADV, available_tas)

    if path:
        print(f"\nChemin trouvé ({len(path)} points):")
        for i, point in enumerate(path):
            print(f"  {i+1}. {point}")

        # Calculer la distance totale
        total_dist = 0
        for i in range(len(path) - 1):
            total_dist += dist_euclidean(path[i], path[i+1])
        print(f"\nDistance totale: {total_dist:.1f} mm")
    else:
        print("\nAucun chemin trouvé!")

    # Test 3: Test avec tas partiellement disponibles
    print("\n=== Test 3: Tas partiellement disponibles ===")
    available_tas_partial = ['tas_1', 'tas_3', 'tas_5']
    target_tas_partial = select_target_tas(available_tas_partial)
    print(f"Tas disponibles: {available_tas_partial}")
    print(f"Tas sélectionné: {target_tas_partial}")

    path_partial = generate_path(ROBOT, target_tas_partial, ROBOT_ADV, available_tas_partial)
    if path_partial:
        print(f"Chemin trouvé ({len(path_partial)} points)")
    else:
        print("Aucun chemin trouvé!")

    # claude diane
    print("\n=== Test dépose caca vers d5 (milieu) ===")
    path_d = generate_path_to_deposit_caca((500, 1150), 'd5', (2600, 1200), available_tas)
    if path_d:
        print(f"Chemin trouvé ({len(path_d)} points):")
        for pt in path_d:
            print(f"  {pt}")
    else:
        print("Aucun chemin trouvé!")

    print("\n=== Test dépose caca vers d1 (bord haut) ===")
    path_d1 = generate_path_to_deposit_caca((500, 1150), 'd1', (2600, 1200), available_tas)
    if path_d1:
        print(f"Chemin trouvé ({len(path_d1)} points):")
        for pt in path_d1:
            print(f"  {pt}")
    else:
        print("Aucun chemin trouvé!")

    print("\n=== Test dépose caca vers d7 (bord droit) ===")
    path_d7 = generate_path_to_deposit_caca((2500, 500), 'd7', (500, 500), available_tas)
    if path_d7:
        print(f"Chemin trouvé ({len(path_d7)} points):")
        for pt in path_d7:
            print(f"  {pt}")
    else:
        print("Aucun chemin trouvé!")

    print("\n=== Test dépose caca vers d10 (bord bas) ===")
    path_d10 = generate_path_to_deposit_caca((2500, 500), 'd10', (500, 500), available_tas)
    if path_d10:
        print(f"Chemin trouvé ({len(path_d10)} points):")
        for pt in path_d10:
            print(f"  {pt}")
    else:
        print("Aucun chemin trouvé!")
    # claude diane
