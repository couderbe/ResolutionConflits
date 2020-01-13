import numpy as np

### ---------- CONSTANTES ---------- ###

"""Constantes globales"""
TYPE_FCT = "Calcul"
N_avion = 10  ### Nombre d'avions
m = 2 * 3.14159 / N_avion
RAYON_CERCLE = 185200 # Rayon du cercle en mètres, correpondant à 100 NM
FICHIER = "Results/"
REPERTOIRE_FITNESS = "FitnessEvolution/"
T = 1800 ### Temps total en secondes, correspondant à 30 minutes.
d = 9260  ### Distance de séparation (en mètres), correspondant à la norme de 5NM

"""Paramètres pour la situation de départ"""
EPSILON = 0.8
VITESSE = 250

""" Paramètres pour l'algorithme DE """
ITERATIONS = 100
alphaMax = np.pi / 6  ### Angle maximal de la manoeuvre en radians
N_pop = 40  ### Nombre d'individus dans la population
CR = 0.05  ### "Change Rate": probabilité de réalisation de la mutation
F = 0.7  ### Facteur de mutation, doit être compris entre 0 et 2
BOUNDS = [(0, T), (0, 1), (-alphaMax, alphaMax)]  ### Bornes de alpha, t0 et theta avec t1=theta*((T-t0)/2):
### sert à vérifier que les individus de la population respectent ces limites après l'étape de cross-over.

""" Constantes (fonction des paramètres) calculées une fois pour toutes """
alMc = alphaMax ** 2
Tc = T ** 2

def recalculConsts():
    global m,Tc,BOUNDS
    m = 2 * 3.14159 / N_avion
    BOUNDS = [(0, T), (0, 1), (-alphaMax, alphaMax)]
    Tc = T ** 2

def f_N_avion(val):
    global N_avion
    N_avion = int(val)

def f_RAYON_CERCLE(val):
    global RAYON_CERCLE
    RAYON_CERCLE = int(val)

def f_FICHIER(val):
    global FICHIER
    FICHIER = str(val)

def f_REPERTOIRE_FITNESS(val):
    global REPERTOIRE_FITNESS
    REPERTOIRE_FITNESS = str(val)

def f_T(val):
    global T
    T = int(val)

def f_d(val):
    global d
    d = int(val)

def f_EPSILON(val):
    global EPSILON
    EPSILON = int(val)

def f_VITESSE(val):
    global VITESSE
    VITESSE = int(val)

def f_ITERATIONS(val):
    global ITERATIONS
    ITERATIONS = int(val)

def f_N_pop(val):
    global N_pop
    N_pop = int(val)

def f_CR(val):
    global CR
    CR = int(val)

def f_F(val):
    global F
    F = int(val)

def f_TYPE_FCT(val):
    global TYPE_FCT
    TYPE_FCT = str(val)

dictParam = {'na':f_N_avion,'rc':f_RAYON_CERCLE,'file':f_FICHIER,'rf':f_REPERTOIRE_FITNESS,'t':f_T,'d':f_d,'eps':f_EPSILON,'v':f_VITESSE,'i':f_ITERATIONS,'np':f_N_pop,'cr':f_CR,'f':f_F,'tf':f_TYPE_FCT}
