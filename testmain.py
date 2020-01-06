import testDE
import numpy as np
import radarview
from cmath import phase
from PyQt5.QtCore import QPoint
import time

""" Paramètres Globaux """

N_avion = 10 # Nombre d'avions
d = 5000 #5 #Distance de séparation
FLIGHTS = []

""" Paramètres pour DE """
T = 240  # Temps total
alphaMax = np.pi / 6
N_pop=50
BOUNDS = [(0,T), (0,1), (-alphaMax, alphaMax)] # bornes de alpha, t0 et theta avec t1=theta*((T-t0)/2)
CR = 0.5
F = 0.7

""" Constantes (fonction des paramètres) calculées une fois pour toutes """
alMc = alphaMax ** 2
Tc = T ** 2


class Flight():
    def __init__(self, speed, pointDepart, angle0, manoeuvre):
        self.pointDepart = pointDepart
        self.angle0 = angle0
        self.manoeuvre = manoeuvre
        self.speed = np.dot(np.array([speed,0]),rotMatrix(self.angle0)) #Un array numpy
        self.dConflits = {}#dictionnaire des conflits, clés: les avions et valeurs: listes des temps de début et fin de conflits pour tous les moments où les avions sont en conflit
        self.etat = 0


    # Permet de savoir à quelle étape de la manoeuvre en est l'avion: 0=avant la manoeuvre; 1= montée initiale; 2= retour à la trajectoire;3 manoeuvre
    # terminée. Initialisé à etape 0 (trajectoire initiale)

    # return 5 QPoints qui sont debut,fin et cassures de la trajectoire
    # angles en radians
    def pointTrajectory(self):
        v = np.linalg.norm(self.speed)
        p0 = self.pointDepart
        p1 = p0 + QPoint(v * self.manoeuvre.t0 * np.cos(self.angle0),
                         v * self.manoeuvre.t0 * np.sin(self.angle0))
        p2 = p1 + QPoint(v * self.manoeuvre.t1 * np.cos(
            self.manoeuvre.angle + self.angle0),
                         v * self.manoeuvre.t1 * np.sin(
                             self.manoeuvre.angle + self.angle0))
        p3 = p2 + QPoint(v * self.manoeuvre.t1* np.cos(
            -self.manoeuvre.angle + self.angle0),
                         v * self.manoeuvre.t1 * np.sin(
                             -self.manoeuvre.angle + self.angle0))
        p4 = p3 + QPoint(v * (T - self.manoeuvre.t0 - 2 * self.manoeuvre.t1) * np.cos(
            self.angle0),
                         v * (T - self.manoeuvre.t0 - 2 * self.manoeuvre.t1 )* np.sin(
                             self.angle0))
        return [p0,p1,p2,p3,p4]


    ## Fonction en cours qui doit donner une liste de plein de points de la trajectoire pour dépacer ensite les avion grace à Qt
    def completeTrajectory(self,nbrPoint):
        intervalleTemps = T/nbrPoint
        resultat = [self.pointDepart]
        v = np.linalg.norm(self.speed)
        for k in range(1,nbrPoint):
            if k*intervalleTemps <= self.manoeuvre.t0:
                resultat.append(resultat[k - 1] + QPoint(intervalleTemps*v*np.cos(self.angle0),
                                                       intervalleTemps*v*np.sin(self.angle0)))
            elif k*intervalleTemps <= (self.manoeuvre.t0 + self.manoeuvre.t1):
                resultat.append(resultat[k - 1] + QPoint(intervalleTemps * v * np.cos(self.angle0 + self.manoeuvre.angle),
                                                         intervalleTemps * v* np.sin(self.angle0 + self.manoeuvre.angle)))
            elif k * intervalleTemps <= (self.manoeuvre.t0 + 2*self.manoeuvre.t1):
                resultat.append(resultat[k - 1] + QPoint(intervalleTemps * v* np.cos(self.angle0 - self.manoeuvre.angle),
                                                         intervalleTemps * v * np.sin(self.angle0 - self.manoeuvre.angle)))
            else:
                resultat.append(resultat[k - 1] + QPoint(intervalleTemps * v * np.cos(self.angle0),
                                                         intervalleTemps * v * np.sin(self.angle0)))
        return resultat


    def listeConflits(self):
        return self.dConflits.values()

    def __repr__(self):
        return ("Vitesse:" + " " + str(self.speed) + " " + "Depart:" + str(self.pointDepart) + " Manoeuvre:" + str(self.manoeuvre) + " Angle0:" + str(self.angle0*180/np.pi))


class Manoeuvre():
    def __init__(self, t0,t1,angle):
        self.t0 = t0
        self.t1 = t1
        self.angle = angle


    def __add__(self, other):
        return Manoeuvre(self.t0 + other.t0,self.t1+other.t1,self.angle+ other.angle)

    def __sub__(self, other):
        return Manoeuvre(self.t0 - other.t0,self.t1-other.t1,self.angle- other.angle)

    def __rmul__(self, other):
        return Manoeuvre(self.t0*other,self.t1*other,self.angle*other)

    def __repr__(self):
        return ("t0:" + str(self.t0) + " t1:" + str(self.t1) + " angle:" + str(self.angle))
    def convertMtoA(self):
        if T-self.t0 != 0:
            return np.array([self.t0, (2*self.t1)/(T-self.t0), self.angle])
        return np.array([self.t0, 0, self.angle])

def convertAtoM(manoeuvre):
    return Manoeuvre(manoeuvre[0],manoeuvre[1]*((T-manoeuvre[0])/2),manoeuvre[2])

def creaPop(Flights):
    global FLIGHTS
    FLIGHTS = Flights
    bounds_t0 = [BOUNDS[0] for k in range(N_avion)]
    bounds_theta = [BOUNDS[1]for k in range(N_avion)]
    bounds_alpha = [BOUNDS[2]for k in range(N_avion)]
    pop_alpha = testDE.initPop(bounds_alpha, N_pop)
    pop_t0 = testDE.initPop(bounds_t0, N_pop)
    pop_theta = testDE.initPop(bounds_theta, N_pop)
    ManoeuvreInit=[flight.manoeuvre.convertMtoA() for flight in Flights]
    liste_manoeuvres = []
    liste_manoeuvres.append(ManoeuvreInit)  # le premier individu de la population est la situation initiale.
    for k in range(1, N_pop):
        eltMan = []
        for l in range(N_avion):
            manArray=np.array([pop_t0[k][l], pop_theta[k][l],pop_alpha[k][l]])
            eltMan.append(manArray)
        liste_manoeuvres.append(eltMan)
    return liste_manoeuvres


# Fonction de calcul du cout
# Prend en parametre Man une liste de manoeuvres (une pour chaque avion)

def cout():
    C_ang = 0
    C_time = 0
    for vol in FLIGHTS:
        C_ang += vol.manoeuvre.angle ** 2
        C_time += (vol.manoeuvre.t1) ** 2 + ((T - vol.manoeuvre.t0) ** 2)
    return C_ang/alMc + C_time/Tc

def dureeConflit(liste_Conflits):
    duree = 0
    for val in liste_Conflits:
        if len(val) != 0:
            for i in val:
                for j in i:
                    duree += j[1] - j[0]
    return duree /(2*T)

def updateConflits():
    liste_Conflits = []
    for i in range(N_avion):
        FLIGHTS[i].dConflits={}
    for i in range(N_avion):
        for j in range(i + 1, N_avion):
            conflit2a2(FLIGHTS[i], FLIGHTS[j])
        liste_Conflits.append(FLIGHTS[i].listeConflits())
    return liste_Conflits



# fonction fitness: # Prend en parametre Man une liste de manoeuvres (une pour chaque avion)
def fitness(Man):
    for i,vol in enumerate(FLIGHTS):
        vol.manoeuvre = convertAtoM(Man[i])
    liste_Conflits = updateConflits()  #Contient tous les conflits de chaque vol
    #print(liste_Conflits)
    dureeConf = dureeConflit(liste_Conflits)
    if dureeConf > 10**(-10):
    #if dureeConf != 0:
        #print("fitness")
        return  1.0/(2.0 + dureeConf)
    else:

        return 0.5 + 1.0/(2+cout())


def rotMatrix(theta):
    return np.array([[np.cos(theta), np.sin(theta)], [-np.sin(theta), np.cos(theta)]])
    # J'ai vérifié les signes, refait les calculs et inversé les signes, sinon c'était faux.
    # Là on a bien la matrice d'une rotation directe

# conflits 2 à 2 avec des vols
def conflit2a2(f1, f2):
    ptdep1 = np.array([float(f1.pointDepart.x()),float(f1.pointDepart.y())])
    ptdep2 = np.array([float(f2.pointDepart.x()),float(f2.pointDepart.y())])
    v1 = f1.speed
    v2 = f2.speed
    t01 = f1.manoeuvre.t0
    alpha1 = f1.manoeuvre.angle
    t11 = f1.manoeuvre.t1
    t02 = f2.manoeuvre.t0
    alpha2 = f2.manoeuvre.angle
    t12 = f2.manoeuvre.t1
    # Pour éviter que les aviosn rentrent plusieurs fois dans un if d'etat
    compteur1 = 0
    compteur2 = 0
    # Les segments de trajectoire ne commencent pas au temps initial 0 mais aux temps ti1,ti2
    ti1 = 0
    ti2 = 0

    temps = sorted([(0,None), (t01,f1), (t01+t11,f1), (t01+2*t11,f1), (t02,f2), (t02+t12,f2), (t02+2*t12,f2)],\
                   key=lambda x:x[0])
    for (i,t) in enumerate(temps):
        if f1.etat == 1 and compteur1 == 0:
            ptdep1 += t01 * v1
            v1 = np.dot(rotMatrix(alpha1), v1)
            ti1 += t01
            compteur1 += 1
        elif f1.etat == 2 and compteur1 == 1:
            ptdep1 += t11 * v1
            v1 = np.dot(rotMatrix(-2 * alpha1), v1)
            ti1 += t11
            compteur1 += 1
        elif f1.etat == 3 and compteur1 == 2:
            ptdep1 += t11 * v1
            v1 = np.dot(rotMatrix(alpha1), v1)
            ti1 += t11
            compteur1 += 1
        if f2.etat == 1 and compteur2 == 0:
            ptdep2 += t02 * v2
            v2 = np.dot(rotMatrix(alpha2), v2)
            ti2 += t02
            compteur2 += 1
        elif f2.etat == 2 and compteur2 == 1:
            ptdep2 += t12 * v2
            v2 = np.dot(rotMatrix(-2 * alpha2), v2)
            ti2 += t12
            compteur2 += 1
        elif f2.etat == 3 and compteur2 == 2:
            ptdep2 += t12 * v2
            v2 = np.dot(rotMatrix(alpha2), v2)
            ti2 += t12
            compteur2 += 1

        # LE [0] est la coordonnée en x et [1] la coordonnée en y
        a = (v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2

        b = 2 * ((ptdep1[0] - ptdep2[0] + v2[0]*ti2 - v1[0]*ti1) * (v1[0] - v2[0]) +
                 (ptdep1[1] - ptdep2[1] + v2[1]*ti2 - v1[1]*ti1) * (v1[1] - v2[1]))

        c = (ptdep1[0] - ptdep2[0] + v2[0]*ti2 - v1[0]*ti1)**2 + (ptdep1[1] - ptdep2[1] + v2[1]*ti2 - v1[1]*ti1)**2 - d**2

        coeff = [a, b, c]

        racines = np.roots(coeff)
        #print("racines: " + str(racines) + " coeff: "+ str(coeff))
        tdeb = min(racines[0].real, racines[1].real)
        tfin = max(racines[0].real, racines[1].real)
        #print("debfin :" + str((tdeb,tfin)))
        if abs(racines[0].imag)<10**(-8):
            #On ne garde que les solutions réelles: si imaginaires, les avions ne sont pas en conflit
            # Pour eviter list index out of range dans le cas où on est dans la dernière partie du trajet
            try:
                tiplus1 = temps[i+1][0]
            except IndexError:
                tiplus1 = T
            tmax= max(t[0], min(tfin, tiplus1))
            tmin= max(t[0], min(tdeb, tiplus1))

            if f2 not in f1.dConflits.keys():
                f1.dConflits[f2] = []
                f2.dConflits[f1] = []

            if (tmin, tmax) not in f1.dConflits[f2]:
                f1.dConflits[f2].append((tmin, tmax))
                f2.dConflits[f1].append((tmin, tmax))
        try:
            temps[i+1][1].etat = (temps[i+1][1].etat + 1) % 4
        except IndexError:
            pass
    # Pour que les etats soient revenus à 0 pour les fois suivantes
    f1.etat = 0
    f2.etat = 0
