import random
import numpy as np


def func1(x):
    # Sphere function, use any bounds, f(0,...,0)=0
    return sum([np.linalg.norm(x[i]) for i in range(len(x))])


def initPop(bounds, popsize):
    # --- INITIALIZE A POPULATION (step #1) ----------------+
    population = []
    for i in range(0, popsize):
        indv = []
        for j in range(len(bounds)):
            indv.append(random.uniform(bounds[j][0], bounds[j][1]))
        population.append(indv)
    return population


def ensure_bounds(vec, bounds):
    vec_new = []
    # cycle through each variable in vector
    for elt in (vec):
        elt_new = np.zeros(len(elt))
        for i in range(len(elt)):
            # variable exceedes the minimum boundary
            if elt[i] < bounds[i][0]:
                elt_new[i] = bounds[i][0]

            # variable exceedes the maximum boundary
            if elt[i] > bounds[i][1]:
                elt_new[i] = bounds[i][1]

            # the variable is fine
            if bounds[i][0] <= elt[i] <= bounds[i][1]:
                elt_new[i] = elt[i]
        vec_new.append(elt_new)
    return vec_new


def algoDE(cost_func, bounds, popsize, mutate, recombination, maxiter, popInit):
    # --- INITIALISATION ----------------+
    population = popInit

    # --- RESOLUTION --------------------+
    popScore = [cost_func(population[i]) for i in range(popsize)]
    # cycle through each generation (step #2)
    for i in range(1, maxiter + 1):
        print('GENERATION: ', i)

        gen_scores = []  # score keeping

        # cycle through each individual in the population
        for j in range(0, popsize):

            # --- MUTATION (step #3.A) ---------------------+

            # select three random vector index positions [0, popsize), not including current vector (j)
            canidates = list(range(0, popsize))
            canidates.pop(j)
            random_index = random.sample(canidates, 3)

            x_1 = population[random_index[0]]
            x_2 = population[random_index[1]]
            x_3 = population[random_index[2]]
            x_t = population[j]  # target individual

            # subtract x3 from x2, and create a new vector (x_diff)
            x_diff = [x_2_i - x_3_i for x_2_i, x_3_i in zip(x_2, x_3)]

            # multiply x_diff by the mutation factor (F) and add to x_1
            v_donor = [x_1_i + mutate * x_diff_i for x_1_i, x_diff_i in zip(x_1, x_diff)]
            v_donor = ensure_bounds(v_donor, bounds)

            # --- RECOMBINATION (step #3.B) ----------------+

            v_trial = []
            for k in range(len(x_t)):
                crossover = random.random()
                if crossover <= recombination:
                    v_trial.append(v_donor[k])

                else:
                    v_trial.append(x_t[k])
            # --- GREEDY SELECTION (step #3.C) -------------+

            score_trial = cost_func(v_trial)

            # score_target = cost_func(x_t)

            if score_trial > popScore[j]:
                population[j] = v_trial
                gen_scores.append(score_trial)
                popScore[j] = score_trial
                # print('   >', score_trial, v_trial)

            else:
                # print('   >', score_target, x_t)
                gen_scores.append(popScore[j])

        # --- SCORE KEEPING --------------------------------+

        gen_avg = sum(gen_scores) / popsize  # current generation avg. fitness
        gen_best = max(gen_scores)  # fitness of best individual
        gen_sol = population[gen_scores.index(max(gen_scores))]  # solution of best individual

        # print('> GENERATION AVERAGE:', gen_avg,'\n')
        print('> GENERATION BEST:', gen_best, '\n')
        # print('> BEST SOLUTION:', gen_sol, '\n')

    return gen_sol
