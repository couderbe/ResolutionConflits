import evolutionDifferentielle
import numpy as np
from PyQt5.QtCore import QPoint

""" Paramètres Globaux """

N_avion = 10  ### Nombre d'avions
d = 9260  ### Distance de séparation (en mètres), correspondant à la norme de 5NM
FLIGHTS = []
T = 1800 ### Temps total en secondes, correspondant à 30 minutes.


""" Paramètres pour l'algorithme DE """

alphaMax = np.pi / 6  ### Angle maximal de la manoeuvre en radians
N_pop = 40  ### Nombre d'individus dans la population
CR = 0.05  ### "Change Rate": probabilité de réalisation de la mutation
F = 0.7  ### Facteur de mutation, doit être compris entre 0 et 2
BOUNDS = [(0, T), (0, 1), (-alphaMax, alphaMax)]  ### Bornes de alpha, t0 et theta avec t1=theta*((T-t0)/2):
### sert à vérifier que les individus de la population respectent ces limites après l'étape de cross-over.

""" Constantes (fonction des paramètres) calculées une fois pour toutes """
alMc = alphaMax ** 2
Tc = T ** 2


class Flight():

    # Cette classe crée un objet flight avec les attributs suivants:
    #    speed: la norme de la vitesse de l'avion.
    #    pointDepart: le point de départ de l'avion.
    #    angle0: l'angle que fait la trajectoire initiale de l'avion avec l'axe des abscisses.
    #        Ainsi en combinant "speed" et "angle0", on peut calculer le vecteur vitesse de l'avion.
    #    manoeuvre: la manoeuvre que fait l'avion (objet à 3 attributs, défini dans la classe Manoeuvre).
    #    dConflits: dictionnaire des conflits associés à l'avion. Les clés sont les autres avions avec lesquels
    #        il est en conflit, et les valeurs la liste des temps de début et de fin de chaque conflit.
    #    etat: attribut qui permet de savoir à quelle étape de la manoeuvre en est l'avion:
    #        0 = avant la manoeuvre; 1 = montée initiale; 2 = retour à la trajectoire; 3 = manoeuvre terminée.
    #        Initialisé à l'étape 0 (trajectoire initiale).

    def __init__(self, speed, pointDepart, angle0, manoeuvre):
        self.pointDepart = pointDepart
        self.angle0 = angle0
        self.manoeuvre = manoeuvre
        self.speed = np.dot(rotMatrix(self.angle0), np.array([speed, 0]))  # Un array numpy
        self.dConflits = {}  # dictionnaire des conflits, clés: les avions et valeurs: listes des temps de début et fin de conflits pour tous les moments où les avions sont en conflit
        self.etat = 0

    # Cette méthode renvoie 5 Qpoints correspondant respectivement: au début de la trajectoire, au début de la manoeuvre,
    # au début du retour à la trajectoire initiale, à l'endroit où l'avion récupère la trajectoire initiale, à la fin de la trajectoire
    def pointTrajectory(self):
        v = np.linalg.norm(self.speed)
        p0 = self.pointDepart
        p1 = p0 + QPoint(v * self.manoeuvre.t0 * np.cos(self.angle0),
                         v * self.manoeuvre.t0 * np.sin(self.angle0))
        p2 = p1 + QPoint(v * self.manoeuvre.t1 * np.cos(
            self.manoeuvre.angle + self.angle0),
                         v * self.manoeuvre.t1 * np.sin(
                             self.manoeuvre.angle + self.angle0))
        p3 = p2 + QPoint(v * self.manoeuvre.t1 * np.cos(
            -self.manoeuvre.angle + self.angle0),
                         v * self.manoeuvre.t1 * np.sin(
                             -self.manoeuvre.angle + self.angle0))
        p4 = p3 + QPoint(v * (T - self.manoeuvre.t0 - 2 * self.manoeuvre.t1) * np.cos(
            self.angle0),
                         v * (T - self.manoeuvre.t0 - 2 * self.manoeuvre.t1) * np.sin(
                             self.angle0))
        return [p0, p1, p2, p3, p4]

    # Cette méthode permet de générer suffisamment de points de la trajectoire pour déplacer ensuite les avions grâce à Qt
    def completeTrajectory(self, nbrPoint):
        intervalleTemps = T / nbrPoint
        resultat = [self.pointDepart]
        v = np.linalg.norm(self.speed)
        for k in range(1, nbrPoint):
            if k * intervalleTemps <= self.manoeuvre.t0:
                resultat.append(resultat[k - 1] + QPoint(intervalleTemps * v * np.cos(self.angle0),
                                                         intervalleTemps * v * np.sin(self.angle0)))
            elif k * intervalleTemps <= (self.manoeuvre.t0 + self.manoeuvre.t1):
                resultat.append(
                    resultat[k - 1] + QPoint(intervalleTemps * v * np.cos(self.angle0 + self.manoeuvre.angle),
                                             intervalleTemps * v * np.sin(self.angle0 + self.manoeuvre.angle)))
            elif k * intervalleTemps <= (self.manoeuvre.t0 + 2 * self.manoeuvre.t1):
                resultat.append(
                    resultat[k - 1] + QPoint(intervalleTemps * v * np.cos(self.angle0 - self.manoeuvre.angle),
                                             intervalleTemps * v * np.sin(self.angle0 - self.manoeuvre.angle)))
            else:
                resultat.append(resultat[k - 1] + QPoint(intervalleTemps * v * np.cos(self.angle0),
                                                         intervalleTemps * v * np.sin(self.angle0)))
        return resultat

    # Cette méthode permet de récupérer la liste de tous les temps de conflits
    def listeConflits(self):
        return self.dConflits.values()

    def __repr__(self):
        return 'Vitesse: {0} Depart: {1} Manoeuvre: {2} Angle0: {3}'.format(self.speed, self.pointDepart,
                                                                              self.manoeuvre, self.angle0 * 180 / np.pi)


class Manoeuvre():
    # Cette classe crée un objet "manoeuvre" représentant la trajectoire d'évitement d'un avion.
    # Elle dispose de 3 attributs:
    #   t0: le temps de début de manoeuvre
    #   t1: la durée de l'étape d'éloignement de la manoeuvre (au total la manoeuvre dure donc 2*t1)
    #   alpha: l'angle de déviation par rapport à la trajectoire initiale de l'avion.
    def __init__(self, t0, t1, angle):
        self.t0 = t0
        self.t1 = t1
        self.angle = angle

    # Ces méthodes permettent de réaliser des opérations entres manoeuvres
    # (utile si l'on effectue l'algorithme de DE sur une population de manoeuvres)
    def __add__(self, other):
        return Manoeuvre(self.t0 + other.t0, self.t1 + other.t1, self.angle + other.angle)

    def __sub__(self, other):
        return Manoeuvre(self.t0 - other.t0, self.t1 - other.t1, self.angle - other.angle)

    def __rmul__(self, other):
        return Manoeuvre(self.t0 * other, self.t1 * other, self.angle * other)

    def __repr__(self):
        return 't0: {0} t1: {1} angle: {2}'.format(self.t0, self.t1, self.angle * 180 / np.pi)

    # Cette méthode permet de convertir une manoeuvre en un array (vecteur numpy)
    def convertMtoA(self):
        if T - self.t0 != 0:
            return np.array([self.t0, (2 * self.t1) / (T - self.t0), self.angle])
        return np.array([self.t0, 0, self.angle])


# Cette fonction convertit un array (vecteur numpy) en une manoeuvre
def convertAtoM(manoeuvre):
    return Manoeuvre(manoeuvre[0], manoeuvre[1] * ((T - manoeuvre[0]) / 2), manoeuvre[2])


# Cette fonction permet de créer la population de listes de vecteurs à 3 dimensions (représentant chacun une manoeuvre)
# pour l'algorithme DE à partir de la fonction InitPop
def creaPop(Flights):
    global FLIGHTS
    FLIGHTS = Flights
    bounds_t0 = [BOUNDS[0] for k in range(N_avion)]
    bounds_theta = [BOUNDS[1] for k in range(N_avion)]
    bounds_alpha = [BOUNDS[2] for k in range(N_avion)]
    pop_alpha = evolutionDifferentielle.initPop(bounds_alpha, N_pop)
    pop_t0 = evolutionDifferentielle.initPop(bounds_t0, N_pop)
    pop_theta = evolutionDifferentielle.initPop(bounds_theta, N_pop)
    ManoeuvreInit = [flight.manoeuvre.convertMtoA() for flight in Flights]
    liste_manoeuvres = []
    liste_manoeuvres.append(ManoeuvreInit)  # le premier individu de la population est la situation initiale.
    for k in range(1, N_pop):
        eltMan = []
        for l in range(N_avion):
            manArray = np.array([pop_t0[k][l], pop_theta[k][l], pop_alpha[k][l]])
            eltMan.append(manArray)
        liste_manoeuvres.append(eltMan)
    return liste_manoeuvres


# Fonction de calcul du coût des manoeuvres de tous les avions
# Prend en paramètre Man une liste de manoeuvres (une pour chaque avion)
def cout():
    C_ang = 0
    C_time = 0
    for vol in FLIGHTS:
        C_ang += vol.manoeuvre.angle ** 2
        C_time += (vol.manoeuvre.t1) ** 2 + ((T - vol.manoeuvre.t0) ** 2)
    return C_ang / alMc + C_time / Tc


# Cette fonction calcule la durée cumulée de tous les conflits de tous les avions
def dureeConflit(liste_Conflits):
    duree = 0
    for val in liste_Conflits:
        if len(val) != 0:
            for i in val:
                for j in i:
                    duree += j[1] - j[0]
    return duree / (2 * T)


# Fonction permettant  d'obtenie la liste de tous les conflits pour tous les avions
def updateConflits():
    liste_Conflits = []
    for i in range(N_avion):
        FLIGHTS[i].dConflits = {}
    for i in range(N_avion):
        for j in range(i + 1, N_avion):
            conflit2a2(FLIGHTS[i], FLIGHTS[j])
        liste_Conflits.append(FLIGHTS[i].listeConflits())
    return liste_Conflits


# Fonction fitness:
# L'algorithme DE cherche à la maximiser.
# Elle va dans un premier temps éliminer les conflits, puis privilégiera les solutions qui réduisent la durée de manoeuvre.
# Tant qu'elle reste inférieure à 1/2: il y a encore des conflits.
# Elle prend en paramètre "Man" une liste de manoeuvres (une pour chaque avion)
def fitness(Man):
    for i, vol in enumerate(FLIGHTS):
        vol.manoeuvre = convertAtoM(Man[i])
    liste_Conflits = updateConflits()
    dureeConf = dureeConflit(liste_Conflits)
    if dureeConf > 10 ** (-10):
        return 1.0 / (2.0 + dureeConf)
    else:
        return 0.5 + 1.0 / (2 + cout())


# Fonction prenant un angle en paramètre et renvoyant la matrice de rotation directe de cet angle.
def rotMatrix(theta):
    return np.array([[np.cos(theta), -np.sin(theta)],
                     [np.sin(theta), np.cos(theta)]])


# Fonction qui calcule les temps de début et de fin de conflit entre deux avions (s'il y a conflit).
# On doit vérifier les conflits sur toutes les parties des trajectoires des deux avions.
def conflit2a2(f1, f2):
    # Dans un souci de clarté, on nomme toutes les variables utiles au calcul:
    ptdep1 = np.array([float(f1.pointDepart.x()), float(f1.pointDepart.y())])
    ptdep2 = np.array([float(f2.pointDepart.x()), float(f2.pointDepart.y())])
    v1 = f1.speed
    v2 = f2.speed
    t01 = f1.manoeuvre.t0
    alpha1 = f1.manoeuvre.angle
    t11 = f1.manoeuvre.t1
    t02 = f2.manoeuvre.t0
    alpha2 = f2.manoeuvre.angle
    t12 = f2.manoeuvre.t1

    # Pour éviter que les avions ne rentrent plusieurs fois dans un if d'etat, on utilise des compteurs.
    compteur1 = 0
    compteur2 = 0

    # Liste ordonnée de tous les angles permettant d'ajuster les vecteurs vitesses des avions
    # sur chaque portion de leur trajectoire
    angle1 = [alpha1, -2 * alpha1, alpha1]
    angle2 = [alpha2, -2 * alpha2, alpha2]

    # Liste des temps où l'un des avions change de direction, car il faut calculer les conflits sur
    # tous les segments temporels définis par ces valeurs.
    temps = sorted(
        [(0, None), (t01, f1), (t01 + t11, f1), (t01 + 2 * t11, f1), (t02, f2), (t02 + t12, f2), (t02 + 2 * t12, f2)], \
        key=lambda x: x[0])
    tOld = 0

    for (i, t) in enumerate(temps):
        tCurrent = t[0]
        dt = tCurrent - tOld
        ptdep2 += dt * v2
        ptdep1 += dt * v1
        flightChanging = t[1]
        if flightChanging != None:
            flightChanging.etat += 1
            if flightChanging == f1:
                v1 = np.dot(rotMatrix(angle1[compteur1]), v1)
                compteur1 += 1
            else:
                v2 = np.dot(rotMatrix(angle2[compteur2]), v2)
                compteur2 += 1

        # Dans notre modélisation, la composante [0] est la coordonnée en x et [1] celle en y
        a = (v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2

        b = 2 * ((ptdep1[0] - ptdep2[0]) * (v1[0] - v2[0]) +
                 (ptdep1[1] - ptdep2[1]) * (v1[1] - v2[1]))

        c = (ptdep1[0] - ptdep2[0]) ** 2 + (ptdep1[1] - ptdep2[1]) ** 2 - d ** 2

        racines = second_degre(a, b, c)
        if racines != None:
            tdeb = min(racines) + t[0]
            tfin = max(racines) + t[0]
            if i < len(temps) - 1:
                tiplus1 = temps[i + 1][0]
            else:
                tiplus1 = T

            tmax = max(tCurrent, min(tfin, tiplus1))
            tmin = max(tCurrent, min(tdeb, tiplus1))

            if f2 not in f1.dConflits.keys():
                f1.dConflits[f2] = []
                f2.dConflits[f1] = []

            if (tmin, tmax) not in f1.dConflits[f2]:
                f1.dConflits[f2].append((tmin, tmax))
                f2.dConflits[f1].append((tmin, tmax))

        tOld = tCurrent

    # Pour que les etats soient revenus à 0 pour les fois suivantes
    f1.etat = 0
    f2.etat = 0


# Fonction "maison" permettant de calculer les racines d'un polynôme du second degré (car numpy roots utilise les valeurs propres
# de la matrice dont le polynôme est son polynôme caractéristique -> coûteux en temps)
def second_degre(a, b, c):
    delta = b ** 2 - 4 * a * c
    if delta > 0:
        racine1 = (-b - np.sqrt(delta)) / (2 * a)
        racine2 = (-b + np.sqrt(delta)) / (2 * a)
        return [racine1, racine2]
    return None
