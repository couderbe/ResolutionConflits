import copy

from PyQt5.QtCore import QPoint
import random
import numpy as np
import time

T = 240  # Temps total
N_avion = 4 # Nombre d'avions
N_pop = 50
alphaMax = np.pi / 6
d = 5000 #5 #Distance de séparation
alMc = alphaMax ** 2
Tc = T ** 2


class Flight():
    def __init__(self, speed, pointDepart, angle0, manoeuvre):
        self.pointDepart = pointDepart
        self.angle0 = angle0
        self.manoeuvre = manoeuvre
        self.speed2 = speed
        self.speed = np.dot(np.array([speed,0]),rotMatrix(self.angle0)) #Un array numpy
        self.dConflits = {}#dictionnaire des conflits, clés: les avions et valeurs: listes des temps de début et fin de conflits pour tous les moments où les avions sont en conflit
        self.etat = 0


    # Permet de savoir à quelle étape de la manoeuvre en est l'avion: 0=avant la manoeuvre; 1= montée initiale; 2= retour à la trajectoire;3 manoeuvre
    # terminée. Initialisé à etape 0 (trajectoire initiale)

    # return 5 QPoints qui sont debut,fin et cassures de la trajectoire
    # angles en radians
    def pointTrajectory(self):
        p0 = self.pointDepart
        p1 = p0 + QPoint(self.speed2 * self.manoeuvre.t0 * np.cos(self.angle0),
                         self.speed2 * self.manoeuvre.t0 * np.sin(self.angle0))
        p2 = p1 + QPoint(self.speed2 * self.manoeuvre.theta*((T-self.manoeuvre.t0)/2) * np.cos(
            self.manoeuvre.angle + self.angle0),
                         self.speed2 * self.manoeuvre.theta*((T-self.manoeuvre.t0)/2) * np.sin(
                             self.manoeuvre.angle + self.angle0))
        p3 = p2 + QPoint(self.speed2 * self.manoeuvre.theta*((T-self.manoeuvre.t0)/2) * np.cos(
            -self.manoeuvre.angle + self.angle0),
                         self.speed2 * self.manoeuvre.theta*((T-self.manoeuvre.t0)/2) * np.sin(
                             -self.manoeuvre.angle + self.angle0))
        p4 = p3 + QPoint(self.speed2 * (T - self.manoeuvre.t0 - 2 * self.manoeuvre.theta*((T-self.manoeuvre.t0)/2)) * np.cos(
            self.angle0),
                         self.speed2 * (T - self.manoeuvre.t0 - 2 * self.manoeuvre.theta*((T-self.manoeuvre.t0)/2)) * np.sin(
                             self.angle0))
        return [p0,p1,p2,p3,p4]


    ## Fonction en cours qui doit donner une liste de plein de points de la trajectoire pour dépacer ensite les avion grace à Qt
    def completeTrajectory(self,nbrPoint):
        intervaleTemps = T/nbrPoint
        resultat = [self.pointDepart]
        for k in range(1,nbrPoint):
            if k*intervaleTemps <= self.manoeuvre.t0:
                resultat.append(resultat[k-1] + QPoint(intervaleTemps*self.speed2*np.cos(self.angle0),
                                                       intervaleTemps*self.speed2*np.sin(self.angle0)))
            elif k*intervaleTemps <= (self.manoeuvre.t0 + self.manoeuvre.theta*((T-self.manoeuvre.t0)/2)):
                resultat.append(resultat[k - 1] + QPoint(intervaleTemps * self.speed2 * np.cos(self.angle0 + self.manoeuvre.angle),
                                                         intervaleTemps * self.speed2 * np.sin(self.angle0 + self.manoeuvre.angle)))
            elif k * intervaleTemps <= (self.manoeuvre.t0 + self.manoeuvre.theta * ((T - self.manoeuvre.t0))):
                resultat.append(resultat[k - 1] + QPoint(intervaleTemps * self.speed2 * np.cos(self.angle0 - self.manoeuvre.angle),
                                                         intervaleTemps * self.speed2 * np.sin(self.angle0 - self.manoeuvre.angle)))
            else:
                resultat.append(resultat[k - 1] + QPoint(intervaleTemps * self.speed2 * np.cos(self.angle0),
                                                         intervaleTemps * self.speed2 * np.sin(self.angle0)))
        return resultat


    def listeConflits(self):
        return self.dConflits.values()

    def premierConflit(self):
        conflits = self.listeConflits()
        if len(conflits) == 0:
            return (T,0)
        min_par_avion_dispo = []
        for k in conflits:
            min_par_avion_dispo.append(min(k,key= lambda x:x[0]))
        return min(min_par_avion_dispo, key=lambda x:x[0])

    def __repr__(self):
        return ("Vitesse:" + " " + str(self.speed) + " " + "Depart:" + str(self.pointDepart) + " Manoeuvre:" + str(self.manoeuvre) + " Angle0:" + str(self.angle0*180/np.pi))


class Manoeuvre():
    def __init__(self, t0, theta, angle):
        self.t0 = t0
        self.angle = angle
        self.theta = theta

    def __add__(self, other):
        return Manoeuvre(self.t0 + other.t0,self.theta+other.theta,self.angle+ other.angle)

    def __sub__(self, other):
        return Manoeuvre(self.t0 - other.t0,self.theta-other.theta,self.angle- other.angle)

    def __rmul__(self, other):
        return Manoeuvre(self.t0*other,self.theta*other,self.angle*other)

    def __repr__(self):
        return ("t0:" + str(self.t0) + " theta:" + str(self.theta) + " angle:" + str(self.angle))


#class Trajectory():
 #   def __init__(self, pointDepart, angle0, manoeuvre):
  #      self.pointDepart = pointDepart
  #      self.angle0 = angle0
  #      self.manoeuvre = manoeuvre



def calculConflit():
    return None


def init(Flights):
    X = []
    liste_Flights = []
    liste_Flights.append(Flights)

    print(Flights)
    premierConflits = updateConflits(Flights) # Liste des conflits pour chaque avion ensuite utilisés pour crée x0 qui est le vecteur avec les manouvres vides

    for k in range(1,N_pop):
        vols = []
        for l in range(N_avion):
            angle = random.uniform(-np.pi / 6, np.pi / 6)
            t0 = random.uniform(0, T)
            theta = random.random()
            vols.append(Flight(Flights[l].speed2,Flights[l].pointDepart, Flights[l].angle0, Manoeuvre(t0,theta,angle)))
        liste_Flights.append(vols)
    return liste_Flights


# Fonction de calcul du cout
# Prend en parametre x une liste de manoeuvre (une pour chaque avion)

def cout(f):
    C_ang = 0
    C_time = 0
    for vol in f:
        C_ang += vol.manoeuvre.angle ** 2
        C_time = C_time + (((vol.manoeuvre.theta/2)*(T-vol.manoeuvre.t0)) ** 2) + ((T - vol.manoeuvre.t0) ** 2)
    return C_ang/alMc + C_time/Tc

# update les Conflits et renvoie la liste du premier conflit pour chaque avion
# Argument est une liste de Flight

def updateConflits(f):
    N = N_avion
    liste_Conflits = []
    for i in range(0, N):
        for j in range(i + 1, N):
            conflit2a2(f[i], f[j])
        liste_Conflits.append(f[i].listeConflits())
    return liste_Conflits


# Fonction de duree de conflit: Prend en parametre x une liste de manoeuvres (une pour chaque avion)

def dureeConflit(liste_Conflits):
    duree = 0
    for val in liste_Conflits:
        if len(val) != 0:
            for i in val:
                for j in i:
                    duree += j[1] - j[0]
    return duree /(2*T)


# fonction fitness: # Prend en parametre x une liste de manoeuvre (une pour chaque avion)
def fitness(f):
    liste_Conflits = updateConflits(f)  #Contient tout les conflits de chaque vol
    dureeConf = dureeConflit(liste_Conflits)
    #print(dureeConf)
    #if dureeConf > 10**(-5):
    if dureeConf != 0:
        #print("fitness")
        return 1 / (2 + dureeConf)
    else:
        return 1 / 2 + 1 / (2+cout(f))


def rotMatrix(theta):
    return np.array([[np.cos(theta), np.sin(theta)], [-np.sin(theta), np.cos(theta)]])
    # Attention peut-être il faut inverser les moins sur les sinus suivant l'orientation de la fenêtre Qt et de l'inversion de l'axe y

# conflits 2 à 2 avec des manoeuvres:!!
def conflit2a2(f1, f2):
    ptdep1 = np.array([float(f1.pointDepart.x()),float(f1.pointDepart.y())])
    ptdep2 = np.array([float(f2.pointDepart.x()),float(f2.pointDepart.y())])
    v1 = f1.speed
    v2 = f2.speed
    t01 = f1.manoeuvre.t0
    alpha1 = f1.manoeuvre.angle
    t11 = f1.manoeuvre.theta*(T-t01)/2
    t02 = f2.manoeuvre.t0
    alpha2 = f2.manoeuvre.angle
    t12 = f2.manoeuvre.theta*(T-t02)/2
    #print(f1)
    #print(f2)


    #dico_temps = {'t01': f1, 't01+t11': f1, 't01+2*t11': f1, 't02': f2, 't02+t12': f2, 't02+2*t12': f2}
    #print(dico_temps.keys())
    #temps = sorted([t01, t01+t11, t01+2*t11, t02, t02+t12, t02+2*t12])
    #print(temps)


    # Il y en a 6 je pense qu'il en faut 7 je le rajoute juste avant pour quand les 2 sont à 0
    temps = sorted([(0,None),(t01,f1), (t01+t11,f1), (t01+2*t11,f1), (t02,f2), (t02+t12,f2), (t02+2*t12,f2)],key=lambda x:x[0])

    for (i,t) in enumerate(temps):
        if f1.etat == 1:
            ptdep1 += t01 * v1
            v1 = np.dot(rotMatrix(alpha1), v1)
        elif f1.etat == 2:
            ptdep1 += t11 * v1
            v1 = np.dot(rotMatrix(-2 * alpha1), v1)
        elif f1.etat == 3:
            ptdep1 += t11 * v1
            v1 = np.dot(rotMatrix(alpha1), v1)
        if f2.etat == 1:
            ptdep2 += t02 * v2
            v2 = np.dot(rotMatrix(alpha2), v2)
        elif f2.etat == 2:
            ptdep2 += t12 * v2
            v2 = np.dot(rotMatrix(-2 * alpha2), v2)
        elif f2.etat == 3:
            ptdep2 += t11 * v2
            v2 = np.dot(rotMatrix(alpha2), v2)
        a = (v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2  ## LE [0] est la coord x de la vitesse et [1] la coord y de la vitesse
        b = 2 * ((ptdep1[0] - ptdep2[0]) * (v1[0] - v2[0]) + (ptdep1[1] - ptdep2[1]) * (v1[1] - v2[1]))
        c = (ptdep1[0] - ptdep2[0]) ** 2 + (ptdep1[1] - ptdep2[1]) ** 2 - d ** 2
        coeff = [a, b, c]
        racines = np.roots(coeff)
        tdeb = min(racines[0].real, racines[1].real)
        tfin = max(racines[0].real, racines[1].real)
        if abs(racines[0].imag)<10**(-5): #On ne garde que les solutions réelles: si imaginaires, les avions ne sont pas en conflit
            # Pour eviter list index out of range dans le cas ou on est dans la dernière partie du trajet
            try:
                tiplus1 = temps[i+1][0]
            except IndexError:
                tiplus1 = T
            tmin= max(t[0],min(tdeb,tiplus1))
            tmax= max(t[0], min(tfin, tiplus1))
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
    # Pour que les etats soient revenus à 0 pour fois suivantes
    f1.etat = 0
    f2.etat = 0

