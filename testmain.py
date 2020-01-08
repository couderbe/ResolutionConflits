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
N_pop=40
BOUNDS = [(0,T), (0,1), (-alphaMax, alphaMax)] # bornes de alpha, t0 et theta avec t1=theta*((T-t0)/2)
CR = 0.05
F = 0.7

""" Constantes (fonction des paramètres) calculées une fois pour toutes """
alMc = alphaMax ** 2
Tc = T ** 2


class Flight():
    def __init__(self, speed, pointDepart, angle0, manoeuvre):
        self.pointDepart = pointDepart
        self.angle0 = angle0
        self.manoeuvre = manoeuvre
        self.speed = np.dot(rotMatrix(self.angle0),np.array([speed,0])) #Un array numpy
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
    #print("fitness")
    if dureeConf > 10**(-10):
    #if dureeConf != 0:

        return  1.0/(2.0 + dureeConf)
    else:

        return 0.5 + 1.0/(2+cout())


def rotMatrix(theta):
    return np.array([[np.cos(theta), -np.sin(theta)],
                     [np.sin(theta), np.cos(theta)]])
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
    angle1 = [alpha1,-2*alpha1,alpha1]
    compteur2 = 0
    angle2 = [alpha2, -2 * alpha2, alpha2]
    temps = sorted([(0,None),(t01,f1), (t01+t11,f1), (t01+2*t11,f1), (t02,f2), (t02+t12,f2), (t02+2*t12,f2)],\
                   key=lambda x:x[0])
    #print("temps: " + str(temps))
    tOld = 0
    '''
    a = (v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2

    b = 2 * ((ptdep1[0] - ptdep2[0]) * (v1[0] - v2[0]) + (ptdep1[1] - ptdep2[1]) * (v1[1] - v2[1]))

    c = (ptdep1[0] - ptdep2[0]) ** 2 + (ptdep1[1] - ptdep2[1]) ** 2 - d ** 2

    racines = second_degre(a, b, c)
    tdeb = min(racines)
    tfin = max(racines)

    tmax = max(0, min(tfin,T))
    tmin = max(0, min(tdeb,T))

    if f2 not in f1.dConflits.keys():
        f1.dConflits[f2] = []
        f2.dConflits[f1] = []

    if (tmin, tmax) not in f1.dConflits[f2]:
        f1.dConflits[f2].append((tmin, tmax))
        f2.dConflits[f1].append((tmin, tmax))
    ##'''
    #print(f1,f2)
    for (i,t) in enumerate(temps):
        #print(i,t)
        tCurrent = t[0]
        dt = tCurrent - tOld
        #print(dt)
        #print(dt)
        ptdep2 += dt * v2
        ptdep1 += dt * v1
        #print(ptdep1,ptdep2)
        #print(ptdep1,ptdep2)
        flightChanging = t[1]
        if flightChanging != None:
            flightChanging.etat += 1
            #print(flightChanging)
            if flightChanging == f1:
                v1 = np.dot(rotMatrix(angle1[compteur1]),v1)
                #print("v1"+str(v1))
                compteur1 += 1
            else:
                v2 = np.dot(rotMatrix(angle2[compteur2]), v2)
                #print("v2" + str(v2))
                compteur2 += 1



        # LE [0] est la coordonnée en x et [1] la coordonnée en y
        a = (v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2

        b = 2 * ((ptdep1[0] - ptdep2[0]) * (v1[0] - v2[0]) +
                 (ptdep1[1] - ptdep2[1]) * (v1[1] - v2[1]))

        c = (ptdep1[0] - ptdep2[0])**2 + (ptdep1[1] - ptdep2[1])**2 - d**2

        racines = second_degre(a,b,c)
        if racines != None:
            tdeb = min(racines) + t[0]
            tfin = max(racines) + t[0]
            #print(tdeb,tfin)
            if i < len(temps)-1:
                tiplus1 = temps[i+1][0]
            else:
                tiplus1 = T

            tmax= max(tCurrent, min(tfin, tiplus1))
            tmin= max(tCurrent, min(tdeb, tiplus1))
            #print(tmin,tmax)

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

def second_degre (a,b,c) :
    delta = b**2 - 4*a*c
    if delta > 0 :
        racine1 = (-b - np.sqrt(delta))/(2*a)
        racine2 = (-b + np.sqrt(delta))/(2*a)
        return [racine1, racine2]
    return None