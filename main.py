from PyQt5 import QtWidgets
from PyQt5.QtCore import QPoint

import radarview
import math
import pb


if __name__ == "__main__":
    #trajectories = [[QPoint(x, y) for x in range(150)] for y in range(0, 300, 100)]
    man = pb.Manoeuvre(10,50,math.pi / 7)
    trajectoire = pb.Trajectory(QPoint(0,0),math.pi/4,man)
    vol1 = pb.Flight(100,trajectoire)
    trajectories = [vol1.pointTrajectory()]
    #trajectories = [vol.pointTrajectory() for vol in pb.init()[0]]
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


