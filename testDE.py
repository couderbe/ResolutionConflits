import random


def initPop(bounds, popsize ):
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
        elt_new=(0*len(elt))
        for i in len(elt);
        # variable exceedes the minimum boundary
            if elt[i] < bounds[i][0]:
                elt_new[i]=bounds[i][0]

        # variable exceedes the maximum boundary
            if elt[i] > bounds[i][1]:
                elt_new[i]=bounds[i][1]

        # the variable is fine
            if bounds[i][0] <= elt[i] <= bounds[i][1]:
                elt_new[i]=elt[i]
        vec_new.append(elt_new)
    return vec_new


def algoDE(bounds, popsize, mutate, maxiter, popInit):
    # --- INITIALISATION ----------------+
    population = popInit

    # --- RESOLUTION --------------------+

    # cycle through each generation (step #2)
    for i in range(1, maxiter + 1):

        # cycle through each individual in the population (step #3)
        for j in range(0, popsize):
            # --- MUTATION ---------------+

            # selection de 3 indices aléatoires excluant j
            candidates = range(0, popsize)
            candidates.remove(j)
            random_index = random.sample(candidates, 3)

            x_1 = population[random_index[0]]
            x_2 = population[random_index[1]]
            x_3 = population[random_index[2]]
            x_t = population[j]  # target individual

            # différence de x3 et x2 (x_diff)
            x_diff = [x_2_i - x_3_i for x_2_i, x_3_i in zip(x_2, x_3)]

            # multiply x_diff by the mutation factor (F) and add to x_1
            v_donor = [x_1_i + mutate * x_diff_i for x_1_i, x_diff_i in zip(x_1, x_diff)]
            v_donor = ensure_bounds(v_donor, bounds)

            # --- RECOMBINATION ----------------+

            v_trial = []
            # cycle through each variable in our target vector
            for k in range(len(x_t)):
                crossover = random.random()

                # recombination occurs when crossover <= recombination rate
                if crossover <= recombination:
                    v_trial.append(v_donor[k])

                # recombination did not occur
                else:
                    v_trial.append(x_t[k])

    return best_individual
