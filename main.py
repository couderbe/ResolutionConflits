from PyQt5 import QtWidgets
from PyQt5.QtCore import QPoint

import radarview
import pb
import numpy as np
from cmath import phase
import de
import time
import random

Flights = []
m = 2*3.1416/pb.N_avion


if __name__ == "__main__":
    #trajectories = [[QPoint(x, y) for x in range(150)] for y in range(0, 300, 100)]
    #man = pb.Manoeuvre(10,50,math.pi / 7)
    #trajectoire = pb.Trajectory(QPoint(0,0),math.pi/4,man)
    #vol1 = pb.Flight(100,trajectoire)
    #trajectories = [vol1.pointTrajectory()]
    t = time.time()
    v = [1 for k in range(pb.N_avion)] # avoir la vitesse des avions (différentes)
    Flights = [pb.Flight(250, QPoint(v[k ]*30000*np.cos(m*k), v[k]*30000*np.sin(m*k)),np.pi+phase(complex(v[k]*30000*np.cos(m*k),v[k]*30000*np.sin(m*k))), pb.Manoeuvre(pb.T, 0, 0)) for k in range(pb.N_avion)]
    solution = de.differential_evolution(Flights,pb.fitness,pb.N_pop, de.F, de.CR, 150)
    print("Temps d'exécution: " + str((time.time()-t)/60))
    print("La meilleure solution est "+str(solution))
    for i,flight in enumerate(Flights):
        flight.manoeuvre = solution[i]
    trajectories = [vol.pointTrajectory() for vol in Flights]
    # Initialize Qt
    app = QtWidgets.QApplication([])

    # create the radar view and the time navigation interface
    rad = radarview.RadarView(Flights)
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


