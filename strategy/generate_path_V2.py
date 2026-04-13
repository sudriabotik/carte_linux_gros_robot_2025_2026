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
from strategy.coordonner_strat import POINTS, GRAPH, TARGETS, PRIORITY_ORDER


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

def update_graph_tas_attraper(available_tas: List[str]) -> Dict[str, List[str]]:
    """
    Relie entre eux les points d'approche des tas déjà attrapés

    Pour chaque tas que l'on a deeja attrapé, on peut maintenant
    relier directement ses 2 points d'approche entre eux dans le graphe,
    car il n'y a plus d'obstacle.

    Args:
        available_tas: Liste des tas encore disponibles

    Returns:
        Graphe modifié avec connexions directes entre points d'approche des tas attrapés

    Exemple:
        Si tas_1 a été attrapé, on relie t1_a <-> t1_b
    """
    # Créer une copie profonde du graphe
    graph_copy = {node: neighbors[:] for node, neighbors in GRAPH.items()}

    # Identifier les tas qui ont été attrapés (pas dans available_tas)
    all_tas = set(TARGETS.keys())
    captured_tas = all_tas - set(available_tas)

    # Pour chaque tas attrapé, relier ses points d'approche
    for tas in captured_tas:
        approach_points = TARGETS[tas]

        # Certains tas n'ont qu'un seul point d'approche (tas_5, tas_8)
        if len(approach_points) >= 2:
            point_a = approach_points[0]
            point_b = approach_points[1]

            # Ajouter la connexion bidirectionnelle entre les deux points
            if point_a in graph_copy and point_b not in graph_copy[point_a]:
                graph_copy[point_a].append(point_b)

            if point_b in graph_copy and point_a not in graph_copy[point_b]:
                graph_copy[point_b].append(point_a)

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
            if dx <= 100 and dy <= 100:  # Carré de 200×200mm (±100mm)
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
### FONCTION PRINCIPALE
########

def generate_path(robot_pos: Tuple[float, float],
                  target_tas: str,
                  adversary_pos: Tuple[float, float],
                  available_tas: List[str],
                  tas_attraper) -> Optional[List[Tuple[float, float]]]:
    """
    Génère un chemin pour atteindre un tas cible en évitant l'adversaire

    Args:
        robot_pos: Position actuelle du robot (x, y)
        target_tas: Nom du tas cible (ex: 'tas_4')
        adversary_pos: Position de l'adversaire (x, y)
        available_tas: Liste des tas encore disponibles

    Returns:
        Liste de coordonnées [(x1, y1), (x2, y2), ...] formant le chemin,
        ou None si aucun chemin trouvé
    """
    # 1. Vérifier que le tas cible existe et est disponible
    if target_tas not in TARGETS:
        return None
    if target_tas not in available_tas:
        return None

    # 2. Créer le graphe filtré par tas disponibles
    #graph = update_graph_available_tas(available_tas)

    graph = update_graph_tas_attraper(tas_attraper)

    # 3. Appliquer l'exclusion et insérer le robot
    graph, robot_node = update_graph_exclusion(graph, adversary_pos, robot_pos)

    # 4. Déterminer le point d'approche optimal du tas cible
    approach_points = TARGETS[target_tas]

    # Choisir le point d'approche le plus proche non bloqué
    best_approach = None
    min_distance = float('inf')

    for approach_point in approach_points:
        if approach_point in graph:  # Le point n'est pas bloqué
            # Calculer la distance du robot à ce point d'approche
            approach_pos = POINTS[approach_point]
            dist = dist_euclidean(robot_pos, approach_pos)
            if dist < min_distance:
                min_distance = dist
                best_approach = approach_point

    if best_approach is None:
        # Tous les points d'approche sont bloqués
        return None

    # 5. Calculer le chemin avec A*
    path_nodes = astar(robot_node, best_approach, graph)

    if path_nodes is None:
        return None

    # 8. Supprimer le premier waypoint s'il est trop proche du robot (< 150mm)
    if len(path_coords) > 1:  # S'assurer qu'il y a au moins 2 points
        first_point = path_coords[0]
        dx = abs(first_point[0] - robot_pos[0])
        dy = abs(first_point[1] - robot_pos[1])
        
        # Si le premier point est dans un carré de 150mm autour du robot
        if dx < 75 and dy < 75:  # 150mm / 2 = 75mm de rayon
            path_coords = path_coords[1:]  # Supprimer le premier point


    # 6. Convertir les noms de nœuds en coordonnées
    path_coords = []
    for i, node_name in enumerate(path_nodes):
        if i == 0:
            # Premier nœud : utiliser la position réelle du robot
            path_coords.append(robot_pos)
        else:
            # Autres nœuds : utiliser les coordonnées du dictionnaire POINTS
            path_coords.append(POINTS[node_name])

    # 7. Optimiser le chemin en supprimant les points alignés
    return optimize_path(path_coords)


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
