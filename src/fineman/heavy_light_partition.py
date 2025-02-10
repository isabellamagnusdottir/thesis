import numpy as np
import random as rand
from collections import defaultdict
from fineman.helper_functions import compute_reach

def heavy_light_partition(graph, negative_subset, rho,c):
    n = len(graph)
    k_hat = len(negative_subset)
    count = defaultdict(int)
    sample_prob = rho/k_hat

    # TODO: consider what type of error there it should be
    if sample_prob > 1 or sample_prob < 0:
        raise ValueError
    
    for _ in range(c*np.ceil(np.log(n))):
        U_prime = {v for v in negative_subset if rand.random() < sample_prob}
        R = compute_reach(U_prime)
        for v in R:
            count[v]
        
    heavy_threshold = (c/2)*np.ceil(np.log(n))
    H = {u for u in negative_subset if count[u] >= heavy_threshold}
    L = negative_subset-H

    return H,L