from PyQt5.QtCore import QPoint
import random
import numpy as np

T = 200  # Temps total
N_avion = 20  # Nombre d'avions
N_pop = 100
alphaMax = np.pi / 6
d = 5

alMc = alphaMax ** 2
Tc = T ** 2


class Flight():
    def __init__(self, speed, trajectory):
        self.speed = speed
        self.trajectory = trajectory
        self.dConflits = {}#dictionnaire des conflits, clés: les avions et valeurs: listes des temps de début et fin de conflits pour tous les moments où les avions sont en conflit
        self.etat = 0

    # Permet de savoir à quelle étape de la manoeuvre en est l'avion: 0=avant la manoeuvre; 1= montée initiale; 2= retour à la trajectoire;3 manoeuvre
    # terminée. Initialisé à etape 0 (trajectoire initiale)

    # return 5 QPoints qui sont debut,fin et cassures de la trajectoire
    # angles en radians
    def pointTrajectory(self):
        p0 = self.trajectory.pointDepart
        p1 = p0 + QPoint(self.speed * self.trajectory.manoeuvre.t0 * np.cos(self.trajectory.angle0),
                         self.speed * self.trajectory.manoeuvre.t0 * np.sin(self.trajectory.angle0))
        p2 = p1 + QPoint(self.speed * self.trajectory.manoeuvre.t1 * np.cos(
            self.trajectory.manoeuvre.angle + self.trajectory.angle0),
                         self.speed * self.trajectory.manoeuvre.t1 * np.sin(
                             self.trajectory.manoeuvre.angle + self.trajectory.angle0))
        p3 = p2 + QPoint(self.speed * self.trajectory.manoeuvre.t1 * np.cos(
            -self.trajectory.manoeuvre.angle + self.trajectory.angle0),
                         self.speed * self.trajectory.manoeuvre.t1 * np.sin(
                             -self.trajectory.manoeuvre.angle + self.trajectory.angle0))
        p4 = p3 + QPoint(self.speed * (T - self.trajectory.manoeuvre.t0 - 2 * self.trajectory.manoeuvre.t1) * np.cos(
            self.trajectory.angle0),
                         self.speed * (T - self.trajectory.manoeuvre.t0 - 2 * self.trajectory.manoeuvre.t1) * np.sin(
                             self.trajectory.angle0))
        return [p0, p1, p2, p3, p4]

    def listeConflits(self):
        return self.dConflits.values()

    def __repr__(self):
        return str(self.speed) + " " + self.trajectory


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
        return ("Depart:" + self.pointDepart + " manoeuvre:" + self.manoeuvre + " angle0:" + str(self.angle0))


def calculConflit():
    return None


def init():
    F = [Flight(100, Trajectory(QPoint(0, 50 * k), 0.5 * k, Manoeuvre(0, 0, 0))) for k in range(N_avion)]
    X = []
    # x0 = [Manoeuvre(calculConflit(f0),0) for f0 in F]
    # X.append(x0)
    for k in range(1, N_pop):
        x = []
        for l in range(N_avion):
            angle = random.uniform(-np.pi / 6, np.pi / 6)
            t0 = random.randint(0, T)  # Les temps sont entier à voir
            t1 = random.randint(0, T)
            x.append(Manoeuvre(t0, t1, angle))
        X.append(x)
    return F, X


# Fonction de calcul du cout
# Prend en parametre f une liste d'avions = trajectoire + vitesse

def cout(f):
    C_ang= 0
    C_time= 0
    for fi in f:
        manoeuvre = (fi.trajectory).manoeuvre
        C_ang+= manoeuvre.angle ** 2
        C_time+= manoeuvre.t1 ** 2 + ((T - manoeuvre.t0) ** 2)
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



def updateConflits(f):
    N = len(f)
    liste_Conflits = []
    for i in range(0, N):
        for j in range(i + 1, N):
            conflit2a2(f[i], f[j])
            liste_Conflits.append(f[i].dConflits[fj][0])
    return liste_Conflits




# Fonction de duree de conflit: prend en parametre f une liste d'avions

def dureeConflit(f):
    duree = 0
    for fi in f:
        if fi.dConflits != {}:
            key_mini = min(fi.dConflits.keys(), key=(lambda k: fi.dConflits[k][0]))
            duree += fi.dConflits[key_mini][1] - fi.dConflits[key_mini][0]
    return duree / T


# fonction fitness:
def fitness(f):
    if dureeConflit(f) > 0:
        return 1 / (2 + dureeConflit(f))
    else:
        return 1 / 2 + 1 / cout(f)


def rotMatrix(theta):
    return np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])


# conflits 2 à 2 avec des manoeuvres:!!
def conflit2a2(f1, f2):
    ptdep1 = f1.trajectory.pointDepart
    ptdep2 = f2.trajectory.pointDepart
    v1 = f1.speed
    v2 = f2.speed
    t01 = f1.manoeuvre.t0
    alpha1 = f1.manoeuvre.angle
    t11 = f1.manoeuvre.t1
    t02 = f2.manoeuvre.t0
    alpha2 = f2.manoeuvre.angle
    t12 = f2.manoeuvre.t1
    dico_temps = {'t01': f1, 't01+t11': f1, 't01+2*t11': f1, 't02': f2, 't02+t12': f2, 't02+2*t12': f2}
    temps = dico_temps.keys().sort()
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
        a = (v1.x - v2.x) ** 2 + (v1.y - v2.y) ** 2
        b = 2 * ((ptdep1.x - ptdep2.x) * (v1.x - v2.x) + (ptdep1.y - ptdep2.y) * (v1.y - v2.y))
        c = (ptdep1.x - ptdep2.x) ** 2 + (ptdep1.y - ptdep2.y) ** 2 - d ** 2
        coeff = [a, b, c]
        racines = np.roots(coeff)
        tdeb = min(racines[0], racines[1])
        tfin = max(racines[0], racines[1])
        if tdeb.imag == 0: #On ne garde que les solutions réelles: si imaginaires, les avions ne sont pas en conflit
            tmin= max(t,min(tdeb,temps[i+1]))
            tmax= max(t, min(tfin, temps[i+1]))
            if f2 not in f1.dConflits.keys():
                f1.dConflits[f2] = []
                f2.dConflits[f1] = []

            if (tmin, tmax) not in f1.dConflits[f2]:
                f1.dConflits[f2].append((tmin, tmax))
                f2.dConflits[f1].append((tmin, tmax))

        dico_temps[t].etat = (dico_temps[t].etat + 1) % 4
