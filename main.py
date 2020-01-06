from PyQt5 import QtWidgets
from PyQt5.QtCore import QPoint

import radarview
import testmain as pb
import numpy as np
from cmath import phase
import testDE as de
import time
import random

Flights = []
m = 2*3.1416/pb.N_avion
ITERATIONS = 100
RAYON_CERCLE = 30000

if __name__ == "__main__":
    #trajectories = [[QPoint(x, y) for x in range(150)] for y in range(0, 300, 100)]
    #man = pb.Manoeuvre(10,50,math.pi / 7)
    #trajectoire = pb.Trajectory(QPoint(0,0),math.pi/4,man)
    #vol1 = pb.Flight(100,trajectoire)
    #trajectories = [vol1.pointTrajectory()]
    t = time.time()
    v = [1 for k in range(pb.N_avion)] # avoir la vitesse des avions (différentes)
    Flights = [pb.Flight(250, QPoint(v[k]*RAYON_CERCLE*np.cos(m*k), v[k]*RAYON_CERCLE*np.sin(m*k)),np.pi+phase(complex(v[k]*RAYON_CERCLE*np.cos(m*k),v[k]*RAYON_CERCLE*np.sin(m*k))), pb.Manoeuvre(pb.T, 0, 0)) for k in range(pb.N_avion)]
    population = pb.creaPop(Flights)
    solution = de.algoDE(pb.fitness,pb.BOUNDS,pb.N_pop, pb.F, pb.CR, ITERATIONS, population)
    print("Temps d'exécution: " + str((time.time()-t)/60))
    print("La meilleure solution est "+str(solution))
    print(pb.fitness(solution))
## Reconstruire une manoeuvre à partir d'un array (t0,theta, alpha):

    for i,vol in enumerate(Flights):
        # manArray = np.array([0,0,0])
        # manArray[0] = solution[i][0]
        # manArray[1] = solution[i][1]
        # manArray[2] = solution[i][2]
        vol.manoeuvre = pb.convertAtoM(solution[i])
        print(vol.manoeuvre)
    print(Flights)
    #trajectories = [vol.pointTrajectory() for vol in Flights]


    # Initialisation Qt
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


