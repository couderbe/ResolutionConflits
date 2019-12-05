import copy

from PyQt5.QtCore import QPoint
import random
import numpy as np
import time

T = 500  # Temps total
N_avion = 20  # Nombre d'avions
N_pop = 10
alphaMax = np.pi / 6
d = 1000#5 #Distance de séparation
alMc = alphaMax ** 2
Tc = T ** 2


class Flight():
    def __init__(self, speed, trajectory):
        self.trajectory = trajectory
        self.speed2 = speed
        self.speed = np.dot(np.array([speed,0]),rotMatrix(self.trajectory.angle0)) #Un array numpy
        self.dConflits = {}#dictionnaire des conflits, clés: les avions et valeurs: listes des temps de début et fin de conflits pour tous les moments où les avions sont en conflit
        self.etat = 0

    # Permet de savoir à quelle étape de la manoeuvre en est l'avion: 0=avant la manoeuvre; 1= montée initiale; 2= retour à la trajectoire;3 manoeuvre
    # terminée. Initialisé à etape 0 (trajectoire initiale)

    # return 5 QPoints qui sont debut,fin et cassures de la trajectoire
    # angles en radians
    def pointTrajectory(self):
        p0 = self.trajectory.pointDepart
        p1 = p0 + QPoint(self.speed2 * self.trajectory.manoeuvre.t0 * np.cos(self.trajectory.angle0),
                         self.speed2 * self.trajectory.manoeuvre.t0 * np.sin(self.trajectory.angle0))
        p2 = p1 + QPoint(self.speed2 * self.trajectory.manoeuvre.t1 * np.cos(
            self.trajectory.manoeuvre.angle + self.trajectory.angle0),
                         self.speed2 * self.trajectory.manoeuvre.t1 * np.sin(
                             self.trajectory.manoeuvre.angle + self.trajectory.angle0))
        p3 = p2 + QPoint(self.speed2 * self.trajectory.manoeuvre.t1 * np.cos(
            -self.trajectory.manoeuvre.angle + self.trajectory.angle0),
                         self.speed2 * self.trajectory.manoeuvre.t1 * np.sin(
                             -self.trajectory.manoeuvre.angle + self.trajectory.angle0))
        p4 = p3 + QPoint(self.speed2 * (T - self.trajectory.manoeuvre.t0 - 2 * self.trajectory.manoeuvre.t1) * np.cos(
            self.trajectory.angle0),
                         self.speed2 * (T - self.trajectory.manoeuvre.t0 - 2 * self.trajectory.manoeuvre.t1) * np.sin(
                             self.trajectory.angle0))
        return [p0,p1,p2,p3,p4]

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
        return str(self.speed) + " " + str(self.trajectory)


class Manoeuvre():
    def __init__(self, t0, t1, angle):
        self.t0 = t0
        self.angle = angle
        self.t1 = t1

    def __add__(self, other):
        self.t0 += other.t0
        self.t1 += other.t1
        self.angle += other.angle
        return self

    def __sub__(self, other):
        self.t0 -= other.t0
        self.t1 -= other.t1
        self.angle -= other.angle
        return self

    def __rmul__(self, other):
        self.t0 *= other
        self.t1 *= other
        self.angle *= other
        return self

    def __repr__(self):
        return ("t0:" + str(self.t0) + " t1:" + str(self.t1) + " angle:" + str(self.angle))


class Trajectory():
    def __init__(self, pointDepart, angle0, manoeuvre):
        self.pointDepart = pointDepart
        self.angle0 = angle0
        self.manoeuvre = manoeuvre

    def __repr__(self):
        return ("Depart:" + str(self.pointDepart) + " manoeuvre:" + str(self.manoeuvre) + " angle0:" + str(self.angle0*180/np.pi))


def calculConflit():
    return None


def init(Flights):
    #Flights = [Flight(100, Trajectory(QPoint(0, 50 * k), 0.5 * k, Manoeuvre(0, 0, 0))) for k in range(N_avion)]
    X = []
    print(Flights)
    premierConflits = updateConflits(Flights) # Liste des premiers conflits pour chaque avion ensuite utilisés pour crée x0 qui est le vecteur avec les manouvres vides

    time.sleep(5)

    print("Premier conflits:  "+ str(premierConflits))
    x0 = [Manoeuvre(premierConflits[k][0],0,0)for k in range(N_avion)] #Le t0 on prend le début du premier conflit mais je sais pas si c'est utile et pas de t1 surtout !!!!
    X.append(x0)
    for k in range(1, N_pop):
        x = []
        for l in range(N_avion):
            angle = random.uniform(-np.pi / 6, np.pi / 6)
            t0 = random.randint(0, T)  # Les temps sont entier à voir
            t1 = random.randint(0, T)
            x.append(Manoeuvre(t0, t1, angle))
        X.append(x)
    return Flights, X


# Fonction de calcul du cout
# Prend en parametre x une liste de manoeuvre (une pour chaque avion)

def cout(x):
    C_ang = 0
    C_time = 0
    for manoeuvre in x:
        C_ang += manoeuvre.angle ** 2
        C_time = C_time + (manoeuvre.t1 ** 2) + ((T - manoeuvre.t0) ** 2)
    return C_ang/alMc + C_time/Tc


# Fonction conflit2a2: renvoie les temps de conflit tdeb et tfin entre deux avions
def conflit2a2_init(f1, f2):
    ptdep1 = f1.trajectory.pointDepart
    ptdep2 = f2.trajectory.pointDepart
    v1 = f1.speed
    v2 = f2.speed
    a = (v1.x - v2.x) ** 2 + (v1.y - v2.y) ** 2
    b = 2 * ((ptdep1.x - ptdep2.x) * (v1.x - v2.x) + (ptdep1.y - ptdep2.y) * (v1.y - v2.y))
    c = (ptdep1.x - ptdep2.x) ** 2 + (ptdep1.y - ptdep2.y) ** 2 - d ** 2
    coeff = [a, b, c]
    racines = np.roots(coeff)
    tdeb = min(racines[0], racines[1])
    tfin = max(racines[0], racines[1])
    if tdeb.imag == 0:
        if len(f1.dConflits) == 0:
            f1.dConflits = []
        if len(f2.dConflits) == 0:
            f2.dConflits = []
        if tdeb < 0:
            if tfin > 0:
                f1.dConflits[f2].append((0, min(tfin, T)))
                f2.dConflits[f1].append((0, min(tfin, T)))
        elif tdeb < T:
            f1.dConflits[f2].append((tdeb, min(tfin, T)))
            f2.dConflits[f1].append((tdeb, min(tfin, T)))



# update les Conflits et renvoie la liste du premier conflit pour chaque avion
# Argument est une liste de Flight

def updateConflits(f):
    print("UpdateConflits: " + str(f))
    N = len(f)
    liste_Conflits = []
    for i in range(0, N):
        for j in range(i + 1, N):
            conflit2a2(f[i], f[j])
            print("Conflits f " + str(i) + str(f[i].dConflits))
            print("Conflits f " + str(j) + str(f[j].dConflits))
        liste_Conflits.append(f[i].premierConflit())
    print(f[0].dConflits)
    return liste_Conflits


# Fonction de duree de conflit: Prend en parametre x une liste de manoeuvre (une pour chaque avion)

def dureeConflit(liste_Conflits):
    duree = 0
    for val in liste_Conflits:
        if len(val) != 0:
            for i in val:
                for j in i:
                    duree += j[1] - j[0]
    return duree / T


# fonction fitness: # Prend en parametre x une liste de manoeuvre (une pour chaque avion)
def fitness(F,x):
    f = copy.deepcopy(F)
    liste_Conflits = calculConflitPourFitness(f)  #Contient tout les conflits de chaque vol
    if dureeConflit(liste_Conflits) > 0:
        return 1 / (2 + dureeConflit(liste_Conflits))
    else:
        return 1 / 2 + 1 / cout(x)

def calculConflitPourFitness(f):
    N = len(f)
    liste_Conflits = []
    for i in range(0, N):
        for j in range(i + 1, N):
            conflit2a2(f[i], f[j])

        liste_Conflits.append(f[i].listeConflits())
    return liste_Conflits

def rotMatrix(theta):
    return np.array([[np.cos(theta), np.sin(theta)], [-np.sin(theta), np.cos(theta)]])
    # Attention peut-être il faut inverser les moins sur les sinus suivant l'orientation de la fenêtre Qt et de l'inversion de l'axe y

# conflits 2 à 2 avec des manoeuvres:!!
def conflit2a2(f1, f2):
    ptdep1 = np.array([float(f1.trajectory.pointDepart.x()),float(f1.trajectory.pointDepart.y())])
    ptdep2 = np.array([float(f2.trajectory.pointDepart.x()),float(f2.trajectory.pointDepart.y())])
    v1 = f1.speed
    v2 = f2.speed
    t01 = f1.trajectory.manoeuvre.t0
    alpha1 = f1.trajectory.manoeuvre.angle
    t11 = f1.trajectory.manoeuvre.t1
    t02 = f2.trajectory.manoeuvre.t0
    alpha2 = f2.trajectory.manoeuvre.angle
    t12 = f2.trajectory.manoeuvre.t1
    print(f1)
    print(f2)
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
        print("Coeffs: " + str(coeff))
        racines = np.roots(coeff)
        print(racines)
        tdeb = min(racines[0].real, racines[1].real)
        tfin = max(racines[0].real, racines[1].real)
        print((tdeb,tfin))
        if racines[0].imag == 0: #On ne garde que les solutions réelles: si imaginaires, les avions ne sont pas en conflit
            # Pour eviter list index out of range dans le cas ou on est dans la dernière partie du trajet
            try:
                tiplus1 = temps[i+1][0]
            except IndexError:
                tiplus1 = T
            tmin= max(t[0],min(tdeb,tiplus1))
            tmax= max(t[0], min(tfin, tiplus1))
            print((tmin,tmax))
            print(f1.dConflits)
            if f2 not in f1.dConflits.keys():
                f1.dConflits[f2] = []
                f2.dConflits[f1] = []
                print(f1.dConflits)

            if (tmin, tmax) not in f1.dConflits[f2]:
                f1.dConflits[f2].append((tmin, tmax))
                f2.dConflits[f1].append((tmin, tmax))
                print(f1.dConflits)

        print(f1.etat)
        print(f2.etat)
        try:
            temps[i+1][1].etat = (temps[i+1][1].etat + 1) % 4
        except IndexError:
            pass
    # Pour que les etats soient revenus à 0 pour fois suivantes
    f1.etat = 0
    f2.etat = 0

