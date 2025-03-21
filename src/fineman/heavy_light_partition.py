from typing import Tuple,Set
import random as rand
from math import ceil, log
from fineman.helper_functions import compute_reach

def heavy_light_partition(graph, neg_edges, negative_subset, rho, c: int, seed=None) -> Tuple[Set[int], Set[int]]:
    if seed is not None: rand.seed(seed)

    n = len(graph)
    k_hat = len(negative_subset)
    if rho > k_hat or rho < 1:
        raise ValueError("Error -- invalid value for rho")

    count = [0] * n

    sample_prob = rho/k_hat
    if sample_prob > 1 or sample_prob < 0:
        raise ValueError
    
    sample_rounds = c*ceil(log(n))

    for _ in range(sample_rounds):
        U_prime = {v for v in negative_subset if rand.random() < sample_prob}
        R = compute_reach(graph, neg_edges, U_prime, 1)
        for v in R:
            count[v] = count[v] + 1

    heavy_threshold = (c/2)*ceil(log(n))
    H = {u for u in negative_subset if count[u] >= heavy_threshold}
    L = negative_subset - H

    return (H,L)