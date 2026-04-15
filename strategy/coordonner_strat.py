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

# Distance d'approche pour les zones de dépose
dist_depose = 200

# Points d'approche des zones de dépose (c = caca)
# Suffixe : _a = +Y (haut), _b = -Y (bas), _c = +X (droite), _d = -X (gauche)

# d1 (1250, 1450)
#d1_c_a = (d1[0], d1[1] + dist_depose)   # (1250, 1650) → pas possible (terrain_pami_ninja)
d1_c_b = (d1[0], d1[1] - dist_depose)   # (1250, 1250)
d1_c_c = (d1[0] + dist_depose, d1[1])   # (1450, 1450)
d1_c_d = (d1[0] - dist_depose, d1[1])   # (1050, 1450)

# d2 (1750, 1450)
#d2_c_a = (d2[0], d2[1] + dist_depose)   # (1750, 1650) → pas possible (terrain_pami_ninja)
d2_c_b = (d2[0], d2[1] - dist_depose)   # (1750, 1250)
d2_c_c = (d2[0] + dist_depose, d2[1])   # (1950, 1450)
d2_c_d = (d2[0] - dist_depose, d2[1])   # (1550, 1450)

# d3 (100, 800)
d3_c_a = (d3[0], d3[1] + dist_depose)   # (100, 1000)
d3_c_b = (d3[0], d3[1] - dist_depose)   # (100, 600)
d3_c_c = (d3[0] + dist_depose, d3[1])   # (300, 800)
# d3_c_d = (d3[0] - dist_depose, d3[1]) # (-100, 800) → pas possible (x < 0)

# d4 (800, 800)
d4_c_a = (d4[0], d4[1] + dist_depose)   # (800, 1000)
d4_c_b = (d4[0], d4[1] - dist_depose)   # (800, 600)
d4_c_c = (d4[0] + dist_depose, d4[1])   # (1000, 800)
d4_c_d = (d4[0] - dist_depose, d4[1])   # (600, 800)

# d5 (1500, 800)
d5_c_a = (d5[0], d5[1] + dist_depose)   # (1500, 1000)
d5_c_b = (d5[0], d5[1] - dist_depose)   # (1500, 600)
d5_c_c = (d5[0] + dist_depose, d5[1])   # (1700, 800)
d5_c_d = (d5[0] - dist_depose, d5[1])   # (1300, 800)

# d6 (2200, 800)
d6_c_a = (d6[0], d6[1] + dist_depose)   # (2200, 1000)
d6_c_b = (d6[0], d6[1] - dist_depose)   # (2200, 600)
d6_c_c = (d6[0] + dist_depose, d6[1])   # (2400, 800)
d6_c_d = (d6[0] - dist_depose, d6[1])   # (2000, 800)

# d7 (2900, 800)
d7_c_a = (d7[0], d7[1] + dist_depose)   # (2900, 1000)
d7_c_b = (d7[0], d7[1] - dist_depose)   # (2900, 600)
# d7_c_c = (d7[0] + dist_depose, d7[1]) # (3100, 800) → pas possible (x > 3000)
d7_c_d = (d7[0] - dist_depose, d7[1])   # (2700, 800)

# d8 (700, 100)
d8_c_a = (d8[0], d8[1] + dist_depose)   # (700, 300)
# d8_c_b = (d8[0], d8[1] - dist_depose) # (700, -100) → pas possible (y < 0)
d8_c_c = (d8[0] + dist_depose, d8[1])   # (900, 100)
d8_c_d = (d8[0] - dist_depose, d8[1])   # (500, 100)

# d9 (1500, 100)
d9_c_a = (d9[0], d9[1] + dist_depose)   # (1500, 300)
# d9_c_b = (d9[0], d9[1] - dist_depose) # (1500, -100) → pas possible (y < 0)
d9_c_c = (d9[0] + dist_depose, d9[1])   # (1700, 100)
d9_c_d = (d9[0] - dist_depose, d9[1])   # (1300, 100)

# d10 (2300, 100)
d10_c_a = (d10[0], d10[1] + dist_depose)   # (2300, 300)
# d10_c_b = (d10[0], d10[1] - dist_depose) # (2300, -100) → pas possible (y < 0)
d10_c_c = (d10[0] + dist_depose, d10[1])   # (2500, 100)
d10_c_d = (d10[0] - dist_depose, d10[1])   # (2100, 100)




######## Points d'approche des zones de dépose (b = bouche)
# Suffixe : _a = +Y (haut), _b = -Y (bas), _c = +X (droite), _d = -X (gauche)
dist_bouche = 100

# d1 (1250, 1450)
#d1_b_a = (d1[0], d1[1] + dist_bouche)     # (1250, 1550) # pas possible pour le robot
d1_b_b = (d1[0], d1[1] - dist_bouche)     # (1250, 1350)
d1_b_c = (d1[0] + dist_bouche, d1[1])     # (1350, 1450)
d1_b_d = (d1[0] - dist_bouche, d1[1])     # (1150, 1450)

# d2 (1750, 1450)
#d2_b_a = (d2[0], d2[1] + dist_bouche)     # (1750, 1550) # pas possible pour le robot
d2_b_b = (d2[0], d2[1] - dist_bouche)     # (1750, 1350)
d2_b_c = (d2[0] + dist_bouche, d2[1])     # (1850, 1450)
d2_b_d = (d2[0] - dist_bouche, d2[1])     # (1650, 1450)

# d3 (100, 800)
d3_b_a = (d3[0], d3[1] + dist_bouche)     # (100, 900)
d3_b_b = (d3[0], d3[1] - dist_bouche)     # (100, 700)
d3_b_c = (d3[0] + dist_bouche, d3[1])     # (200, 800)
#d3_b_d = (d3[0] - dist_bouche, d3[1])     # (0, 800) # pas possible pour le robot

# d4 (800, 800)
d4_b_a = (d4[0], d4[1] + dist_bouche)     # (800, 900)
d4_b_b = (d4[0], d4[1] - dist_bouche)     # (800, 700)
d4_b_c = (d4[0] + dist_bouche, d4[1])     # (900, 800)
d4_b_d = (d4[0] - dist_bouche, d4[1])     # (700, 800)

# d5 (1500, 800)
d5_b_a = (d5[0], d5[1] + dist_bouche)     # (1500, 900)
d5_b_b = (d5[0], d5[1] - dist_bouche)     # (1500, 700)
d5_b_c = (d5[0] + dist_bouche, d5[1])     # (1600, 800)
d5_b_d = (d5[0] - dist_bouche, d5[1])     # (1400, 800)

# d6 (2200, 800)
d6_b_a = (d6[0], d6[1] + dist_bouche)     # (2200, 900)
d6_b_b = (d6[0], d6[1] - dist_bouche)     # (2200, 700)
d6_b_c = (d6[0] + dist_bouche, d6[1])     # (2300, 800)
d6_b_d = (d6[0] - dist_bouche, d6[1])     # (2100, 800)

# d7 (2900, 800)
d7_b_a = (d7[0], d7[1] + dist_bouche)     # (2900, 900)
d7_b_b = (d7[0], d7[1] - dist_bouche)     # (2900, 700)
#d7_b_c = (d7[0] + dist_bouche, d7[1])     # (3000, 800) # pas possible pour le robot
d7_b_d = (d7[0] - dist_bouche, d7[1])     # (2800, 800)

# d8 (700, 100)
d8_b_a = (d8[0], d8[1] + dist_bouche)     # (700, 200)
#d8_b_b = (d8[0], d8[1] - dist_bouche)     # (700, 0) # pas possible pour le robot
d8_b_c = (d8[0] + dist_bouche, d8[1])     # (800, 100)
d8_b_d = (d8[0] - dist_bouche, d8[1])     # (600, 100)

# d9 (1500, 100)
d9_b_a = (d9[0], d9[1] + dist_bouche)     # (1500, 200)
#d9_b_b = (d9[0], d9[1] - dist_bouche)     # (1500, 0)# pas possible pour le robot
d9_b_c = (d9[0] + dist_bouche, d9[1])     # (1600, 100)
d9_b_d = (d9[0] - dist_bouche, d9[1])     # (1400, 100)

# d10 (2300, 100)
d10_b_a = (d10[0], d10[1] + dist_bouche)  # (2300, 200)
#d10_b_b = (d10[0], d10[1] - dist_bouche)  # (2300, 0) # pas possible pour le robot
d10_b_c = (d10[0] + dist_bouche, d10[1])  # (2400, 100)
d10_b_d = (d10[0] - dist_bouche, d10[1])  # (2200, 100)


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
#p10 = (x4, y_ligne_max)  # (1700, 1150)
#p11 = (x5, y_ligne_max)  # (2050, 1150)
#p12 = (x6, y_ligne_max)  # (2450, 1150)


########
### DICTIONNAIRE DES POINTS
########

POINTS = {
    # Points de passage (ligne basse)
    'p1': p1, 'p2': p2, 'p3': p3, 
    # Points de passage (ligne haute)
    'p4': p4, 'p5': p5, 'p6': p6,
    # Points d'approche tas
    't1_a': t1_a, 't1_b': t1_b,
    't2_a': t2_a, 't2_b': t2_b,
    't3_a': t3_a, 't3_b': t3_b,
    't4_a': t4_a, 't4_b': t4_b,
    't5_a': t5_a, #'t5_b': t5_b,
    't6_a': t6_a, 't6_b': t6_b,
    't7_a': t7_a, 't7_b': t7_b,
    't8_a': t8_a, #'t8_b': t8_b,
}


########
### GRAPHE DES CONNEXIONS
########
# Ce graphe détermine quels points sont reliés entre eux

GRAPH = {
    # Ligne basse (y=500) - connexions horizontales
    'p1': ['p2', 't6_b', 't5_a', 't3_b', 't1_b'],  
    'p2': ['p1', 'p3', 't3_a', 't4_b', 't7_b', 't6_a'],  
    'p3': ['p2', 't8_a', 't4_a', 't7_a','t2_b'], 

    # Ligne haute (y=1150) - connexions horizontales
    'p4': ['p5', 't1_b', 't5_a', 't1_a', 't3_b'],  
    'p5': ['p4', 'p6', 't3_a', 't4_b', ], 
    'p6': ['p5', 't2_b', 't8_a', 't2_a', 't4_a'],  

    # Points d'approche tas 1
    't1_a': ['p4'],  
    't1_b': ['t5_a', 'p4', 't3_b', 'p1'],  # t1_b (bas) connecté à t1_a, p1, p7

    # Points d'approche tas 2 
    't2_a': ['p6'],
    't2_b': ['t8_a', 't4_a', 'p6','p3'],  # t2_b (bas) connecté à t2_a, p12

    # Points d'approche tas 3
    't3_a': ['t4_b', 'p5', 'p2'],  # t3_a (droite) connecté à t3_b, p9
    't3_b': ['p1', 'p4', 't1_b', 't5_a'],  # t3_b (gauche) connecté à t3_a, p2, p8

    # Points d'approche tas 4 
    't4_a': ['p3', 'p6', 't8_a', 't2_b'],  # t4_a (droite) connecté à t4_b, p11
    't4_b': ['t3_a', 'p5', 'p2'], # t4_b (gauche) connecté à t4_a, p5, p10

    # Points d'approche tas 5 
    't5_a': ['t1_b', 'p4', 't3_b', 'p1'],  # t5_a (haut) connecté à t5_b, p1
    #'t5_b': ['t5_a'],  # t5_b (bas) connecté à t5_a

    # Points d'approche tas 6 
    't6_a': ['t7_b', 'p2'],  # t6_a (droite) connecté à t6_b, p3
    't6_b': ['p1'],  # t6_b (gauche) connecté à t6_a, p2

    # Points d'approche tas 7
    't7_a': ['p3'],  # t7_a (droite) connecté à t7_b, p5
    't7_b': ['t6_a', 'p2'],  # t7_b (gauche) connecté à t7_a, p4

    # Points d'approche tas 8 
    't8_a': ['t2_b', 'p3', 'p6', 't4_a'],  # t8_a (haut) connecté à t8_b, p12
    #'t8_b': ['t8_a', 'p6'],  # t8_b (bas) connecté à t8_a, p6
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
