import random
import numpy as np


# Cette fonction sert à créer la population de départ de l'algorithme DE
def initPop(bounds, popsize):
    population = []
    for i in range(0, popsize):
        indv = []
        for j in range(len(bounds)):
            indv.append(random.uniform(bounds[j][0], bounds[j][1]))
        population.append(indv)
    return population


# Cette fonction sert à vérifier que les individus générés par les mutations/cross_over
# respectent les limites définies pour les manoeuvres
def keepLimits(vec, bounds):
    vec_new = []
    # Boucle sur tous les éléments du vecteur
    for elt in (vec):
        elt_new = np.zeros(len(elt))
        for i in range(len(elt)):
            # Si l'élément est inférieur à la limite basse
            if elt[i] < bounds[i][0]:
                elt_new[i] = bounds[i][0]

            # Si l'élément est supérieur à la limite haute
            if elt[i] > bounds[i][1]:
                elt_new[i] = bounds[i][1]

            # On conserve l'élément sinon
            if bounds[i][0] <= elt[i] <= bounds[i][1]:
                elt_new[i] = elt[i]
        vec_new.append(elt_new)
    return vec_new


def algoDE(cost_func, bounds, popsize, mutate, recombination, maxiter, popInit, FLIGHTS):
    ### Initialisation de la population
    population = popInit

    ### Calcul du "score": fitness des individus de la population
    popScore = [cost_func(population[i], FLIGHTS) for i in range(popsize)]

    list_gen_avg = []
    list_gen_best = []

    # Boucle sur toutes les générations (nombre de générations: maxiter)
    for i in range(1, maxiter + 1):
        print('GENERATION: ', i)

        gen_scores = []  # score keeping

        ### Mutations et Cross-Overs de la population:
        # Boucle sur les individus de la population:
        for j in range(0, popsize):

            # Sélection de 3 individus différents de l'individu j
            # Pour cela, on sélectionne au hasard 3 indices différents de j
            candidats = list(range(0, popsize))
            candidats.pop(j)
            random_index = random.sample(candidats, 3)

            x_1 = population[random_index[0]]
            x_2 = population[random_index[1]]
            x_3 = population[random_index[2]]
            x_t = population[j]  # target individual

            # Etapes de "Mutation" et "Cross_over" de j:
            # x_mute est le candidat éventuel au remplacement de l'individu j
            x = [x_2_i - x_3_i for x_2_i, x_3_i in zip(x_2, x_3)]  # Cross_over
            x_mute = [x_1_i + mutate * x_i for x_1_i, x_i in zip(x_1, x)]  # Mutation
            x_mute = keepLimits(x_mute, bounds)  # Limitation

            # Etape de "Recombinaison":
            # On remplace chaque composante de l'individu j avec une probabilité égale à "recombination".
            x_replace = []
            for k in range(len(x_t)):
                crossover = random.random()
                if crossover <= recombination:
                    x_replace.append(x_mute[k])

                else:
                    x_replace.append(x_t[k])

            # Sélection de l'individu qui maximise la fonction de coût:
            score_mute = cost_func(x_replace, FLIGHTS)

            if score_mute > popScore[j]:
                population[j] = x_replace
                gen_scores.append(score_mute)
                popScore[j] = score_mute

            else:
                gen_scores.append(popScore[j])

        # Conservation des différentes valeurs de la fonction de coût de la génération courante:
        gen_avg = sum(gen_scores) / popsize  # Moyenne des scores de la génération courante
        gen_best = max(gen_scores)  # Score du meilleur individu
        gen_sol = population[
            gen_scores.index(max(gen_scores))]  # Solution au problème: individu qui maximise la fonction de coût

        list_gen_avg.append(gen_avg)
        list_gen_best.append(gen_best)

        # print('> GENERATION AVERAGE:', gen_avg,'\n')
        print('> GENERATION BEST:', gen_best, '\n')
        # print('> BEST SOLUTION:', gen_sol, '\n')

    return gen_sol, list_gen_avg, list_gen_best
