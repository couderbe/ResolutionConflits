from PyQt5 import QtWidgets

import radarview
import probleme as pb
import evolutionDifferentielle as de
import time
import IO
import sys
import creationSituation as cS

###----------CONSTANTES--------###
m = 2 * 3.1416 / pb.N_avion
ITERATIONS = 100
RAYON_CERCLE = 185200 # Rayon du cercle en mètres, correpondant à 100 NM
FICHIER = "Results/"
EPSILON = 0.8

if __name__ == "__main__":
    if len(sys.argv) == 1:
        t = time.time()
        v = [1 for k in range(pb.N_avion)]  # avoir la vitesse des avions (différentes)
        Flights = cS.cercle_deforme(m, RAYON_CERCLE, v, EPSILON)
        population = pb.creaPop(Flights)
        solution = de.algoDE(pb.fitness, pb.BOUNDS, pb.N_pop, pb.F, pb.CR, ITERATIONS, population)
        print("Temps d'exécution: " + str((time.time() - t) / 60))
        print("La meilleure solution est " + str(solution))
        print(pb.fitness(solution))
        ## Reconstruire une manoeuvre à partir d'un array (t0,theta, alpha):

        for i, vol in enumerate(Flights):
            vol.manoeuvre = pb.convertAtoM(solution[i])
            print(vol.manoeuvre)
        print(Flights)
        date = time.ctime(time.time())
        dateTest = "_".join(date.split()).replace(':', '_')
        filename = FICHIER + dateTest + '.txt'
        try:
            IO.write(Flights, filename)
        except Exception:
            print("Probleme d'enregistrement du fichier")
    # trajectories = [vol.pointTrajectory() for vol in Flights]

    else:
        Flights = IO.read(sys.argv[1])
    # Initialisation Qt
    app = QtWidgets.QApplication([])

    # create the radar view and the time navigation interface
    # rad = radarview.RadarView(Flights)
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
