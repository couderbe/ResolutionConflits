from PyQt5 import QtWidgets
from PyQt5.QtCore import QPoint

import radarview
import testmain as pb
import numpy as np
from cmath import phase
import testDE as de
import time
import IO
import sys
import creationSituation as cS


###----------CONSTANTES--------###
Flights = []
m = 2*3.1416/pb.N_avion
ITERATIONS = 500
RAYON_CERCLE = 30000
FICHIER = "Results/"



if __name__ == "__main__":
    if len(sys.argv)==1:
    #trajectories = [[QPoint(x, y) for x in range(150)] for y in range(0, 300, 100)]
    #man = pb.Manoeuvre(10,50,math.pi / 7)
    #trajectoire = pb.Trajectory(QPoint(0,0),math.pi/4,man)
    #vol1 = pb.Flight(100,trajectoire)
    #trajectories = [vol1.pointTrajectory()]
        t = time.time()
        v = [1 for k in range(pb.N_avion)] # avoir la vitesse des avions (différentes)
        Flights = cS.cercle(m,RAYON_CERCLE,v)
        population = pb.creaPop(Flights)
        solution = de.algoDE(pb.fitness,pb.BOUNDS,pb.N_pop, pb.F, pb.CR, ITERATIONS, population)
        print("Temps d'exécution: " + str((time.time()-t)/60))
        print("La meilleure solution est "+str(solution))
        print(pb.fitness(solution))
## Reconstruire une manoeuvre à partir d'un array (t0,theta, alpha):

        for i,vol in enumerate(Flights):
            vol.manoeuvre = pb.convertAtoM(solution[i])
            print(vol.manoeuvre)
        print(Flights)
        date = time.ctime(time.time())
        dateTest = "_".join(date.split()).replace(':','_')
        filename = FICHIER + dateTest + '.txt'
        try:
            IO.write(Flights, filename)
        except Exception:
            print("Probleme d'enregistrement du fichier")
    #trajectories = [vol.pointTrajectory() for vol in Flights]

    else:
        Flights = IO.read(sys.argv[1])
    # Initialisation Qt
    app = QtWidgets.QApplication([])

    # create the radar view and the time navigation interface
    #rad = radarview.RadarView(Flights)
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

