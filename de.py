import random
import pb
import copy
F = 0.7 # à voir
CR = 0.2 # à voir
# on genere le X à la génération N+1 et on vérifie s'il est valable avec la fonction fitness


# faut il tester l'angle entre -pi/6 ou pi/6 ou paaass ????



# Code de la mutation : On sélectionne trois individus de la génération courante différents deux à deux mais aussi différents de l'individu que l'on souhaite muter. Le nouvel individu v est donné par la relation v=x1+F(x2-x3) où F est le facteur de mutation entre 0 et 2#
# Problème : Il se peut que l'individu créé v soit en dehors des limites bounds, il faut donc écrire une fonction qui vérifie si v est en dehors des frontières ou non. S'il l'est, on déplace v à la frontière la plus proche. Cette fonction s'appelle ensure_bounds#




def ensure_bounds(vec):

    for manoeuver in vec :

            manoeuver.t0 = sorted ([ 0, manoeuver.t0, pb.T])[1]
            manoeuver.theta = sorted([0,manoeuver.theta, 1])[1]
            manoeuver.angle = sorted ([- pb.alphaMax, manoeuver.angle, pb.alphaMax])[1]
            t1 = (pb.T - manoeuver.t0) * manoeuver.theta
            if t1 == 0 :
                manoeuver.angle = 0
                manoeuver.t0 = pb.T
    return vec


def differential_evolution(Flights,cost_func, N_pop, F, CR, maxiter):
    # Flights est la liste de vol
    # F est le facteur de mutation
    # CR est le crossover rate
    # maxiter est le nombre de générations pour lequel on veut faire tourner l'algo
    # N_pop est la taille de la population
    # cost_func => fitness

    # --- INITIALISER LA POPULATION  ---#

    _, population = pb.init(Flights)
    print("Population:  ------>  "+str(population))
    # --- RESOLUTION ---#
    score = cost_func(Flights,population[0])
    for i,elt in enumerate(population):
        print(elt)
        print(cost_func(Flights,elt))
    print(score)
    for i in range(1, maxiter + 1):
        print('GENERATION:', i)
        gen_scores = []  # Stockage des résultats

       # candidats = range(0, N_pop) #candidats correspond au petit x : liste des manoeuvres
        for j in range(0, pb.N_pop):

            # --- MUTATION ---#

            candidats = list(range(0, pb.N_pop))
            candidats.pop(j)
            random_index = random.sample(candidats, 3)
            x_1 = [pb.Manoeuvre(man.t0,man.theta,man.angle) for man in population[random_index[0]]]
            x_2 = [pb.Manoeuvre(man.t0,man.theta,man.angle) for man in population[random_index[1]]]
            x_3 = [pb.Manoeuvre(man.t0,man.theta,man.angle) for man in population[random_index[2]]]
            x_t = population[j]  # Individu cible

            # Définition du vecteur x_diff = x_3 - x_2
            x_diff = [x_2_i - x_3_i for x_2_i, x_3_i in zip(x_2, x_3)] # Soustrait les composantes
            # Définition du vecteur mutant v_mutant par multiplication de x_diff par F et ajout de x_1 (formule du cours)
            v_mutant = [x_1_i + F * x_diff_i for x_1_i, x_diff_i in zip(x_1, x_diff)]
            v_mutant = ensure_bounds(v_mutant)
            # --- CROSSOVER ---#

            v_trial = []

            for k in range(len(x_t)):
                crossover = random.random()

                # On fait du crossover si crossover <= crossover_rate
                if crossover <= CR:
                    v_trial.append(v_mutant[k])

                # S'il n'y pas lieu de faire du crossover
                else:
                    v_trial.append(x_t[k])

            # --- SELECTION ---#

            # On compare notre nouvel individu avec l'individu actuel
            #score_trial = cost_func(v_trial)
            #score_target = cost_func(x_t)
            flights_trial = [pb.Flight(F.speed2,F.pointDepart,F.angle0,v_trial[i]) for i, F in enumerate(Flights)]
            flights_target = [pb.Flight(F.speed2, F.pointDepart, F.angle0, x_t[i]) for i, F in enumerate(Flights)]
            score_trial = cost_func(flights_trial,v_trial)
            score_target = cost_func(flights_target,x_t) #D'une génération à l'autre il faut penser que le score gagnant sera là en target à la prochaine géné
            if score_trial > score_target:
                population[j] = v_trial
                gen_scores.append(score_trial)
                print('Trial  >', score_trial, v_trial)

            else:
                #print('Target  >', score_target, x_t)
                gen_scores.append(score_target)

            # --- RESULTATS ---#

            #gen_avg = sum(gen_scores) / N_avion  # fitness moyen de la génération actuelle
            #gen_best = min(gen_scores)  # fitness du meilleur individu
            gen_sol = population[gen_scores.index(max(gen_scores))]  # solution du meilleur individu
    return gen_sol







