from typing import Set
import random as rand
import math
from fineman.helper_functions import subset_bfd

def rand_is(graph,negative_edges, negative_subset, rho) -> Set[int]:

    sample_size = math.ceil(rho/4)
    I_prime = set(rand.sample(tuple(negative_subset),sample_size))
    distances = subset_bfd(graph,negative_edges,I_prime,True)
    R = {v for v in graph.keys() if distances[v] < 0}
    I = I_prime - R # TODO: read up on the running time of this operation on sets
    return I
