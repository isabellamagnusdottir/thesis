from src.fineman.core_functions import *
from src.fineman.rand_is import *
from src.fineman.heavy_light_partition import *
import time
from math import ceil, log2
import random as rand


def find_is_or_crust(graph, neg_edges, t_neg_edges, negative_subset, c=6, c_prime=4, seed = None):
    if seed is not None: rand.seed(seed)
    k_hat = len(negative_subset)
    rho = k_hat**(1/3)

    (H,L) = heavy_light_partition(graph, neg_edges, negative_subset, rho, c)
    if H:
        y = rand.choice(tuple(H))
        dist = h_hop_stsp(y, graph, t_neg_edges, 1)
        U = {u for u in negative_subset if dist[u] < 0}
        if len(U) < (1/8)*k_hat/rho:
            new_seed = (int(time.time()*1000))
            return find_is_or_crust(graph, neg_edges, t_neg_edges, negative_subset, seed=new_seed)
        else:
            return (y,U)
    else:
        IS_size_threshold = rho/16
        for _ in range(c_prime*ceil(log2(len(graph)))):
            I = rand_is(graph, neg_edges, L, rho)
            if len(I) >= IS_size_threshold:
                return I
        new_seed = (int(time.time()*1000))
        return find_is_or_crust(graph, neg_edges, t_neg_edges, negative_subset, seed=new_seed)