from fineman.helper_functions import *
from fineman.rand_is import *
from fineman.heavy_light_partition import *
import time
from math import ceil, log2
import random as rand


def find_is_or_crust(graph, neg_edges, negative_subset, c, c_prime, seed = None):
    if seed is not None: rand.seed(seed)
    k_hat = len(negative_subset)
    rho = k_hat**(1/3)
    if rho < 1 or rho > k_hat: raise ValueError("rho must be between 1 and k_hat!")

    (H,L) = heavy_light_partition(graph, neg_edges, negative_subset, rho, c)
    if H:
        y = rand.choice(tuple(H))
        #TODO: Consider if we want to strictly extract the transpose graph here as we will
        # be working with the transpose graph after if we succeed in finding large enough set
        dist = b_hop_stsp(y, graph,1)
        U = {u for u in negative_subset if dist[u] < 0}
        if len(U) < (1/8)*k_hat/rho:
            new_seed = (int(time.time()*1000))
            print(f"Reseeding algorithm with new seed: {new_seed}")
            return find_is_or_crust(graph, neg_edges, negative_subset, c, new_seed)
        else:
            return (y,U)
    else:
        # TODO: argue for the value of c' since the choice varies probability of success
        IS_size_threshold = rho/16
        for _ in range(c_prime*ceil(log2(len(graph)))):
            I = rand_is(graph, neg_edges, L, rho)
            if len(I) >= IS_size_threshold: return I