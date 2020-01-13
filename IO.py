import numpy as np
from PyQt5.QtCore import QPoint
import probleme as pb
import constantes as ct

### Fonction permettant de lire un fichier texte contenant les paramètres de tous les avions et leurs manoeuvres
def read(filename):
    Flights = []
    with open(filename, 'r') as file:
        for line in file:
            line2 = [float(elt) for elt in line.split(';')]
            if len(line2 == 3):
                ct.T = line2[0]
                ct.ITERATIONS = line2[1]
            else:
                avion = pb.Flight(np.linalg.norm(np.array([line2[3], line2[4]])), QPoint(line2[0], line2[1]), line2[2],
                                pb.Manoeuvre(line2[5], line2[6], line2[7]))
                Flights.append(avion)
    return Flights


### Fonction écrivant les paramètres de tous les avions de la solution trouvée, afin de la stocker et de pouvoir la
### consulter ultérieurement.
def write(Flights, filename, tExec):
    with open(filename, 'w') as file:
        file.write('{0};{1};{2}\n'.format(ct.T,ct.ITERATIONS,tExec))
        for f in Flights:
            file.write(
                '{0};{1};{2};{3[0]};{3[1]};{4.t0};{4.t1};{4.angle}\n'.format(f.pointDepart.x(), f.pointDepart.y(),
                                                                             f.angle0, f.speed, f.manoeuvre))

def readCommand(args):
    for i,arg in enumerate(args):
        if arg[0] == '-':
            f_constante = ct.dictParam[arg[1:]]
            f_constante(args[i+1])
    ct.recalculConsts()