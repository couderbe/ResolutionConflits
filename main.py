from PyQt5 import QtWidgets

import radarview
import probleme as pb
import evolutionDifferentielle as de
import time
import IO
import sys
import creationSituation as cS
import matplotlib.pyplot as plt

### ---------- CONSTANTES ---------- ###
m = 2 * 3.1416 / pb.N_avion
ITERATIONS = 100
RAYON_CERCLE = 185200 # Rayon du cercle en mètres, correpondant à 100 NM
FICHIER = "Results/"
REPERTOIRE_FITNESS = "FitnessEvolution/"
EPSILON = 0.8
VITESSE = 250

### ---------- MAIN ---------- ###

if __name__ == "__main__":
    if len(sys.argv) == 1:
        t = time.time()
        liste_vitesse_avion = cS.vitesseConstante(VITESSE)  # avoir la vitesse des avions (différentes si on choisit la situation aléatoire (mettre une liste de borne min et borne max))
        Flights = cS.cercle(m,RAYON_CERCLE,liste_vitesse_avion)
        population = pb.creaPop(Flights)
        solution,list_gen_avg,list_gen_best = de.algoDE(pb.fitness, pb.BOUNDS, pb.N_pop, pb.F, pb.CR, ITERATIONS, population)


        x = [k for k in range(ITERATIONS)]
        yAvg = list_gen_avg
        yBest = list_gen_best
        fig = plt.figure(1, figsize=(20, 10))
        plt.plot(x, yAvg, 'b')
        plt.plot(x, yBest, 'r')
        plt.plot(x, [0.5 for k in range(ITERATIONS)], 'g--')
        plt.title("Evolution de la fitness en fonction du nombre d'itérations")
        plt.legend(["Moyenne population", "Meilleur individu", "Seuil du zéro-conflit"], loc=4)
        plt.xlabel("Itérations")
        plt.ylabel("Fitness")

        print("Temps d'exécution: " + str((time.time() - t) / 60))
        print("La meilleure solution est " + str(solution))
        print(pb.fitness(solution))
        # Reconstruire une manoeuvre à partir d'un array (t0,theta, alpha):

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
        trajectories = [vol.pointTrajectory() for vol in Flights]
        # fileFitnessname = FICHIER + REPERTOIRE_FITNESS + dateTest + '.png'
        # plt.savefig(fileFitnessname)
        plt.show(block = False)
    else:
        Flights = IO.read(sys.argv[1])
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
