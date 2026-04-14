'''
Ce fichier permet de regrouper à un seul endroit toutes les coordonnées
des différents points utiles :
 - éléments de jeux # la coordonnée du tas qui regroupe les éléments de jeux
 - points de passage # les points par lesquels le robot peut passer pour atteindre sa destination
 - points d'approche # le point juste avant un élément de jeux (il permet d'appréhender dans la bonne direction l'élément de jeux)
 - point de dépose # là où les éléments de jeux doivent être posés
'''

########
### COORDONNÉES DES ÉLÉMENTS DE JEUX & POINTS D'APPROCHE ###
########
# Syntaxe :
# tas_num = (x,y)

tas_1 = (175, 1200)
tas_2 = (2825, 1200)
tas_3 = (1150, 800)
tas_4 = (1850, 800)
tas_5 = (175, 400)
tas_6 = (1100, 175)
tas_7 = (1900, 175)
tas_8 = (2825, 400)

# Dictionnaire pour accéder facilement aux coordonnées des tas
TAS_COORDS = {
    'tas_1': tas_1,
    'tas_2': tas_2,
    'tas_3': tas_3,
    'tas_4': tas_4,
    'tas_5': tas_5,
    'tas_6': tas_6,
    'tas_7': tas_7,
    'tas_8': tas_8,
}

# Zones interdites des tas (200mm × 150mm) — le robot ne peut pas passer dans ces zones
# tant que le tas n'a pas été ramassé (format : x_min, x_max, y_min, y_max)
TAS_W = 100  # demi-largeur : 200mm / 2
TAS_H = 75   # demi-hauteur : 150mm / 2
ZONES_INTERDITES_TAS = {
    'tas_1': (tas_1[0]-TAS_W, tas_1[0]+TAS_W, tas_1[1]-TAS_H, tas_1[1]+TAS_H),  # (75,  275, 1125, 1275)
    'tas_2': (tas_2[0]-TAS_W, tas_2[0]+TAS_W, tas_2[1]-TAS_H, tas_2[1]+TAS_H),  # (2725,2925,1125,1275)
    'tas_3': (tas_3[0]-TAS_W, tas_3[0]+TAS_W, tas_3[1]-TAS_H, tas_3[1]+TAS_H),  # (1050,1250, 725, 875)
    'tas_4': (tas_4[0]-TAS_W, tas_4[0]+TAS_W, tas_4[1]-TAS_H, tas_4[1]+TAS_H),  # (1750,1950, 725, 875)
    'tas_5': (tas_5[0]-TAS_W, tas_5[0]+TAS_W, tas_5[1]-TAS_H, tas_5[1]+TAS_H),  # (75,  275,  325, 475)
    'tas_6': (tas_6[0]-TAS_W, tas_6[0]+TAS_W, tas_6[1]-TAS_H, tas_6[1]+TAS_H),  # (1000,1200, 100, 250)
    'tas_7': (tas_7[0]-TAS_W, tas_7[0]+TAS_W, tas_7[1]-TAS_H, tas_7[1]+TAS_H),  # (1800,2000, 100, 250)
    'tas_8': (tas_8[0]-TAS_W, tas_8[0]+TAS_W, tas_8[1]-TAS_H, tas_8[1]+TAS_H),  # (2725,2925, 325, 475)
}

# Pour appréhender ces tas, le robot doit arriver avec une certaine distance de ce tas.
dist_tas = 400

# En fonction des tas, cette distance doit être ajoutée en x ou en y :
# tas : 1, 2, 5, 8 la distance doit être ajoutée en y
# tas : 3, 4, 6, 7 la distance doit être ajoutée en x

# Points d'approche pour tas 1, 2, 5, 8 (ajout en Y)
t1_a = (tas_1[0], tas_1[1] + dist_tas)  # (175, 1600)
t1_b = (tas_1[0], tas_1[1] - dist_tas)  # (175, 800)     #jumeau : t5_a/t1_b
t2_a = (tas_2[0], tas_2[1] + dist_tas)  # (2825, 1600)
t2_b = (tas_2[0], tas_2[1] - dist_tas)  # (2825, 800)    #jumeau : t8_a/t2_b
t5_a = (tas_5[0], tas_5[1] + dist_tas)  # (175, 800)     #jumeau : t1_b/t5_a
# t5_b = (tas_5[0], tas_5[1] - dist_tas)  # (175, 0)     # robot gros
t8_a = (tas_8[0], tas_8[1] + dist_tas)  # (2825, 800)    #jumeau : t2_b/t8_a
# t8_b = (tas_8[0], tas_8[1] - dist_tas)  # (2825, 0)    # robot gros

# Points d'approche pour tas 3, 4, 6, 7 (ajout en X)
t3_a = (tas_3[0] + dist_tas, tas_3[1])  # (1550, 800) 
t3_b = (tas_3[0] - dist_tas, tas_3[1])  # (750, 800)
t4_a = (tas_4[0] + dist_tas, tas_4[1])  # (2250, 800)
t4_b = (tas_4[0] - dist_tas, tas_4[1])  # (1450, 800)
t6_a = (tas_6[0] + dist_tas, tas_6[1])  # (1500, 175)   #jumeau : t7_b/t6_a
t6_b = (tas_6[0] - dist_tas, tas_6[1])  # (700, 175)
t7_a = (tas_7[0] + dist_tas, tas_7[1])  # (2300, 175)
t7_b = (tas_7[0] - dist_tas, tas_7[1])  # (1500, 175)   #jumeau : t6_a/t7_b

#########
### ZONE DE DÉPOSE
########
# Syntaxe :
# dx = (x, y)  → centre de la zone de dépose

d1  = (1250, 1450)
d2  = (1750, 1450)
d3  = (100,  800)
d4  = (800,  800)
d5  = (1500, 800)
d6  = (2200, 800)
d7  = (2900, 800)
d8  = (700,  100)
d9  = (1500, 100)
d10 = (2300, 100)

DEPOSE_COORDS = {
    'd1':  d1,  'd2':  d2,
    'd3':  d3,  'd4':  d4,  'd5':  d5,  'd6':  d6,  'd7':  d7,
    'd8':  d8,  'd9':  d9,  'd10': d10,
}

# Zones interdites des dépôts — actives après que le robot y a déposé des objets  # claude diane
# Rectangle 200×200mm centré sur le centre de chaque dépôt (format : x_min, x_max, y_min, y_max)
DEP_W = 100  # demi-côté : 200mm / 2                                               # claude diane
ZONES_INTERDITES_DEPOT = {                                                          # claude diane
    'd1':  (d1[0]-DEP_W,  d1[0]+DEP_W,  d1[1]-DEP_W,  d1[1]+DEP_W),
    'd2':  (d2[0]-DEP_W,  d2[0]+DEP_W,  d2[1]-DEP_W,  d2[1]+DEP_W),
    'd3':  (d3[0]-DEP_W,  d3[0]+DEP_W,  d3[1]-DEP_W,  d3[1]+DEP_W),
    'd4':  (d4[0]-DEP_W,  d4[0]+DEP_W,  d4[1]-DEP_W,  d4[1]+DEP_W),
    'd5':  (d5[0]-DEP_W,  d5[0]+DEP_W,  d5[1]-DEP_W,  d5[1]+DEP_W),
    'd6':  (d6[0]-DEP_W,  d6[0]+DEP_W,  d6[1]-DEP_W,  d6[1]+DEP_W),
    'd7':  (d7[0]-DEP_W,  d7[0]+DEP_W,  d7[1]-DEP_W,  d7[1]+DEP_W),
    'd8':  (d8[0]-DEP_W,  d8[0]+DEP_W,  d8[1]-DEP_W,  d8[1]+DEP_W),
    'd9':  (d9[0]-DEP_W,  d9[0]+DEP_W,  d9[1]-DEP_W,  d9[1]+DEP_W),
    'd10': (d10[0]-DEP_W, d10[0]+DEP_W, d10[1]-DEP_W, d10[1]+DEP_W),
}                                                                                    # claude diane

# Distance d'approche pour les zones de dépose
dist_depose = 200

# Points d'approche fixes pour les zones de dépose de bord (dist = 200mm)
# Axe Y (robot longe le mur vertical) : d3 (bord gauche), d7 (bord droit)
x_depose_gauche = tas_1[0]  # 175 — aligné à tas1 (bord gauche)
x_depose_droit  = tas_2[0]  # 2825 — aligné à tas2 (bord droit)
d3_a = (x_depose_gauche, d3[1] + dist_depose)  # (175, 1000)
d3_b = (x_depose_gauche, d3[1] - dist_depose)  # (175,  600)
d7_a = (x_depose_droit,  d7[1] + dist_depose)  # (2825, 1000)
d7_b = (x_depose_droit,  d7[1] - dist_depose)  # (2825,  600)

# Axe X (robot longe le mur horizontal bas) : d8, d9, d10
y_depose=tas_6[1]  #aligné à tas6
d8_a  = (d8[0]  + dist_depose, y_depose)   # (900,  100)
d8_b  = (d8[0]  - dist_depose, y_depose)   # (500,  100)
d9_a  = (d9[0]  + dist_depose, y_depose)   # (1700, 100)
d9_b  = (d9[0]  - dist_depose, y_depose)   # (1300, 100)
d10_a = (d10[0] + dist_depose, y_depose)  # (2500, 100)
d10_b = (d10[0] - dist_depose, y_depose)  # (2100, 100)

# Axe X (y+ bloqué par zone interdite) : d1, d2
d1_a = (d1[0] + dist_depose, d1[1]-50)  # (1450, 1400)
d1_b = (d1[0] - dist_depose, d1[1]-50)  # (1050, 1400)
d2_a = (d2[0] + dist_depose, d2[1]-50)  # (1950, 1400)
d2_b = (d2[0] - dist_depose, d2[1]-50)  # (1550, 1400)

# 4 points d'approche (milieu de table) : d4, d5, d6
# _a=+Y(haut), _b=-Y(bas), _c=+X(droite), _d=-X(gauche)
d4_a = (d4[0],             d4[1] + dist_depose)   # (800,  1000)
d4_b = (d4[0],             d4[1] - dist_depose)   # (800,   600)
d4_c = (d4[0] + dist_depose, d4[1])               # (1000,  800)
d4_d = (d4[0] - dist_depose, d4[1])               # (600,   800)

d5_a = (d5[0],             d5[1] + dist_depose)   # (1500, 1000)
d5_b = (d5[0],             d5[1] - dist_depose)   # (1500,  600)
d5_c = (d5[0] + dist_depose, d5[1])               # (1700,  800)
d5_d = (d5[0] - dist_depose, d5[1])               # (1300,  800)

d6_a = (d6[0],             d6[1] + dist_depose)   # (2200, 1000)
d6_b = (d6[0],             d6[1] - dist_depose)   # (2200,  600)
d6_c = (d6[0] + dist_depose, d6[1])               # (2400,  800)
d6_d = (d6[0] - dist_depose, d6[1])               # (2000,  800)




######## Points d'approche des zones de dépose (b = bouche) — conservés comme référence
# Suffixe : _a = +Y (haut), _b = -Y (bas), _c = +X (droite), _d = -X (gauche)
dist_bouche = 100

# d1 (1250, 1450)
#d1_b_a = (d1[0], d1[1] + dist_bouche)   # (1250, 1550) # pas possible pour le robot
#d1_b_b = (d1[0], d1[1] - dist_bouche)   # (1250, 1350)
#d1_b_c = (d1[0] + dist_bouche, d1[1])   # (1350, 1450)
#d1_b_d = (d1[0] - dist_bouche, d1[1])   # (1150, 1450)

# d2 (1750, 1450)
#d2_b_a = (d2[0], d2[1] + dist_bouche)   # (1750, 1550) # pas possible pour le robot
#d2_b_b = (d2[0], d2[1] - dist_bouche)   # (1750, 1350)
#d2_b_c = (d2[0] + dist_bouche, d2[1])   # (1850, 1450)
#d2_b_d = (d2[0] - dist_bouche, d2[1])   # (1650, 1450)

# d3 (100, 800)
#d3_b_a = (d3[0], d3[1] + dist_bouche)   # (100, 900)
#d3_b_b = (d3[0], d3[1] - dist_bouche)   # (100, 700)
#d3_b_c = (d3[0] + dist_bouche, d3[1])   # (200, 800)
#d3_b_d = (d3[0] - dist_bouche, d3[1])   # (0, 800) # pas possible pour le robot

# d4 (800, 800)
#d4_b_a = (d4[0], d4[1] + dist_bouche)   # (800, 900)
#d4_b_b = (d4[0], d4[1] - dist_bouche)   # (800, 700)
#d4_b_c = (d4[0] + dist_bouche, d4[1])   # (900, 800)
#d4_b_d = (d4[0] - dist_bouche, d4[1])   # (700, 800)

# d5 (1500, 800)
#d5_b_a = (d5[0], d5[1] + dist_bouche)   # (1500, 900)
#d5_b_b = (d5[0], d5[1] - dist_bouche)   # (1500, 700)
#d5_b_c = (d5[0] + dist_bouche, d5[1])   # (1600, 800)
#d5_b_d = (d5[0] - dist_bouche, d5[1])   # (1400, 800)

# d6 (2200, 800)
#d6_b_a = (d6[0], d6[1] + dist_bouche)   # (2200, 900)
#d6_b_b = (d6[0], d6[1] - dist_bouche)   # (2200, 700)
#d6_b_c = (d6[0] + dist_bouche, d6[1])   # (2300, 800)
#d6_b_d = (d6[0] - dist_bouche, d6[1])   # (2100, 800)

# d7 (2900, 800)
#d7_b_a = (d7[0], d7[1] + dist_bouche)   # (2900, 900)
#d7_b_b = (d7[0], d7[1] - dist_bouche)   # (2900, 700)
#d7_b_c = (d7[0] + dist_bouche, d7[1])   # (3000, 800) # pas possible pour le robot
#d7_b_d = (d7[0] - dist_bouche, d7[1])   # (2800, 800)

# d8 (700, 100)
#d8_b_a = (d8[0], d8[1] + dist_bouche)   # (700, 200)
#d8_b_b = (d8[0], d8[1] - dist_bouche)   # (700, 0) # pas possible pour le robot
#d8_b_c = (d8[0] + dist_bouche, d8[1])   # (800, 100)
#d8_b_d = (d8[0] - dist_bouche, d8[1])   # (600, 100)

# d9 (1500, 100)
#d9_b_a = (d9[0], d9[1] + dist_bouche)   # (1500, 200)
#d9_b_b = (d9[0], d9[1] - dist_bouche)   # (1500, 0) # pas possible pour le robot
#d9_b_c = (d9[0] + dist_bouche, d9[1])   # (1600, 100)
#d9_b_d = (d9[0] - dist_bouche, d9[1])   # (1400, 100)

# d10 (2300, 100)
#d10_b_a = (d10[0], d10[1] + dist_bouche)  # (2300, 200)
#d10_b_b = (d10[0], d10[1] - dist_bouche)  # (2300, 0) # pas possible pour le robot
#d10_b_c = (d10[0] + dist_bouche, d10[1])  # (2400, 100)
#d10_b_d = (d10[0] - dist_bouche, d10[1])  # (2200, 100)

ROBOT_WIDTH  = 280  # largeur du robot en mm
ROBOT_LENGTH = 340  # longueur du robot en mm

# Zone réservée à l'autre robot — interdite
ZONE_INTERDITE = (600, 2400, 1550, 2000)  # (x_min, x_max, y_min, y_max)



########
### POINTS DE PASSAGE
########


########
### POINTS DE PASSAGE
########

y_ligne_min = 500
y_ligne_max = 1150

x1 = 500
x2 = 1500
x3 = 2500


p1 = (x1, y_ligne_min)   # (700, 500)
p2 = (x2, y_ligne_min)   # (950, 500)
p3 = (x3, y_ligne_min)   # (1300, 500)
#p4 = (x4, y_ligne_min)   # (1700, 500)
#p5 = (x5, y_ligne_min)   # (2050, 500)
#p6 = (x6, y_ligne_min)   # (2450, 500)
p4 = (x1, y_ligne_max)   # (700, 1150)
p5 = (x2, y_ligne_max)   # (950, 1150)
p6 = (x3, y_ligne_max)   # (1300, 1150)


# Ligne extérieure basse (y = 300)
p7  = (350,  300)    # bas gauche
p8 = (2500, 300)    # bas droit


########
### DICTIONNAIRE DES POINTS
########

POINTS = {
    # Points de passage ligne haute (y=1150)
    'p1': p1, 'p2': p2, 'p3': p3,
    # Points de passage ligne haute (y=1150)
    'p4': p4, 'p5': p5, 'p6': p6,
    # Points de passage ligne basse (y=300)
    'p7': p7, 'p8': p8,
    # Points d'approche tas
    't1_a': t1_a, 't1_b': t1_b,
    't2_a': t2_a, 't2_b': t2_b,
    't3_a': t3_a, 't3_b': t3_b,
    't4_a': t4_a, 't4_b': t4_b,
    't5_a': t5_a, #'t5_b': t5_b,
    't6_a': t6_a, 't6_b': t6_b,
    't7_a': t7_a, 't7_b': t7_b,
    't8_a': t8_a, #'t8_b': t8_b,
    # Points d'approche zones de dépose milieu (d4, d5, d6 — 4 directions)
    'd4_a': d4_a, 'd4_b': d4_b, 'd4_c': d4_c, 'd4_d': d4_d,
    'd5_a': d5_a, 'd5_b': d5_b, 'd5_c': d5_c, 'd5_d': d5_d,
    'd6_a': d6_a, 'd6_b': d6_b, 'd6_c': d6_c, 'd6_d': d6_d,
    # Points d'approche fixes zones de dépose bord (d1, d2, d3, d7, d8, d9, d10)
    'd1_a':  d1_a,
    'd1_b':  d1_b,
    'd2_a':  d2_a,  'd2_b':  d2_b,
    'd3_a':  d3_a,  'd3_b':  d3_b,
    'd7_a':  d7_a,  'd7_b':  d7_b,
    'd8_a':  d8_a,  'd8_b':  d8_b,
    'd9_a':  d9_a,  'd9_b':  d9_b,
    'd10_a': d10_a, 'd10_b': d10_b,
}


########
### GRAPHE DES CONNEXIONS
########
# Ce graphe détermine quels points sont reliés entre eux

GRAPH = {
    # ──────────────────────────────────────────────────────────
    #  p4(500,1150) ──── p5(1500,1150) ──── p6(2500,1150)   ligne haute
    #  |                  |                  |
    #  p1(500,500)  ──── p2(1500,500)  ──── p3(2500,500)    ligne basse
    #  |                                     |
    #  p7(350,300)  ─────────────────── p8(2500,300)         ligne très basse
    # ──────────────────────────────────────────────────────────

    # Ligne basse (y=500)
    'p1':  ['p2', 'p4', 't1_b', 't5_a', 't3_b', 't6_b', 'd3_b', 'd4_d', 'd4_b', 'd8_a', 'd8_b', 'p7', 'd5_b'],
    'p2':  ['p1', 'p3', 'p5', 't3_a', 't4_b', 't6_a', 't7_b', 'd5_b', 'd5_d', 'd6_d', 'd9_a', 'd9_b', 'd6_b', 'd4_b'],
    'p3':  ['p2', 'p6', 't4_a', 't2_b', 't8_a', 't7_a', 'd5_c', 'd6_b', 'd6_c', 'd7_b', 'd10_a', 'd10_b', 'p8', 'd5_b'],

    # Ligne haute (y=1150)
    'p4':  ['p1', 'p5', 't1_a', 't1_b', 't5_a', 't3_b', 't3_a', 't4_b', 'd4_a', 'd4_d', 'd3_a', 'd5_a', 'd5_d', 'd1_b'],
    'p5':  ['p4', 'p6', 'p2', 't3_a', 't4_b', 't4_a', 't2_b', 't8_a', 'd4_c', 'd5_a', 'd5_c', 'd6_a', 'd6_d', 'd1_a', 'd1_b', 'd2_a', 'd2_b', 'd4_a', 'd6_a'],
    'p6':  ['p3', 'p5', 't2_a', 't2_b', 't8_a', 't4_a', 'd6_a', 'd6_c', 'd7_a', 'd2_a', 'd5_a'],

    # Ligne très basse (y=300)
    'p7':  ['p1', 'p8', 't6_b', 'd8_a', 'd8_b', 'd3_b'],
    'p8':  ['p3', 'p7', 't7_a', 'd10_a', 'd10_b', 'd7_b'],

    # Points d'approche tas 1 — axe Y, bord gauche
    't1_a': ['p4', 't1_b'],                                              # (175, 1600)
    't1_b': ['p1', 'p4', 't1_a', 't5_a', 't3_b', 'd3_a', 'd3_b', 'd4_d'],     # (175, 800)

    # Points d'approche tas 2 — axe Y, bord droit
    't2_a': ['p6', 't2_b'],                                              # (2825, 1600)
    't2_b': ['p3', 'p5', 'p6', 't2_a', 't8_a', 't4_a', 'd7_a', 'd7_b', 'd6_c'], # (2825, 800)

    # Points d'approche tas 3 — axe X, milieu
    't3_a': ['p2', 'p4', 'p5', 't3_b', 't4_b', 'd4_c', 'd5_c', 'd5_d'],  # (1550, 800)
    't3_b': ['p1', 'p4', 't3_a', 't1_b', 't5_a', 'd4_c'],              # (750,  800)

    # Points d'approche tas 4 — axe X, milieu
    't4_a': ['p3', 'p5', 'p6', 't4_b', 't2_b', 't8_a', 'd6_d'],        # (2250, 800)
    't4_b': ['p2', 'p4', 'p5', 't4_a', 't3_a', 'd5_c', 'd5_d', 'd6_d'], # (1450, 800)

    # Points d'approche tas 5 — axe Y, bord gauche (jumeau t1_b)
    't5_a': ['p1', 'p4', 't1_b', 't3_b', 'd3_a', 'd3_b', 'd4_d'],             # (175, 800)

    # Points d'approche tas 6 — axe X, bord bas
    't6_a': ['p2', 't6_b', 't7_b', 'd9_a', 'd9_b'],                    # (1500, 175)
    't6_b': ['p1', 'p7', 't6_a', 'd8_a', 'd8_b'],                      # (700,  175)

    # Points d'approche tas 7 — axe X, bord bas
    't7_a': ['p3', 'p8', 't7_b', 'd10_a', 'd10_b'],                    # (2300, 175)
    't7_b': ['p2', 't7_a', 't6_a', 'd9_a', 'd9_b'],                    # (1500, 175)

    # Points d'approche tas 8 — axe Y, bord droit (jumeau t2_b)
    't8_a': ['p3', 'p5', 'p6', 't2_b', 't4_a', 'd7_a', 'd7_b', 'd6_c'], # (2825, 800)

    # Points d'approche d4 — 4 directions (milieu gauche)
    'd4_a': ['p4', 'd4_b','d1_b', 'p5'],   # (800,  1000)
    'd4_b': ['p1', 'd4_a', 'd8_a', 'p2'],   # (800,   600)
    'd4_c': ['p5', 'd4_d', 't3_b', 't3_a', 'd5_d'],   # (1000,  800)
    'd4_d': ['p1', 'p4', 'd4_c', 'd3_a', 'd3_b', 't5_a', 't1_b'],  # (600, 800)

    # Points d'approche d5 — 4 directions (milieu centre)
    'd5_a': ['p4', 'p5', 'p6', 'd5_b', 'd2_b', 'd1_a'],  # (1500, 1000)
    'd5_b': ['p1', 'p2', 'p3', 'd5_a', 'd9_a', 'd9_b'],  # (1500,  600)
    'd5_c': ['p3', 'p5', 'd5_d', 't3_a', 't4_b', 'd6_d'],  # (1700,  800)
    'd5_d': ['p2', 'p4', 'd5_c', 't3_a', 't4_b', 'd4_c'],  # (1300,  800)

    # Points d'approche d6 — 4 directions (milieu droite) — symétrique de d4
    'd6_a': ['p5', 'p6', 'd6_b', 'd2_a'],                           # (2200, 1000) ← miroir d4_a=['p4','p5','d4_b','d1_b']
    'd6_b': ['p2', 'p3', 'd6_a', 'd10_b'],                          # (2200,  600) ← miroir d4_b=['p1','p2','d4_a','d8_a']
    'd6_c': ['p3', 'p6', 'd6_d', 'd7_a', 'd7_b', 't8_a', 't2_b'],  # (2400,  800) ← miroir d4_d
    'd6_d': ['p2', 'p5', 'd6_c', 'd5_c', 't4_a', 't4_b'],          # (2000,  800) ← miroir d4_c

    # Points d'approche d1 — axe X (y+ bloqué zone interdite)
    'd1_a': ['p5', 'd1_b', 'd2_b', 'd5_a'],   # (1450, 1400)
    'd1_b': ['p4', 'p5', 'd1_a', 'd4_a'],     # (1050, 1400)

    # Points d'approche d2 — axe X (y+ bloqué zone interdite)
    'd2_a': ['p5', 'p6', 'd2_b', 'd6_a'],     # (1950, 1400)
    'd2_b': ['p5', 'd2_a', 'd1_a', 'd5_a'],   # (1550, 1400)

    # Points d'approche d3 — axe Y, bord gauche
    'd3_a': ['p4', 'd3_b', 't1_b', 't5_a','d4_d'],     # (175, 1000)
    'd3_b': ['p1', 'p7', 'd3_a', 't1_b', 't5_a', 'd4_d'],  # (175,  600)

    # Points d'approche d7 — axe Y, bord droit
    'd7_a': ['p6', 'd7_b', 't2_b', 't8_a', 'd6_c'],      # (2825, 1000)
    'd7_b': ['p3', 'p8', 'd7_a', 't2_b', 't8_a', 'd6_c'], # (2825,  600)

    # Points d'approche d8 — axe X, bord bas
    'd8_a': ['p1', 'p7', 'd8_b', 't6_b', 'd4_b'],        # (900,  175)
    'd8_b': ['p1', 'p7', 'd8_a', 't6_b'],        # (500,  175)

    # Points d'approche d9 — axe X, bord bas
    'd9_a': ['p2', 'd9_b', 't6_a', 't7_b', 'd5_b'],  # (1700, 175)
    'd9_b': ['p2', 'd9_a', 't6_a', 't7_b', 'd5_b'],  # (1300, 175)

    # Points d'approche d10 — axe X, bord bas
    'd10_a': ['p3', 'p8', 'd10_b', 't7_a'],      # (2500, 175)
    'd10_b': ['p3', 'p8', 'd10_a', 't7_a', 'd6_b'],   # (2100, 175)
}




########
### DÉFINITION DES CIBLES (TAS)
########

TARGETS = {
    'tas_1': ['t1_a', 't1_b'],
    'tas_2': ['t2_a', 't2_b'],
    'tas_3': ['t3_a', 't3_b'],
    'tas_4': ['t4_a', 't4_b'],
    'tas_5': ['t5_a'],
    'tas_6': ['t6_a', 't6_b'],
    'tas_7': ['t7_a', 't7_b'],
    'tas_8': ['t8_a'],
}


########
### ORDRE DE PRIORITÉ DES TAS
########

PRIORITY_ORDER = ['tas_4', 'tas_8', 'tas_6', 'tas_3', 'tas_5', 'tas_2', 'tas_7', 'tas_1']


########
### DÉFINITION DES CIBLES DÉPOSE (CACA)
########

# Tous les dépôts utilisent des points d'approche fixes.
# Le robot va du point d'approche A au point d'approche B en traversant la zone.
# DEPOTS_CIRCULAIRE = {'d4', 'd5', 'd6'}  # plus utilisé — approche circulaire abandonnée

TARGETS_DEPOT_CACA = {
    'd1':  ['d1_a', 'd1_b'],
    'd2':  ['d2_a', 'd2_b'],
    'd3':  ['d3_a', 'd3_b'],
    'd4':  ['d4_a', 'd4_b', 'd4_c', 'd4_d'],
    'd5':  ['d5_a', 'd5_b', 'd5_c', 'd5_d'],
    'd6':  ['d6_a', 'd6_b', 'd6_c', 'd6_d'],
    'd7':  ['d7_a', 'd7_b'],
    'd8':  ['d8_a', 'd8_b'],
    'd9':  ['d9_a', 'd9_b'],
    'd10': ['d10_a', 'd10_b'],
}
