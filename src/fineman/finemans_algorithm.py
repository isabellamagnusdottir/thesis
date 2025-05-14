import random as rand
from math import log2

from src.fineman import preprocess_graph
from src.fineman.dijkstra import dijkstra
from src.fineman.elimination_algorithm import elimination_algorithm
import src.globals as globals

def fineman(graph, source: int, seed = None, weight_type = float):
    globals.change_weight_type(weight_type)
    if seed is not None: rand.seed(seed)

    org_n = len(graph.keys())
    m = sum(len(neighbors) for neighbors in graph.values())

    graph, neg_edges = preprocess_graph(graph, org_n, m)
    org_graph = graph.copy()
    n = len(graph.keys())
    neg_edges = {(u,v) for u, edges in graph.items() for v, w in edges.items() if w < 0}

    for _ in range(int(log2(n))):

        k = len(neg_edges)

        for _ in range(int(k**(2/3))):
            prev_k = len(neg_edges)
            print("calling elimination_algorithm")
            graph, neg_edges, _ = elimination_algorithm(graph, neg_edges)
            assert prev_k >= len(neg_edges)

            if len(neg_edges) == 0: return dijkstra(graph, source, org_graph)[:org_n]

    distances = dijkstra(graph, source, org_graph)[:org_n]

    return distances
