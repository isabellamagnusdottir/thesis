import random as rand

import numpy as np

from .helper_functions import b_hop_sssp, b_hop_stsp, super_source_bfd


def betweenness_reduction(graph: dict[int, dict[int, int]], neg_edges, tau, beta, c):
    if (beta < 1) or (tau < 1) or (tau > len(graph)) or (c <= 1):
        raise ValueError
    #rand.seed()

    n = len(graph)
    sample_size = int(c*tau*np.ceil(np.log(n)))
    if sample_size > len(graph): raise ValueError

    T = rand.sample(tuple(graph.keys()), sample_size)
    
    distances = {}
    for x in T:
        distances[x] = (b_hop_sssp(x, graph, neg_edges, beta), b_hop_stsp(x, graph, beta))

    h_graph, h_neg_edges = construct_h(graph, T, distances)
    
    l = 2*sample_size

    return super_source_bfd(h_graph, h_neg_edges, l, cycleDetection=True)


def construct_h(graph: dict[int, dict[int, int]], T, distances):
    h_graph = {}
    h_neg_edges = set()

    # TODO: consider: does it require a double for-loop?

    for v in graph.keys():
        if v not in h_graph:
            h_graph[v] = {}

        for t in T:
            if t not in h_graph:
                h_graph[t] = {}

            h_graph[t][v] = distances[t][0][v]
            if distances[t][0][v] < 0:
                h_neg_edges.add((t,v))

            h_graph[v][t] = distances[t][1][v]
            if distances[t][1][v] < 0:
                h_neg_edges.add((t,v))
    
    return h_graph, h_neg_edges
