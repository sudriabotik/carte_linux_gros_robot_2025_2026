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
dist_tas = 200

# En fonction des tas, cette distance doit être ajoutée en x ou en y :
# tas : 1, 2, 5, 8 la distance doit être ajoutée en y
# tas : 3, 4, 6, 7 la distance doit être ajoutée en x

# Points d'approche pour tas 1, 2, 5, 8 (ajout en Y)
t1_a = (tas_1[0], tas_1[1] + dist_tas)  # (175, 1400)
t1_b = (tas_1[0], tas_1[1] - dist_tas)  # (175, 1000)
t2_a = (tas_2[0], tas_2[1] + dist_tas)  # (2825, 1400)
t2_b = (tas_2[0], tas_2[1] - dist_tas)  # (2825, 1000)
t5_a = (tas_5[0], tas_5[1] + dist_tas)  # (175, 600)
t5_b = (tas_5[0], tas_5[1] - dist_tas)  # (175, 200)
t8_a = (tas_8[0], tas_8[1] + dist_tas)  # (2825, 600)
t8_b = (tas_8[0], tas_8[1] - dist_tas)  # (2825, 200)

# Points d'approche pour tas 3, 4, 6, 7 (ajout en X)
t3_a = (tas_3[0] + dist_tas, tas_3[1])  # (1350, 800)
t3_b = (tas_3[0] - dist_tas, tas_3[1])  # (950, 800)
t4_a = (tas_4[0] + dist_tas, tas_4[1])  # (2050, 800)
t4_b = (tas_4[0] - dist_tas, tas_4[1])  # (1650, 800)
t6_a = (tas_6[0] + dist_tas, tas_6[1])  # (1300, 175)
t6_b = (tas_6[0] - dist_tas, tas_6[1])  # (900, 175)
t7_a = (tas_7[0] + dist_tas, tas_7[1])  # (2100, 175)
t7_b = (tas_7[0] - dist_tas, tas_7[1])  # (1700, 175)

#########
### ZONE DE DÉPOSE
########

# On va implémenter cela par la suite


########
### POINTS DE PASSAGE
########

y_ligne_min = 500
y_ligne_max = 1150

x1 = 700
x2 = 950
x3 = 1300
x4 = 1700
x5 = 2050
x6 = 2450

p1 = (x1, y_ligne_min)   # (700, 500)
p2 = (x2, y_ligne_min)   # (950, 500)
p3 = (x3, y_ligne_min)   # (1300, 500)
p4 = (x4, y_ligne_min)   # (1700, 500)
p5 = (x5, y_ligne_min)   # (2050, 500)
p6 = (x6, y_ligne_min)   # (2450, 500)
p7 = (x1, y_ligne_max)   # (700, 1150)
p8 = (x2, y_ligne_max)   # (950, 1150)
p9 = (x3, y_ligne_max)   # (1300, 1150)
p10 = (x4, y_ligne_max)  # (1700, 1150)
p11 = (x5, y_ligne_max)  # (2050, 1150)
p12 = (x6, y_ligne_max)  # (2450, 1150)


########
### DICTIONNAIRE DES POINTS
########

POINTS = {
    # Points de passage (ligne basse)
    'p1': p1, 'p2': p2, 'p3': p3, 'p4': p4, 'p5': p5, 'p6': p6,
    # Points de passage (ligne haute)
    'p7': p7, 'p8': p8, 'p9': p9, 'p10': p10, 'p11': p11, 'p12': p12,
    # Points d'approche tas
    't1_a': t1_a, 't1_b': t1_b,
    't2_a': t2_a, 't2_b': t2_b,
    't3_a': t3_a, 't3_b': t3_b,
    't4_a': t4_a, 't4_b': t4_b,
    't5_a': t5_a, 't5_b': t5_b,
    't6_a': t6_a, 't6_b': t6_b,
    't7_a': t7_a, 't7_b': t7_b,
    't8_a': t8_a, 't8_b': t8_b,
}


########
### GRAPHE DES CONNEXIONS
########
# Ce graphe détermine quels points sont reliés entre eux

GRAPH = {
    # Ligne basse (y=500) - connexions horizontales
    'p1': ['p2', 't1_b', 't5_a'],  # p1 connecté à p2, proche de t1_b et t5_a
    'p2': ['p1', 'p3', 't3_b', 't6_b'],  # p2 connecté à p1, p3, proche de t3_b et t6_b
    'p3': ['p2', 'p4', 't6_a'],  # p3 connecté à p2, p4, proche de t6_a
    'p4': ['p3', 'p5', 't7_b'],  # p4 connecté à p3, p5, proche de t7_b
    'p5': ['p4', 'p6', 't4_b', 't7_a'],  # p5 connecté à p4, p6, proche de t4_b et t7_a
    'p6': ['p5', 't8_b'],  # p6 connecté à p5, proche de t8_b

    # Ligne haute (y=1150) - connexions horizontales
    'p7': ['p8', 't1_b'],  # p7 connecté à p8, proche de t1_b
    'p8': ['p7', 'p9', 't3_b'],  # p8 connecté à p7, p9, proche de t3_b
    'p9': ['p8', 'p10', 't3_a'],  # p9 connecté à p8, p10, proche de t3_a
    'p10': ['p9', 'p11', 't4_b'],  # p10 connecté à p9, p11, proche de t4_b
    'p11': ['p10', 'p12', 't4_a'],  # p11 connecté à p10, p12, proche de t4_a
    'p12': ['p11', 't2_b', 't8_a'],  # p12 connecté à p11, proche de t2_b et t8_a

    # Points d'approche tas 1 (x=175, y=1000-1400)
    't1_a': ['t1_b', 't2_a'],  # t1_a (haut) connecté à t1_b
    't1_b': ['t1_a', 'p1', 'p7'],  # t1_b (bas) connecté à t1_a, p1, p7

    # Points d'approche tas 2 (x=2825, y=1000-1400)
    't2_a': ['t2_b', 't1_a'],  # t2_a (haut) connecté à t2_b
    't2_b': ['t2_a', 'p12'],  # t2_b (bas) connecté à t2_a, p12

    # Points d'approche tas 3 (x=950-1350, y=800)
    't3_a': ['t3_b', 'p9'],  # t3_a (droite) connecté à t3_b, p9
    't3_b': ['t3_a', 'p2', 'p8'],  # t3_b (gauche) connecté à t3_a, p2, p8

    # Points d'approche tas 4 (x=1650-2050, y=800)
    't4_a': ['t4_b', 'p11'],  # t4_a (droite) connecté à t4_b, p11
    't4_b': ['t4_a', 'p5', 'p10'],  # t4_b (gauche) connecté à t4_a, p5, p10

    # Points d'approche tas 5 (x=175, y=200-600)
    't5_a': ['t5_b', 'p1'],  # t5_a (haut) connecté à t5_b, p1
    't5_b': ['t5_a'],  # t5_b (bas) connecté à t5_a

    # Points d'approche tas 6 (x=900-1300, y=175)
    't6_a': ['t6_b', 'p3'],  # t6_a (droite) connecté à t6_b, p3
    't6_b': ['t6_a', 'p2'],  # t6_b (gauche) connecté à t6_a, p2

    # Points d'approche tas 7 (x=1700-2100, y=175)
    't7_a': ['t7_b', 'p5'],  # t7_a (droite) connecté à t7_b, p5
    't7_b': ['t7_a', 'p4'],  # t7_b (gauche) connecté à t7_a, p4

    # Points d'approche tas 8 (x=2825, y=200-600)
    't8_a': ['t8_b', 'p12'],  # t8_a (haut) connecté à t8_b, p12
    't8_b': ['t8_a', 'p6'],  # t8_b (bas) connecté à t8_a, p6
}


########
### DÉFINITION DES CIBLES (TAS)
########

TARGETS = {
    'tas_1': ['t1_a', 't1_b'],
    'tas_2': ['t2_a', 't2_b'],
    'tas_3': ['t3_a', 't3_b'],
    'tas_4': ['t4_a', 't4_b'],
    'tas_5': ['t5_a', 't5_b'],
    'tas_6': ['t6_a', 't6_b'],
    'tas_7': ['t7_a', 't7_b'],
    'tas_8': ['t8_a', 't8_b'],
}


########
### ORDRE DE PRIORITÉ DES TAS
########

PRIORITY_ORDER = ['tas_4', 'tas_8', 'tas_6', 'tas_3', 'tas_5', 'tas_2', 'tas_7', 'tas_1']
