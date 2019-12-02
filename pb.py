from PyQt5.QtCore import QPoint
import math
import random
import numpy as np

T = 200 # Temps total
N_avion = 20 # Nombre d'avion
alphaMax=math.pi/6
d=5

alMc=alphaMax**2
Tc=T**2


class Flight():
    def __init__(self,speed,trajectory):
        self.speed = speed
        self.trajectory = trajectory

    # return 5 QPoints qui sont debut,fin et cassures de la trajectoire
    # angles en radians
    def pointTrajectory(self):
        p0 = self.trajectory.pointDepart
        p1 = p0 + QPoint(self.speed*self.trajectory.manoeuvre.t0*math.cos(self.trajectory.angle0),
                         self.speed*self.trajectory.manoeuvre.t0*math.sin(self.trajectory.angle0))
        p2 = p1 + QPoint(self.speed*self.trajectory.manoeuvre.t1*math.cos(self.trajectory.manoeuvre.angle + self.trajectory.angle0),
                         self.speed*self.trajectory.manoeuvre.t1*math.sin(self.trajectory.manoeuvre.angle + self.trajectory.angle0))
        p3 = p2 + QPoint(self.speed*self.trajectory.manoeuvre.t1*math.cos(-self.trajectory.manoeuvre.angle + self.trajectory.angle0),
                         self.speed*self.trajectory.manoeuvre.t1*math.sin(-self.trajectory.manoeuvre.angle + self.trajectory.angle0))
        p4 = p3 + QPoint(self.speed*(T - self.trajectory.manoeuvre.t0 - 2*self.trajectory.manoeuvre.t1)*math.cos(self.trajectory.angle0),
                         self.speed*(T - self.trajectory.manoeuvre.t0 - 2*self.trajectory.manoeuvre.t1)*math.sin(self.trajectory.angle0))
        return [p0,p1,p2,p3,p4]

    def __repr__(self):
        return str(self.speed) + " " +self.trajectory

class Manoeuvre():
    def __init__(self,t0,t1,angle):
        self.t0 = t0
        self.angle = angle
        self.t1 = t1

    def __add__(self,other):
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
    def __init__(self,pointDepart, angle0, manoeuvre):
        self.pointDepart = pointDepart
        self.angle0 = angle0
        self.manoeuvre = manoeuvre

    def __repr__(self):
        return ("Depart:" + self.pointDepart + " manoeuvre:" + self.manoeuvre + " angle0:" + str(self.angle0))

def calculConflit():
    return None

def init():
    F = [Flight(100,Trajectory(QPoint(0,50*k),0.5*k,Manoeuvre(0,0,0))) for k in range(N_avion)]
    X = []
    #x0 = [Manoeuvre(calculConflit(f0),0) for f0 in F]
    #X.append(x0)
    for k in range(1,N_avion):
        x = []
        for l in range(N_avion):
            angle = random.uniform(-math.pi/6,math.pi/6)
            t0 = random.randint(0,T) # Les temps sont entier à voir
            t1 = random.randint(0,T)
            x.append(Manoeuvre(t0,t1,angle))
        X.append(x)
    return F,X


#Fonction de calcul du cout
# Prend en parametre f une liste d'avions = trajectoire + vitesse

def cout(f):
    N=len(f)
    C=0
    for fi in f:
        manoeuvre=(fi.trajectory).manoeuvre
        C+=(manoeuvre.angle**2)/alMc+(manoeuvre.t1**2+((T-manoeuvre.t0)**2))/Tc
    return C


#Fonction conflit2a2: renvoie les temps de conflit tdeb et tfin entre deux avions
def conflit2a2(f1,f2):
    ptdep1=f1.trajectory.pointDepart
    ptdep2=f2.trajectory.pointDepart
    v1=f1.speed
    v2=f2.speed
    a=(v1.x-v2.x)**2 + (v1.y-v2.y)**2
    b= 2*((ptdep1.x-ptdep2.x)*(v1.x-v2.x) + (ptdep1.y-ptdep2.y)*(v1.y-v2.y))
    c=(ptdep1.x-ptdep2.x)**2 + (ptdep1.y-ptdep2.y)**2 - d**2
    coeff=[a,b,c]
    racines=np.roots(coeff)
    tdeb=racines[0]
    tfin=racines[1]
    if tdeb<0 or tdeb>T:
        if tfin<0 or tfin>T:
            return (0,0)
        else:
            return (0,tfin)
    elif tfin<0 or tfin>T:
        return (tdeb,0)
    else:
        return (tdeb, tfin)



#Fonction de duree de conflit: prend en parametre f une liste d'avions

def dureeConflit(f):
    N=len(f)
    dicoConflits={}
    duree=0
    for i in range(0,N):
        for j in range(0, N):
            if j!=i:
                if conflit2a2(f[i], f[j])!= (0,0):
                    dicoConflits[f[i]]=(f[j], conflit2a2(f[i], f[j]))
                    duree+=(conflit2a2(f[i], f[j])[1]- conflit2a2(f[i], f[j])[0])
                    break # car on s'arrête pour le moment au premier conflit
    return duree/T


#fonciton fitness:
def fitness(f):
    if dureeConflit(f)>0:
        return 1/(2+dureeConflit(f))
    else:
        return 1/2+ 1/cout(f)


