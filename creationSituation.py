# Situation première avec un cercle

from PyQt5 import QtWidgets
from PyQt5.QtCore import QPoint
from cmath import phase
import random

import probleme as pb
import numpy as np

def vitesseConstante (vitesse) :
    return [vitesse for k in range(pb.N_avion)]

def vitesseAleatoire(vitesse) :
    return [random.uniform(vitesse[0],vitesse[1]) for k in range(pb.N_avion)]

def cercle(m, RAYON_CERCLE, vitesse):
    return [pb.Flight(vitesse[k], QPoint(RAYON_CERCLE * np.cos(m * k),  RAYON_CERCLE * np.sin(m * k)),
                      np.pi + phase(complex( RAYON_CERCLE * np.cos(m * k), RAYON_CERCLE * np.sin(m * k))),
                      pb.Manoeuvre(pb.T, 0, 0)) for k in range(pb.N_avion)]


def cercle_deforme(m, RAYON_CERCLE, vitesse, epsilon):
    deformation = [random.uniform(- epsilon, epsilon) for i in range(pb.N_avion)]
    return [pb.Flight(vitesse[k], QPoint(RAYON_CERCLE * np.cos(m * k + deformation[k]),
                                  RAYON_CERCLE * np.sin(m * k + deformation[k])), np.pi + phase(
        complex(RAYON_CERCLE * np.cos(m * k + deformation[k]),
                RAYON_CERCLE * np.sin(m * k + deformation[k]))), pb.Manoeuvre(pb.T, 0, 0)) for k in
            range(pb.N_avion)]


def hasard(vitesse):
    L = []
    i = 0
    while i < pb.N_avion:
        val_x = random.uniform(0, 10)
        val_y = random.uniform(0, 10)
        val = [val_x, val_y]
        if val not in L:
            L.append(val)
            i += 1

    return [pb.Flight(vitesse, QPoint(L[k][0], L[k][1]), np.pi + complex(L[k][0], L[k][1]), pb.Manoeuvre(pb.T, 0, 0)) for k in range(pb.N_avion)]


