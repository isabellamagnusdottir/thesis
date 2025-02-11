from fineman.helper_functions import *
from fineman.rand_is import *
from fineman.heavy_light_partition import *
import time
import random as rand


def find_is_or_crust(graph,neg_edges,negative_subset,c, seed = None):
    if seed is not None: rand.seed(seed)
    k_hat = len(negative_subset)
    rho = np.pow(k_hat, (1/3))
    (H,L) = heavy_light_partition(graph,neg_edges,negative_subset,rho,c,seed)
    if H:
        y = rand.choice(tuple(H))
        #TODO: Consider if we want to strictly extract the transpose graph here as we will
        # be working with the transpose graph after if we succeed in finding large enough set
        dist = b_hop_stsp(y,graph,1)
        U = {u for u in negative_subset if dist[u] < 0}
        if len(U) < (1/8)*k_hat*rho:
            # TODO: Clearly not functional -> need a way to seed the function so it doesn't
            # arrive at the same answer
            return find_is_or_crust(graph,neg_edges,negative_subset,c,(int(time.time()*1000)))
        else:
            return (y,U)
    else:
        # TODO: argue for the value of c' since the choice varies probability of success
        c_prime = 4
        IS_size_threshold = rho/16
        for _ in range(c_prime*np.ceil(np.log2(len(graph))).astype(int)):
            I = rand_is(graph,neg_edges,L,rho)
            if len(I) >= IS_size_threshold: return I