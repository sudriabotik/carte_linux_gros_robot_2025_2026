#from communication_wifi.comm_wifi import get_tas_available
import heapq
from copy import deepcopy
from strat_dynamique.mouv_automatiser import Robot
'''
on va essayer de faire un protoype avec des prints de generation d'un nouveau chemin et de la gestion des obstacles 
L'objectif est de pouvoir attraper un tas disponible meme si l'adversaire se trouve sur le chemin d'un tas que l'on voulais attraper

''' 
robot = Robot()

ordre_tas_prioritaire = ['tas_4', 'tas_8', 'tas_6', 'tas_3', 'tas_5', 'tas_2', 'tas_7', 'tas_1']

y_ligne_min = 700
y_ligne_max = 1320

x1 = 700
x2 = 950
x3 = 1300
x4 = 1700
x5 = 2050
x6 = 2450

x_y_Robot = (0,0) # position de notre robot 

p1= (x1, y_ligne_min)
p2= (x2, y_ligne_min)
p3= (x3, y_ligne_min)
p4= (x4, y_ligne_min)
p5= (x5, y_ligne_min)
p6= (x6, y_ligne_min)
p7= (x1, y_ligne_max)
p8= (x2, y_ligne_max)
p9= (x3, y_ligne_max)
p10= (x4, y_ligne_max)
p11= (x5, y_ligne_max)
p12= (x6, y_ligne_max)
t1= (300,400)
t2= (780,500)
t3= (2220,500)
t4= (2650,400)
t5= (300,1320)
t6_1= (1100,700) # en bas 
t6_2= (1100,1200)# en haut
t7_1= (1900,700) # en bas
t7_2= (1900,1200) # en haut
t8= (2650,1320)

points = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, t1, t2, t3, t4, t5, t6_1, t6_2, t7_1, t7_2, t8]

point_devant_tas = { # (x,y)
    'tas_1':[t1],
    'tas_2':[t2],
    'tas_3':[t3],
    'tas_4':[t4],
    'tas_5':[t5],
    'tas_6':[t6_1, t6_2],
    'tas_7':[t7_1, t7_2],
    'tas_8':[t8],
}


graph = {
    p1: [t1, t2, t6_1, p2, p7],
    p2: [p1, p3, t2, t6_1, t1],
    p3: [p2, p4, t6_1],
    p4: [p3, p5, t7_1],
    p5: [p4, p6, t7_1, t3],
    p6: [p5, p12, t4, t3],
    p7: [p1, p8, t5],
    p8: [p7, p9, t6_2],
    p9: [p8, p10, t6_2],
    p10: [p9, p11, t7_2],
    p11: [p10, p12, t7_2],
    p12: [p11, p6, t8],
    t1: [p1, p2],
    t2: [p1, p2, p3],
    t6_1: [p2, p3],
    t7_1: [p4, p5],
    t3: [p5, p6, p4],
    t4: [p6],
    t5: [p7],
    t6_2: [p8, p9],
    t7_2: [p10, p11],
    t8: [p12],
    # x_y_Robot: [...] ajout dynamique de ce point et de ces liens en fonction de la position du robot et de la zone

}

zone = { #'zone_nom':{'coord':(x_min,x_max,y_min,y_max,), 'point':[p1,p2...]}
    'zone_1':{'coord':(0,1500,0,1000),'point':[p1,p2,p3]},
    'zone_2':{'coord':(1500,2250,0,1000),'point':[p4,p5]},
    'zone_3':{'coord':(2250,3000,0,1000),'point':[p6]},
    'zone_4':{'coord':(0,750,1000,2000), 'point':[p7]},
    'zone_5':{'coord':(750,1500,1000,2000), 'point':[p8,p9]},
    'zone_6':{'coord':(1500,2250,1000,2000), 'point':[p10,p11]},
    'zone_7':{'coord':(2250,3000,1000,2000), 'point':[p12]},
}

def find_zone_robot(position_robot):
    global x_y_Robot
    x_robot = position_robot[0]
    y_robot = position_robot[1]

    x_y_Robot = (x_robot, y_robot)

    zone_robot = None
    for nom_zone, data in zone.items():
        x_min, x_max, y_min, y_max = data['coord']
        if x_min <= x_robot <= x_max and y_min <= y_robot <= y_max:
            zone_robot = nom_zone
            break
    if zone_robot is None:
        print("Le robot choisi n'est pas dans une zone définie.")
        return None
    #print(f"Zone de l'adversaire : {zone_robot}")

    return zone_robot

def tas_cible(tas_available, zone_adversaire):
    # On cherche un tas prioritaire disponible, dont AU MOINS UN point n'est pas dans la zone de l'adversaire
    for tas in ordre_tas_prioritaire:
        if tas in tas_available:
            for (x_tas, y_tas) in point_devant_tas[tas]:
                for nom_zone, data in zone.items():
                    x_min, x_max, y_min, y_max = data['coord']
                    if x_min <= x_tas <= x_max and y_min <= y_tas <= y_max:
                        zone_tas = nom_zone
                        break
                else:
                    zone_tas = None

                if zone_tas != zone_adversaire:
                    print(f"Tas cible choisi : {tas} (zone {zone_tas}), car l'adversaire est en {zone_adversaire}")
                    point_objectif = (x_tas, y_tas)
                    print(f"Point objectif : {point_objectif}")

                    return tas, point_objectif
    print("Aucun tas prioritaire disponible hors de la zone de l'adversaire.")
    return None

def update_graph(position_robot, zone_adversaire, base_graph):
    """
    Retourne toujours (graphe_modifié, robot_node ou None)
    """
    g = deepcopy(base_graph)
    robot_node = tuple(position_robot)

    # 1) zone du robot
    z_robot = find_zone_robot(position_robot)
    print(f"Zone de notre robot : {z_robot}")

    # 2) suppression des points de la zone adverse
    if zone_adversaire and zone_adversaire != z_robot:
        for pt in zone[zone_adversaire]['point']:
            if pt in g:
                for v in g.values():
                    if pt in v:
                        v.remove(pt)
                del g[pt]

    # 3) insertion du robot ----------------------------------------
    if z_robot is None:
        print("[update_graph] Robot hors zones → robot_node=None")
        return g, None

    connex = [p for p in zone[z_robot]['point'] if p in g]

    # s’il n’y a plus de nœud officiel dans la zone (ex. supprimés car adv),
    # on relie le robot au sommet restant le plus proche
    if not connex:
        if not g:
            print("[update_graph] Graphe vide (!)"); return g, None
        nearest = min(g, key=lambda n: abs(n[0]-robot_node[0])+abs(n[1]-robot_node[1]))
        connex = [nearest]
        print(f"[update_graph] Aucun nœud dans la zone ➜ relié à {nearest}")

    g[robot_node] = list(connex)
    for p in connex:
        g[p].append(robot_node)

    return g, robot_node 

def dist(a, b):
    xa, ya = a
    xb, yb = b
    return abs(xb - xa) + abs(yb - ya)    # distance Manhattan

def astar(start, goal, graph):
    pq = [(dist(start, goal), 0, start, [start])]
    best_g = {start: 0}

    while pq:
        f, g, node, path = heapq.heappop(pq)
        if node == goal:
            return path

        for neigh in graph[node]:
            w  = dist(node, neigh)        # poids de l’arête
            g2 = g + w                    # coût cumulé
            if g2 < best_g.get(neigh, 1e18):
                best_g[neigh] = g2
                f2 = g2 + dist(neigh, goal)
                heapq.heappush(pq, (f2, g2, neigh, path + [neigh]))
    return None

def conversion(point_passage):
    # 1) Retirer le point de départ
    if not point_passage or len(point_passage) < 2:
        return []
    points = point_passage[1:]  # on retire le point de départ

    # 2) Garder seulement les points extrêmes pour chaque valeur de y
    if len(points) < 2:
        filtered = points
    else:
        filtered = [points[0]]
        for i in range(1, len(points) - 1):
            prev, curr, next_ = points[i-1], points[i], points[i+1]
            # Si le y du point courant est différent du précédent ou du suivant, on garde
            if curr[1] != prev[1] or curr[1] != next_[1]:
                filtered.append(curr)
        filtered.append(points[-1])

    # 3) Conversion en string de 4 chiffres
    result = []
    for x, y in filtered:
        sx = f"{x:04d}"
        sy = f"{y:04d}"
        result.append((sx, sy))
    print(f"[DEBUG] point de passage : {result}")
    return result

def find_orientation_callage_objectif(point_passage, face):
    point_final = point_passage[-1]  # le dernier point de passage
    orientation_objectif = None
    callage_x = False # Variable pour savoir si on doit faire un callage
    callage_y = False # Variable pour savoir si on doit faire un callage en x
    for nom_tas, points in point_devant_tas.items():
        if point_final in points:
            # Gestion spéciale pour tas_6 et tas_7 (deux points possibles)
            if nom_tas == 'tas_6':
                if point_final == t6_1:
                    orientation_objectif = '090' if face == 'A' else '270'  # t6_1 = en bas
                elif point_final == t6_2:
                    orientation_objectif = '270' if face == 'A' else '090'  # t6_2 = en haut
                else:
                    orientation_objectif = None
            elif nom_tas == 'tas_7':
                if point_final == t7_1:
                    orientation_objectif = '090' if face == 'A' else '270'  # t7_1 = en bas
                elif point_final == t7_2:
                    orientation_objectif = '270' if face == 'A' else '090'  # t7_2 = en haut
                else:
                    orientation_objectif = None
            elif (nom_tas == 'tas_1') or (nom_tas == 'tas_5'):
                callage_x = True  # On doit faire un callage en x
                orientation_objectif = '180' if face == 'A' else '000'
            elif (nom_tas == 'tas_4') or (nom_tas == 'tas_8'):
                callage_x = True  # On doit faire un callage en y
                orientation_objectif = '000' if face == 'A' else '180'
            elif (nom_tas == 'tas_2') or (nom_tas == 'tas_3'):
                callage_y = True  # On doit faire un callage en y
                orientation_objectif = '270' if face == 'A' else '090'
            else:
                orientation_objectif = None
            return orientation_objectif, callage_x, callage_y
    print(f"[find_orientation_objectif] Aucun tas trouvé pour le point final {point_final}")
    return None


def generate_path_to_next_tas(position_notre_robot, position_robot_adersaire, les_tas_available):
    #position_notre_robot = (x,y)
    #position_robot_adersaire = (x,y)

    #les_tas_available = get_tas_available()
    les_tas_available = ['tas_5', 'tas_4', 'tas_3', 'tas_1', 'tas_2', 'tas_6', 'tas_7', 'tas_8']
    #les_tas_available = ['tas_1']

    zone_adversaire = find_zone_robot(position_robot_adersaire)
    print(f"Zone de l'adversaire : {zone_adversaire}")

    tas_objectif, point_cible = tas_cible(les_tas_available, zone_adversaire)

    if tas_objectif is None:
        print("Aucun tas disponible hors de la zone de l'adversaire.")
        return None

    g_mod, robot_node = update_graph(position_notre_robot, zone_adversaire, graph )

    
    if robot_node is None:
        print("Impossible d’insérer le robot ; abort.")
        return None

    point_passage = astar(robot_node, point_cible, g_mod) # comment sont gérer les point 6_1 et 6_2 , 7_1 et 7_2

    if point_passage is None:
        print("Aucun chemin possible vers le tas objectif.")
        return None
    
    print(f"[DEBUG]Point de passage astar {tas_objectif} : {point_passage}")

    pt_passage = conversion(point_passage)

    # which face of the robot we need to face to the tas
    face = robot.priority_face()

    # which orientation we need to face to the tas
    orientation_objectif, callage_x, callage_y = find_orientation_callage_objectif(point_passage, face)

    sens = '1' if face == 'A' else '0'

    print(f"[DEBUG] Face: {face}, Sens: {sens}, Orientation Objectif: {orientation_objectif}, Callage X: {callage_x}, Callage Y: {callage_y}")
    return pt_passage, orientation_objectif, callage_x, callage_y, sens

