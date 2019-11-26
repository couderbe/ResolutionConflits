from PyQt5.QtCore import QPoint
import math
import random

T = 200 # Temps total
N_avion = 20 # Nombre d'avion

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
            t1 = random.randint(t0,T)
            x.append(Manoeuvre(t0,t1,angle))
        X.append(x)
    return F,X
