from PyQt5 import QtWidgets
from PyQt5.QtCore import QPoint

import radarview
import math

T = 200

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

class Manoeuvre():
    def __init__(self,t0,angle,t1):
        self.t0 = t0
        self.angle = angle
        self.t1 = t1

class Trajectory():
    def __init__(self,pointDepart, angle0, manoeuvre):
        self.pointDepart = pointDepart
        self.angle0 = angle0
        self.manoeuvre = manoeuvre



if __name__ == "__main__":
    #trajectories = [[QPoint(x, y) for x in range(150)] for y in range(0, 300, 100)]
    man = Manoeuvre(10, math.pi / 7, 15)
    trajectoire = Trajectory(QPoint(0,0),math.pi/4,man)
    vol1 = Flight(100,trajectoire)
    trajectories = [vol1.pointTrajectory()]
    # Initialize Qt
    app = QtWidgets.QApplication([])

    # create the radar view and the time navigation interface
    rad = radarview.RadarView(trajectories)
    rad.move(10, 10)

    # create the QMainWindow and add both widgets
    win = QtWidgets.QMainWindow()
    win.setWindowTitle("Résolution de conflits")
    win.setCentralWidget(rad)
    # win.resize(1000, 600)
    # win.show()
    win.showMaximized()

    # enter the main loop
    app.exec_()


