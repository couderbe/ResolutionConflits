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

def cercle(m, RAYON_CERCLE, liste_vitesse_avion):
    return [pb.Flight(liste_vitesse_avion[k], QPoint(RAYON_CERCLE * np.cos(m * k),  RAYON_CERCLE * np.sin(m * k)),
                      np.pi + phase(complex( RAYON_CERCLE * np.cos(m * k), RAYON_CERCLE * np.sin(m * k))),
                      pb.Manoeuvre(pb.T, 0, 0)) for k in range(pb.N_avion)]


def cercle_deforme(m, RAYON_CERCLE, liste_vitesse_avion, epsilon):
    deformation = [random.uniform(- epsilon, epsilon) for i in range(pb.N_avion)]
    return [pb.Flight(liste_vitesse_avion[k], QPoint(RAYON_CERCLE * np.cos(m * k + deformation[k]),
                                  RAYON_CERCLE * np.sin(m * k + deformation[k])), np.pi + phase(
        complex(RAYON_CERCLE * np.cos(m * k + deformation[k]),
                RAYON_CERCLE * np.sin(m * k + deformation[k]))), pb.Manoeuvre(pb.T, 0, 0)) for k in
            range(pb.N_avion)]


def hasard(liste_vitesse_avion):
    liste_angle = []
    val_x = -100000 + 200000 * random.random()
    val_y = -100000 + 200000 * random.random()
    position = [np.array ([val_x, val_y])]
    i = 1
    while i < pb.N_avion:
        val_x = -100000 + 200000*random.random()
        val_y = -100000 + 200000*random.random()
        angle = random.uniform(-np.pi/6,np.pi/6)
        val = np.array ([val_x, val_y])
        distance = np.linalg.norm(position[-1] - val)
        if distance >= pb.d :
            position.append(val)
            i += 1
    #print(position)
    for pos in position :
        if pos[0] >= 0 : #val de x
            if pos[1] >= 0 : #val de y"
                angle_hasard = (3*np.pi)/4 + ((np.pi/4)*random.random())
                liste_angle.append(angle_hasard)
            else :
                angle_hasard = np.pi/2 + ((np.pi/2) * random.random())
                liste_angle.append(angle_hasard)
        else:
            if pos[1] >= 0:
                angle_hasard = ((3 * np.pi) / 4)*random.random()
                liste_angle.append(angle_hasard)
            else :
                angle_hasard = (np.pi/2) * random.random()
                liste_angle.append(angle_hasard)
    #print(liste_angle)
    return [pb.Flight(liste_vitesse_avion[k], QPoint(position[k][0], position[k][1]), liste_angle[k], pb.Manoeuvre(pb.T, 0, 0)) for k in range(pb.N_avion)]

