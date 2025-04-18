import random as rand
from math import log2

from src.fineman import preprocess_graph
from src.fineman.dijkstra import dijkstra
from src.fineman.elimination_algorithm import elimination_algorithm

def fineman(graph: dict[int, dict[int, int]], source: int, seed = None):

    if seed is not None: rand.seed(seed)

    org_n = len(graph.keys())

    m = sum(len(neighbors) for neighbors in graph.values())
    graph, neg_edges = preprocess_graph(graph, org_n, m)
    org_graph = graph.copy()
    n = len(graph.keys())
    neg_edges = {(u,v) for u, edges in graph.items() for v, w in edges.items() if w < 0}

    all_price_functions = [0] * len(graph)

    for _ in range(int(log2(n))):

        k = len(neg_edges)

        for _ in range(int(k**(2/3))):
            graph, neg_edges, _, price_function = elimination_algorithm(graph, neg_edges)

            for idx in range(len(price_function)):
                all_price_functions[idx] += price_function[idx]

            if len(neg_edges) == 0: break

    distances = dijkstra(graph, source,org_graph)[:org_n]

    return distances
