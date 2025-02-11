import numpy as np
import random as rand
from fineman.helper_functions import b_hop_sssp

def rand_is(graph, negative_subset, rho):

    sample_size = rho/4
    I_prime = rand.sample(negative_subset,sample_size)
    