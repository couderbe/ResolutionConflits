import numpy as np
import argparse

### ---------- CONSTANTES ---------- ###

    # dictParam = {'na':N_avion,'rc':f_RAYON_CERCLE,'file':f_FICHIER,'rf':f_REPERTOIRE_FITNESS,'t':f_T,
    # 'd':f_d,'eps':f_EPSILON,'v':f_VITESSE,'i':f_ITERATIONS,'np':f_N_pop,'cr':f_CR,'f':f_F,'tf':f_TYPE_FCT}
parser = argparse.ArgumentParser()
parser.add_argument("-na",type=int,default=10)
parser.add_argument("-rc",type=int,default=185200)
parser.add_argument("-rep", type=str, default= "Results/")
parser.add_argument("-rf", type=str, default="FitnessEvolution/")
parser.add_argument("-t", type=int, default=1800)
parser.add_argument("-d", type=int, default=9260)
parser.add_argument("-eps", type=float, default=0.8)
parser.add_argument("-v",default=250)
parser.add_argument("-i", type=int, default=250)
parser.add_argument("-np", type=int, default=40)
parser.add_argument("-cr", type=float, default=0.05)
parser.add_argument("-f", type=float, default=0.7)
parser.add_argument("-tf",type=int, default=0,help= "Configuration de départ des avions: 0:cercle  1:cercle déformé, 2:répartition pseudo-aléatoire ")
parser.add_argument("-file",default=None)
parser.add_argument("-st",type=int,default=0,help="Configuration des vitesses: 0:constantes 1:pseudo-aléatoire")
args = parser.parse_args()
"""Constantes globales"""
FILE = args.file
SPEED_TYPE = args.st
TYPE_FCT = args.tf
N_avion = args.na  ### Nombre d'avions
m = 2 * 3.14159 / N_avion
RAYON_CERCLE = args.rc # Rayon du cercle en mètres, correpondant à 100 NM
FICHIER = args.rep
REPERTOIRE_FITNESS = args.rf
T = args.t ### Temps total en secondes, correspondant à 30 minutes.
d = args.d  ### Distance de séparation (en mètres), correspondant à la norme de 5NM

"""Paramètres pour la situation de départ"""
EPSILON = args.eps
VITESSE = args.v

""" Paramètres pour l'algorithme DE """
ITERATIONS = args.i
alphaMax = np.pi / 6  ### Angle maximal de la manoeuvre en radians
N_pop = args.np  ### Nombre d'individus dans la population
CR = args.cr  ### "Change Rate": probabilité de réalisation de la mutation
F = args.f  ### Facteur de mutation, doit être compris entre 0 et 2
BOUNDS = [(0, T), (0, 1), (-alphaMax, alphaMax)]  ### Bornes de alpha, t0 et theta avec t1=theta*((T-t0)/2):
### sert à vérifier que les individus de la population respectent ces limites après l'étape de cross-over.

""" Constantes (fonction des paramètres) calculées une fois pour toutes """
alMc = alphaMax ** 2
Tc = T ** 2

#dictParam = {'na':N_avion,'rc':f_RAYON_CERCLE,'file':f_FICHIER,'rf':f_REPERTOIRE_FITNESS,'t':f_T,'d':f_d,'eps':f_EPSILON,'v':f_VITESSE,'i':f_ITERATIONS,'np':f_N_pop,'cr':f_CR,'f':f_F,'tf':f_TYPE_FCT}
