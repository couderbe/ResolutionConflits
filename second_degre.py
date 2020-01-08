import math
import time
import random
import numpy as np

a = random.uniform(-1000, 1000)
b = random.uniform(-1000, 1000)
c = random.uniform(-1000, 1000)

def second_degre (a,b,c) :
    delta = b**2 - 4*a*c
    print("delta" + str(delta))
    if delta > 0 :
        racine1 = (-b - math.sqrt(delta) ) / 2*a
        racine2 = (b-math.sqrt(delta))/2*a
        return [racine1, racine2]


debut = time.time()
second_degre(a,b,c)
time_fonction = time.time() - debut


coeff = [a,b,c]

debutN = time.time()
np.roots(coeff)
time_root = time.time() - debutN

print(time_fonction , time_root)
