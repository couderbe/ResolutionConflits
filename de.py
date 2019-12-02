import random


N = 20 #nombre d'avion attention Benoit l'a
F = 1.5 # à voir
CR = 0.8 # à voir
def genX (X) :
    genereX = []
    for i,x in enumerate (X):
        R = random.randint(0,N-1)
        l = [k for k in range(N) if k != i]
        a,b,c = random.sample(l,3) # les indices différents entre eux et de i
        genere_x = []
        for k,maneuver in enumerate (x):
            difference = X[b][k] - X[c][k]
            if (k == R) or (random.random() < CR) and (difference.t1 >= 0) and (difference.t0 >= 0): #t1 est la durée de demie manoeuvre et non pas l'instant où la manoeuvre se finit
                genere_x.append (X[a][k] + F * difference )
            else :
                genere_x.append(maneuver)
        genereX.append(genere_x)
    for i, x in enumerate(X):
        if de.fitness (genereX[i]) < de.fitness(x):
            genereX[i] = x
    return genereX
# on genere le X à la génération N+1 et on vérifie s'il est valable avec la fonction fitness


# faut il tester l'angle entre -pi/6 ou pi/6 ou paaass ????