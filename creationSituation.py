# Situation première avec un cercle

from PyQt5 import QtWidgets
from PyQt5.QtCore import QPoint
from cmath import phase
import random

import probleme as pb
import numpy as np


def cercle(m, RAYON_CERCLE, v):
    return [pb.Flight(250, QPoint(v[k] * RAYON_CERCLE * np.cos(m * k), v[k] * RAYON_CERCLE * np.sin(m * k)),
                      np.pi + phase(complex(v[k] * RAYON_CERCLE * np.cos(m * k), v[k] * RAYON_CERCLE * np.sin(m * k))),
                      pb.Manoeuvre(pb.T, 0, 0)) for k in range(pb.N_avion)]


def cercle_deforme(m, RAYON_CERCLE, v, epsilon):
    deformation = [random.uniform(- epsilon, epsilon) for i in range(pb.N_avion)]
    return [pb.Flight(250, QPoint(v[k] * RAYON_CERCLE * np.cos(m * k + deformation[k]),
                                  v[k] * RAYON_CERCLE * np.sin(m * k + deformation[k])), np.pi + phase(
        complex(v[k] * RAYON_CERCLE * np.cos(m * k + deformation[k]),
                v[k] * RAYON_CERCLE * np.sin(m * k + deformation[k]))), pb.Manoeuvre(pb.T, 0, 0)) for k in
            range(pb.N_avion)]


def hasard():
    L = []
    i = 0
    while i < pb.N_avion:
        val_x = random.uniform(2, 10)
        val_y = random.uniform(2, 10)
        val = (val_x, val_y)
        if val not in L:
            L.append(val)
            i += 1
    print(L)
    return [pb.Flight(250, QPoint(L[k][0], L[k][1]), np.pi + complex(L[k][0], L[k][1]), pb.Manoeuvre(pb.T, 0, 0)) for k
            in range(pb.N_avion)]
