#
# Ce module permet de créer différentes configurations de départ, où les avions sont placés:
#   - régulièrement autour d'un cercle
#   - autour d'un cercle, mais avec quelques variations de rayon et de régularité (on perturbe le rayon, et l'angle)
#   - aléatoirement dans la fenêtre d'observation
#
# Les vitesses des avions peuvent être toutes similaires ou différentes, comprises aléatoirement entre deux valeurs.

from PyQt5 import QtWidgets
from PyQt5.QtCore import QPoint
from cmath import phase
import random

import constantes as ct
import probleme as pb
import numpy as np
BORNE_MIN = -100000
AMPLITUDE = 200000


def vitesseConstante (vitesse) :
    return [vitesse for k in range(ct.N_avion)]

def vitesseAleatoire(vitesse) :
    return [random.uniform(vitesse[0],vitesse[1]) for k in range(ct.N_avion)]

def cercle(m, RAYON_CERCLE, liste_vitesse_avion):
    return [pb.Flight(liste_vitesse_avion[k], QPoint(RAYON_CERCLE * np.cos(m * k),  RAYON_CERCLE * np.sin(m * k)),
                      np.pi + phase(complex( RAYON_CERCLE * np.cos(m * k), RAYON_CERCLE * np.sin(m * k))),
                      pb.Manoeuvre(ct.T, 0, 0)) for k in range(ct.N_avion)]


def cercle_deforme(m, RAYON_CERCLE, liste_vitesse_avion, epsilon):
    deformation = [random.uniform(- epsilon, epsilon) for i in range(ct.N_avion)]
    return [pb.Flight(liste_vitesse_avion[k], QPoint(RAYON_CERCLE * np.cos(m * k + deformation[k]),
                                  RAYON_CERCLE * np.sin(m * k + deformation[k])), np.pi + phase(
        complex(RAYON_CERCLE * np.cos(m * k + deformation[k]),
                RAYON_CERCLE * np.sin(m * k + deformation[k]))), pb.Manoeuvre(ct.T, 0, 0)) for k in
            range(ct.N_avion)]


def hasard(liste_vitesse_avion):
    liste_angle = []
    val_x = BORNE_MIN+ AMPLITUDE * random.random()
    val_y = BORNE_MIN + AMPLITUDE * random.random()
    position = [np.array ([val_x, val_y])]
    i = 1
    while i < pb.N_avion:
        val_x = BORNE_MIN + AMPLITUDE*random.random()
        val_y = BORNE_MIN + AMPLITUDE*random.random()
        angle = random.uniform(-np.pi/6,np.pi/6)
        val = np.array ([val_x, val_y])

        # Cette condition sert à éliminer les situations où les avions sont en conflit dès le départ,
        # ce qui serait irrésoluble avec une manoeuvre:
        pas_erreur = True
        for pos in position :
            distance = np.linalg.norm(pos - val)
            if distance <= ct.d :
                pas_erreur = False
        if pas_erreur :
            position.append(val)
            i += 1
    # Cette boucle nous permet de définir l'angle de la trajectoire initiale de manière à ce que les avions se croisent
    # et engendre donc une situation de départ avec des conflits.
    for pos in position :
        if pos[0] >= 0 : # Valeur de la coordonnée x de l'avion
            if pos[1] >= 0 : # Valeur de la coordonnée y de l'avion
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
    return [pb.Flight(liste_vitesse_avion[k], QPoint(position[k][0], position[k][1]), liste_angle[k], pb.Manoeuvre(ct.T, 0, 0)) for k in range(ct.N_avion)]

