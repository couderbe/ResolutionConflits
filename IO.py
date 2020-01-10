import numpy as np
from PyQt5.QtCore import QPoint
import probleme as pb


###Fonction qui lit
def read(filename):
    Flights = []
    with open(filename, 'r') as file:
        for line in file:
            line2 = [float(elt) for elt in line.split(';')]
            print(line2)
            avion = pb.Flight(np.linalg.norm(np.array([line2[3], line2[4]])), QPoint(line2[0], line2[1]), line2[2],
                              pb.Manoeuvre(line2[5], line2[6], line2[7]))
            Flights.append(avion)
    return Flights


###Fonction qui écrit les résultats pour les sauvegarder
def write(Flights, filename):
    with open(filename, 'w') as file:
        for f in Flights:
            file.write(
                '{0};{1};{2};{3[0]};{3[1]};{4.t0};{4.t1};{4.angle}\n'.format(f.pointDepart.x(), f.pointDepart.y(),
                                                                             f.angle0, f.speed, f.manoeuvre))
