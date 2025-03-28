from typing import Set
import random as rand
from math import ceil
from fineman.helper_functions import subset_bfd

def rand_is(graph,negative_edges, negative_subset, rho) -> Set[int]:

    sample_size = ceil(rho/4)
    I_prime = set(rand.sample(tuple(negative_subset), sample_size))
    distances = subset_bfd(graph, negative_edges, I_prime,1, I_prime=I_prime, save_source=True)
    R = {v for v in graph.keys() if distances[v] < 0}
    I = I_prime - R  # O(len(I_prime) -> https://wiki.python.org/moin/TimeComplexity
    return I
