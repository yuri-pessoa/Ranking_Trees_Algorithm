###############################################################################

# Required Libraries
import matplotlib.pyplot as plt
import numpy  as np
import random
import os

###############################################################################

# Function: Target
def target_function():
    return

# Function: Clip Thresholds
def clip_thresholds(population, indv = 0, size = 3, min_values = [-5,-5], max_values = [5,5]):
    size = size
    for i in range(0, size):
        if (population[indv][size*1 + i] > population[indv][size*2 + i]):
            population[indv][size*1 + i] = population[indv][size*2 + i]
        if (population[indv][size*2 + i] > population[indv][size*3 + i] and population[indv][size*1 + i] > population[indv][size*3 + i]):
            population[indv][size*1 + i] = population[indv][size*3 + i]
            population[indv][size*2 + i] = population[indv][size*3 + i]      
        if (population[indv][size*2 + i] > population[indv][size*3 + i] and population[indv][size*1 + i] < population[indv][size*3 + i]):
            population[indv][size*2 + i] = population[indv][size*3 + i] 
    population[indv,:-1] = np.clip(population[indv,:-1], min_values, max_values)
    return population

# Function: Initialize Variables
def initial_population(population_size = 5, size = 3, min_values = [-5,-5], max_values = [5,5], target_function = target_function):
    population = np.zeros((population_size, len(min_values) + 1))
    for i in range(0, population_size):
        for j in range(0, len(min_values)):
             population[i,j] = random.uniform(min_values[j], max_values[j]) 
        population = clip_thresholds(population, indv = i, size = size, min_values = min_values, max_values = max_values)
        population[i,-1] = target_function(population[i,0:population.shape[1]-1])
    return population

# Function: Fitness
def fitness_function(population): 
    fitness = np.zeros((population.shape[0], 2))
    for i in range(0, fitness.shape[0]):
        fitness[i,0] = 1/(1+ population[i,-1] + abs(population[:,-1].min()))
    fit_sum = fitness[:,0].sum()
    fitness[0,1] = fitness[0,0]
    for i in range(1, fitness.shape[0]):
        fitness[i,1] = (fitness[i,0] + fitness[i-1,1])
    for i in range(0, fitness.shape[0]):
        fitness[i,1] = fitness[i,1]/fit_sum
    return fitness

# Function: Selection
def roulette_wheel(fitness): 
    ix = 0
    random = int.from_bytes(os.urandom(8), byteorder = "big") / ((1 << 64) - 1)
    for i in range(0, fitness.shape[0]):
        if (random <= fitness[i, 1]):
          ix = i
          break
    return ix

# Function: Offspring
def breeding(population, fitness, min_values = [-5,-5], max_values = [5,5], size = 3, mu = 1, elite = 0, target_function = target_function):
    offspring = np.copy(population)
    b_offspring = 0
    if (elite > 0):
        preserve = np.copy(population[population[:,-1].argsort()])
        for i in range(0, elite):
            for j in range(0, offspring.shape[1]):
                offspring[i,j] = preserve[i,j]
    for i in range (elite, offspring.shape[0]):
        parent_1, parent_2 = roulette_wheel(fitness), roulette_wheel(fitness)
        while parent_1 == parent_2:
            parent_2 = random.sample(range(0, len(population) - 1), 1)[0]
        for j in range(0, offspring.shape[1] - 1):
            rand = int.from_bytes(os.urandom(8), byteorder = "big") / ((1 << 64) - 1)
            rand_b = int.from_bytes(os.urandom(8), byteorder = "big") / ((1 << 64) - 1)                                
            if (rand <= 0.5):
                b_offspring = 2*(rand_b)
                b_offspring = b_offspring**(1/(mu + 1))
            elif (rand > 0.5):  
                b_offspring = 1/(2*(1 - rand_b))
                b_offspring = b_offspring**(1/(mu + 1))       
            offspring[i,j] = np.clip(((1 + b_offspring)*population[parent_1, j] + (1 - b_offspring)*population[parent_2, j])/2, min_values[j], max_values[j])           
            if(i < population.shape[0] - 1):   
                offspring[i+1,j] = np.clip(((1 - b_offspring)*population[parent_1, j] + (1 + b_offspring)*population[parent_2, j])/2, min_values[j], max_values[j]) 
        offspring = clip_thresholds(offspring, indv = i, size = size, min_values = min_values, max_values = max_values)
        offspring[i,-1] = target_function(offspring[i,0:offspring.shape[1]-1]) 
    return offspring
 
# Function: Mutation
def mutation(offspring, mutation_rate = 0.1, eta = 1, size = 3, min_values = [-5,-5], max_values = [5,5], target_function = target_function):
    d_mutation = 0            
    for i in range (0, offspring.shape[0]):
        for j in range(0, offspring.shape[1] - 1):
            probability = int.from_bytes(os.urandom(8), byteorder = "big") / ((1 << 64) - 1)
            if (probability < mutation_rate):
                rand = int.from_bytes(os.urandom(8), byteorder = "big") / ((1 << 64) - 1)
                rand_d = int.from_bytes(os.urandom(8), byteorder = "big") / ((1 << 64) - 1)                                     
                if (rand <= 0.5):
                    d_mutation = 2*(rand_d)
                    d_mutation = d_mutation**(1/(eta + 1)) - 1
                elif (rand > 0.5):  
                    d_mutation = 2*(1 - rand_d)
                    d_mutation = 1 - d_mutation**(1/(eta + 1))                
                offspring[i,j] = np.clip((offspring[i,j] + d_mutation), min_values[j], max_values[j])
        offspring = clip_thresholds(offspring, indv = i, size = size, min_values = min_values, max_values = max_values)
        offspring[i,-1] = target_function(offspring[i,0:offspring.shape[1]-1])                        
    return offspring

# Function: GA
def genetic_algorithm(population_size = 5, mutation_rate = 0.1, elite = 0, min_values = [-5,-5], max_values = [5,5], eta = 1, mu = 1, generations = 50, size = 3, target_function = target_function):    
    count = 0
    population = initial_population(population_size = population_size, min_values = min_values, max_values = max_values, size = size, target_function = target_function)
    fitness = fitness_function(population)    
    elite_ind = np.copy(population[population[:,-1].argsort()][0,:])
    while (count <= generations):  
        offspring = breeding(population, fitness, min_values = min_values, max_values = max_values, mu = mu, elite = elite, size = size, target_function = target_function) 
        population = mutation(offspring, mutation_rate = mutation_rate, eta = eta, min_values = min_values, max_values = max_values, size = size, target_function = target_function)
        fitness = fitness_function(population)
        value = np.copy(population[population[:,-1].argsort()][0,:])
        if(elite_ind[-1] > value[-1]):
            elite_ind = np.copy(value) 
        count = count + 1      
    return elite_ind 

###############################################################################

# Function: Global Concordance Matrix
def global_concordance_matrix(dataset, P, Q, W):
    global_concordance = np.zeros((dataset.shape[0], dataset.shape[0]))
    for k in range(0, dataset.shape[1]):
        for i in range(0, global_concordance.shape[0]):
            for j in range(0, global_concordance.shape[1]):
                if (dataset[j,k] - dataset[i,k] >= P[k] ):
                    global_concordance[i,j] = global_concordance[i,j] + W[k]*0
                elif (dataset[j,k] - dataset[i,k] <= Q[k] ):
                    global_concordance[i,j] = global_concordance[i,j] + W[k]*1
                elif (dataset[j,k] - dataset[i,k] > Q[k] and dataset[j,k] - dataset[i,k] < P[k]):
                    global_concordance[i,j] = global_concordance[i,j] + W[k]*((P[k] - dataset[j,k] + dataset[i,k]) / (P[k] - Q[k]))
    if (np.sum(W) != 0):
        global_concordance = global_concordance/np.sum(W)
    return global_concordance

# New Function: Partial Concordance Matrix

def partial_concordance_matrix(dataset, P, Q):
    partial_concordance = np.zeros((dataset.shape[0], dataset.shape[0]))
    for k in range(0, dataset.shape[1]):
        for i in range(0, partial_concordance.shape[0]):
            for j in range(0, partial_concordance.shape[1]):
                if (dataset[j,k] - dataset[i,k] >= P[k]):
                    partial_concordance[i,j] = 0
                elif (dataset[j,k] - dataset[i,k] <= Q[k]):
                    partial_concordance[i,j] = 1
                elif (dataset[j,k] - dataset[i,k] < P[k] and dataset[j,k] - dataset[i,k] > Q[k]):
                    partial_concordance[i,j] = ((P[k] - dataset[j,k] + dataset[i,k]) / (P[k] - Q[k]))
    return partial_concordance

# New Function: Partial Discordance Matrix

def partial_discordance_matrix(dataset, P, V):
    partial_discordance = np.zeros((dataset.shape[0], dataset.shape[0]))
    for k in range(0, dataset.shape[1]):
        for i in range(0, partial_discordance.shape[0]):
            for j in range(0, partial_discordance.shape[1]):
                if (dataset[j,k] - dataset[i,k] <= P[k]):
                    partial_discordance[i,j] = 0
                elif (dataset[j,k] - dataset[i,k] >= V[k]):
                    partial_discordance[i,j] = 1
                elif (dataset[j,k] - dataset[i,k] > P[k] and dataset[j,k] - dataset[i,k] < V[k]):
                    partial_discordance[i,j] = (dataset[j,k] - dataset[i,k] - P[k]) / (V[k] - P[k])
    return partial_discordance

# Function: Credibility Matrix
def credibility_matrix (dataset, global_concordance, P, V):
    credibility = np.copy(global_concordance)
    for i in range(0, credibility.shape[0]):
        for j in range(0, credibility.shape[1]):
            discordance_k = 0
            value         = 1
            for k in range(0, dataset.shape[1]):
                if (dataset[j,k] - dataset[i,k] <= P[k] ):
                    discordance_k = 0
                elif (dataset[j,k] - dataset[i,k] >= V[k] ):
                    discordance_k = 1
                elif (dataset[j,k] - dataset[i,k] > P[k] and dataset[j,k] - dataset[i,k] < V[k]):
                    discordance_k = (dataset[j,k] - dataset[i,k] - P[k]) / (V[k] - P[k])
                if (discordance_k > global_concordance[i,j]):
                    value = ((1-discordance_k) / (1-global_concordance[i,j]))
                else:
                    value = 1
                credibility[i,j] = credibility[i,j]*value
                if (i == j):
                    credibility[i,j] = 0
    return credibility

# Function: Qualification
def qualification(credibility):
    lambda_max = np.max(credibility)
    lambda_s   = 0.30 - 0.15*lambda_max
    lambda_L   = credibility[credibility < (lambda_max - lambda_s)]
    if (lambda_L.shape[0] > 0):
        lambda_L = lambda_L.max()
    else:
        lambda_L = 0
    matrix_d   = np.zeros((credibility.shape[0], credibility.shape[0]))
    for i in range(0, credibility.shape[0]):
        for j in range(0, credibility.shape[0]):
            if (i != j):
                if (credibility[i,j] > lambda_L and credibility[i,j] > credibility[j,i] + lambda_s):
                   matrix_d[i,j] = 1.0                  
    rows = np.sum(matrix_d, axis = 1)
    cols = np.sum(matrix_d, axis = 0)  
    qual = rows - cols
    return qual

# Function: Destilation D
def destilation_descending(credibility):
    alts = list(range(1, credibility.shape[0] + 1)) 
    alts = ['a' + str(alt) for alt in alts]
    rank = []    
    while len(alts) > 0:
        qual = qualification(credibility)
        if (np.where(qual == np.amax(qual))[0].shape[0] > 1):
            index           = np.where(qual == np.amax(qual))[0]
            credibility_tie = credibility[index[:, None], index] 
            qual_tie        = qualification(credibility_tie)
            while (np.where(qual_tie == np.amax(qual_tie))[0].shape[0] > 1 and np.where(qual_tie == np.amax(qual_tie))[0].shape[0] < np.where(qual == np.amax(qual))[0].shape[0]):
                qual            = qualification(credibility_tie)
                index_tie       = np.where(qual == np.amax(qual))[0]
                credibility_tie = credibility_tie[index_tie[:, None], index_tie] 
                qual_tie        = qualification(credibility_tie)   
                for i in range(index.shape[0]-1, -1, -1):
                    if (np.isin(i, index_tie) == False):
                        index = np.delete(index, i, axis = 0)
            if (np.where(qual_tie == np.amax(qual_tie))[0].shape[0] > 1):
                ties = ''
                for i in range(0, index.shape[0]):
                    ties = ties + alts[index[i]]
                    if (i != index.shape[0] - 1):
                        ties = ties + '; '
                rank.append(ties)
                for i in range(index.shape[0]-1, -1, -1):
                    del alts[index[i]]
            else:
                index_tie = int(np.where(qual_tie == np.amax(qual_tie))[0])
                index     = index[index_tie]
                rank.append(alts[index])
                del alts[index]
        else:
            index = int(np.where(qual == np.amax(qual))[0])
            rank.append(alts[index])
            del alts[index]
        credibility = np.delete(credibility, index, axis = 1)
        credibility = np.delete(credibility, index, axis = 0)
    return rank

# Function: Destilation A
def destilation_ascending(credibility):
    alts = list(range(1, credibility.shape[0] + 1)) 
    alts = ['a' + str(alt) for alt in alts]
    rank = []
    while len(alts) > 0:
        qual = qualification(credibility)
        if (np.where(qual == np.amin(qual))[0].shape[0] > 1):
            index           = np.where(qual == np.amin(qual))[0]
            credibility_tie = credibility[index[:, None], index] 
            qual_tie        = qualification(credibility_tie)
            while (np.where(qual_tie == np.amin(qual_tie))[0].shape[0] > 1 and np.where(qual_tie == np.amin(qual_tie))[0].shape[0] < np.where(qual == np.amin(qual))[0].shape[0]):
                qual            = qualification(credibility_tie)
                index_tie       = np.where(qual == np.amin(qual))[0]
                credibility_tie = credibility_tie[index_tie[:, None], index_tie] 
                qual_tie        = qualification(credibility_tie)
                for i in range(index.shape[0]-1, -1, -1):
                    if (np.isin(i, index_tie) == False):
                        index = np.delete(index, i, axis = 0)
            if (np.where(qual_tie == np.amin(qual_tie))[0].shape[0] > 1):
                ties = ''
                for i in range(0, index.shape[0]):
                    ties = ties + alts[index[i]]
                    if (i != index.shape[0] - 1):
                        ties = ties + '; '
                rank.append(ties)
                for i in range(index.shape[0]-1, -1, -1):
                    del alts[index[i]]
            else:
                index_tie = int(np.where(qual_tie == np.amin(qual_tie))[0])
                index     = index[index_tie]
                rank.append(alts[index])
                del alts[index]
        else:
            index = int(np.where(qual == np.amin(qual))[0])
            rank.append(alts[index])
            del alts[index]
        credibility = np.delete(credibility, index, axis = 1)
        credibility = np.delete(credibility, index, axis = 0)
    rank = rank[ : : -1]
    return rank

# Function: Pre-Order Matrix
def pre_order_matrix(rank_D, rank_A, number_of_alternatives):
    alts   = list(range(1, number_of_alternatives + 1)) 
    alts   = ['a' + str(alt) for alt in alts]
    alts_D = [0]*number_of_alternatives
    alts_A = [0]*number_of_alternatives
    for i in range(0, number_of_alternatives):
        for j in range(0, len(rank_D)):
            if (alts[i] in rank_D[j]):
                alts_D[i] = j + 1
        for k in range(0, len(rank_A)):
            if (alts[i] in rank_A[k]):
                alts_A[i] = k + 1    
    po_string = np.empty((number_of_alternatives, number_of_alternatives), dtype = 'U25')
    po_string.fill('-')
    for i in range(0, number_of_alternatives):
        for j in range(0, number_of_alternatives): 
            if (i < j):
                if ( (alts_D[i] < alts_D[j] and alts_A[i] < alts_A[j]) or (alts_D[i] == alts_D[j] and alts_A[i] < alts_A[j]) or (alts_D[i] < alts_D[j] and alts_A[i] == alts_A[j]) ):
                    po_string[i,j] = 'P+'
                    po_string[j,i] = 'P-'
                if ( (alts_D[i] > alts_D[j] and alts_A[i] > alts_A[j]) or (alts_D[i] == alts_D[j] and alts_A[i] > alts_A[j]) or (alts_D[i] > alts_D[j] and alts_A[i] == alts_A[j]) ):
                    po_string[i,j] = 'P-'
                    po_string[j,i] = 'P+'
                if ( (alts_D[i] == alts_D[j] and alts_A[i] == alts_A[j]) ):
                    po_string[i,j] = 'I'
                    po_string[j,i] = 'I'
                if ( (alts_D[i] > alts_D[j] and alts_A[i] < alts_A[j]) or (alts_D[i] < alts_D[j] and alts_A[i] > alts_A[j])):
                    po_string[i,j] = 'R'
                    po_string[j,i] = 'R'
    return po_string   

# Function: Pre-Order Rank 
def po_ranking(po_string):
    alts   = list(range(1, po_string.shape[0] + 1)) 
    alts   = ['a' + str(alt) for alt in alts]
    for i in range(po_string.shape[0] - 1, -1, -1):
        for j in range(po_string.shape[1] -1, -1, -1):
            if (po_string[i,j] == 'I'):
                po_string = np.delete(po_string, i, axis = 0)
                po_string = np.delete(po_string, i, axis = 1)
                alts[j] = str(alts[j] + ";" + alts[i])
                del alts[i]
                break    
    graph = {}
    for i in range(po_string.shape[0]):
        if (len(alts[i]) == 0):
            graph[alts[i]] = i 
        else:
            graph[alts[i][ :2]] = i   
            graph[alts[i][-2:]] = i 
    po_matrix = np.zeros((po_string.shape[0], po_string.shape[1]))
    for i in range (0, po_string.shape[0]):
        for j in range (0, po_string.shape[1]):
            if (po_string[i,j] == 'P+'):
                po_matrix[i,j] = 1
    col_sum = np.sum(po_matrix, axis = 1)
    alts_rank = [x for _, x in sorted(zip(col_sum, alts))]
    if (np.sum(col_sum) != 0):
        alts_rank.reverse()      
    graph_rank = {}
    for i in range(po_string.shape[0]):
        if (len(alts_rank[i]) == 0):
            graph_rank[alts_rank[i]] = i 
        else:
            graph_rank[alts_rank[i][ :2]] = i   
            graph_rank[alts_rank[i][-2:]] = i
    rank = np.copy(po_matrix)
    for i in range(0, po_matrix.shape[0]):
        for j in range(0, po_matrix.shape[1]): 
            if (po_matrix[i,j] == 1):
                rank[i,:] = np.clip(rank[i,:] - rank[j,:], 0, 1)   
    rank_xy = np.zeros((len(alts_rank), 2))
    for i in range(0, rank_xy.shape[0]):
        rank_xy[i, 0] = 0
        if (len(alts_rank) - np.sum(~rank.any(1)) != 0):
            rank_xy[i, 1] = len(alts_rank) - np.sum(~rank.any(1))
        else:
            rank_xy[i, 1] = 1
    for i in range(0, len(alts_rank) - 1):
        i1 = int(graph[alts_rank[ i ][:2]]) 
        i2 = int(graph[alts_rank[i+1][:2]])
        if (po_string[i1,i2] == 'P+'):
            rank_xy[i+1,1] = rank_xy[i+1,1] - 1
            for j in range(i+2, rank_xy.shape[0]):
                rank_xy[j,1] = rank_xy[i+1,1]
        if (po_string[i1,i2] == 'R'):
            rank_xy[i+1,0] = rank_xy[i,0] + 1            
    for i in range(0, rank_xy.shape[0]):
        plt.text(rank_xy[i, 0],  rank_xy[i, 1], alts_rank[i], size = 12, ha = 'center', va = 'center', bbox = dict(boxstyle = 'round', ec = (0.0, 0.0, 0.0), fc = (0.8, 1.0, 0.8),))
    for i in range(0, len(alts_rank)):
        alts_rank[i] = alts_rank[i][:2]
    for i in range(0, rank.shape[0]):
        for j in range(0, rank.shape[1]):
            k1 = int(graph_rank[list(graph.keys())[list(graph.values()).index(i)]])
            k2 = int(graph_rank[list(graph.keys())[list(graph.values()).index(j)]])
            if (rank[i, j] == 1):  
                plt.arrow(rank_xy[k1, 0], rank_xy[k1, 1], rank_xy[k2, 0] - rank_xy[k1, 0], rank_xy[k2, 1] - rank_xy[k1, 1], head_width = 0.01, head_length = 0.2, overhang = 0.0, color = 'black', linewidth = 0.9, length_includes_head = True)
    axes = plt.gca()
    xmin = np.amin(rank_xy[:,0])
    xmax = np.amax(rank_xy[:,0])
    axes.set_xlim([xmin-1, xmax+1])
    ymin = np.amin(rank_xy[:,1])
    ymax = np.amax(rank_xy[:,1])
    if (ymin < ymax):
        axes.set_ylim([ymin, ymax])
    else:
        axes.set_ylim([ymin-1, ymax+1])
    plt.axis('off')
    plt.show() 
    return

# Function: ELECTRE III
def electre_iii(dataset, P, Q, V, W, graph=False):
    alts   = list(range(1, dataset.shape[0] + 1)) 
    alts   = ['a' + str(alt) for alt in alts]
    alts_D = [0]*dataset.shape[0]
    alts_A = [0]*dataset.shape[0]
    global_concordance = global_concordance_matrix(dataset, P = P, Q = Q, W = W)
    partial_concordance = partial_concordance_matrix(dataset, P = P, Q = Q)
    partial_discordance = partial_discordance_matrix(dataset, P = P, V = V)
    credibility = credibility_matrix(dataset, global_concordance, P = P, V = V)
    rank_D = destilation_descending(credibility = credibility)
    rank_A = destilation_ascending(credibility = credibility)
    #rank_M = []
    rank_N = np.zeros((dataset.shape[0], 1))
    for i in range(0, dataset.shape[0]):
        for j in range(0, len(rank_D)):
            if (alts[i] in rank_D[j]):
                alts_D[i] = j + 1
        for k in range(0, len(rank_A)):
            if (alts[i] in rank_A[k]):
                alts_A[i] = k + 1 
    for i in range(0, len(alts)):
        #rank_M.append('a' + str(i+1) )
        rank_N[i, 0] = (alts_D[i] +  alts_A[i])/2
    #rank_M.sort()
    rank_P = pre_order_matrix(rank_D, rank_A, number_of_alternatives = dataset.shape[0])
    if (graph == True):
        po_ranking(rank_P)
    return partial_concordance, partial_discordance, global_concordance, credibility, rank_D, rank_A, rank_N, rank_P

###############################################################################
