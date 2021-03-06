from PyQt5 import QtWidgets

import radarview
import probleme as pb
import evolutionDifferentielle as de
import time
import IO
import creationSituation as cS
import matplotlib.pyplot as plt
import constantes as ct
import os

### ---------- MAIN ---------- ###

if __name__ == "__main__":

    if ct.FILE == None:
        t = time.time()
        if ct.SPEED_TYPE == 0:
            liste_vitesse_avion = cS.vitesseConstante(int(
                ct.VITESSE))  # avoir la vitesse des avions (différentes si on choisit la situation aléatoire (mettre une liste de borne min et borne max))
        else:
            print(ct.VITESSE[1:-1].split(','))
            liste_vitesse_avion = cS.vitesseAleatoire(ct.VITESSE[1:-1].split(','))
        type = ct.TYPE_FCT
        if type == 0:
            Flights = cS.cercle(ct.m, ct.RAYON_CERCLE, liste_vitesse_avion)
        elif type == 1:
            Flights = cS.cercle_deforme(ct.m, ct.RAYON_CERCLE, liste_vitesse_avion, ct.EPSILON)
        elif type == 2:
            Flights = cS.hasard(liste_vitesse_avion)
        population, FLIGHTS = pb.creaPop(Flights)
        solution, list_gen_avg, list_gen_best = de.algoDE(pb.fitness, ct.BOUNDS, ct.N_pop, ct.F, ct.CR, ct.ITERATIONS,
                                                          population, FLIGHTS)

        x = [k for k in range(ct.ITERATIONS)]
        yAvg = list_gen_avg
        yBest = list_gen_best
        fig = plt.figure(1, figsize=(20, 10))
        plt.plot(x, yAvg, 'b')
        plt.plot(x, yBest, 'r')
        plt.plot(x, [0.5 for k in range(ct.ITERATIONS)], 'g--')
        plt.title("Evolution de la fitness en fonction du nombre d'itérations")
        plt.legend(["Moyenne population", "Meilleur individu", "Seuil du zéro-conflit"], loc=4)
        plt.xlabel("Itérations")
        plt.ylabel("Fitness")
        tExec = (time.time() - t) / 60
        print("Temps d'exécution: " + str(tExec))
        print("La meilleure solution est: " + str(solution))
        print("Fitness: " + str(pb.fitness(solution, FLIGHTS)))
        # Reconstruire une manoeuvre à partir d'un array (t0,theta, alpha):

        for i, vol in enumerate(Flights):
            vol.manoeuvre = pb.convertAtoM(solution[i])

        date = time.ctime(time.time())
        dateTest = "_".join(date.split()).replace(':', '_')
        os.makedirs(ct.REPERTOIRE, exist_ok=True)
        os.makedirs(ct.REPERTOIRE + ct.REPERTOIRE_FITNESS, exist_ok=True)
        filename = ct.REPERTOIRE + dateTest + '.txt'
        fileFitnessname = ct.REPERTOIRE + ct.REPERTOIRE_FITNESS + dateTest + '.png'

        try:
            IO.write(Flights, filename, tExec)
            plt.savefig(fileFitnessname)
        except Exception:
            print("Problème d'enregistrement du fichier")
        trajectories = [vol.pointTrajectory() for vol in Flights]
        plt.show(block=False)
    else:
        Flights = IO.read(ct.FILE)
        Man = [vol.manoeuvre.convertMtoA() for vol in Flights]
        print(pb.fitness(Man, Flights))

    # Initialisation Qt
    app = QtWidgets.QApplication([])

    # create the radar view and the time navigation interface
    rad = radarview.RadarView(Flights)
    rad.move(10, 10)

    # create the QMainWindow and add both widgets
    win = QtWidgets.QMainWindow()
    win.setWindowTitle("Résolution de conflits")
    win.setCentralWidget(rad)
    win.showMaximized()

    # enter the main loop
    app.exec_()
