from collections import deque
from math import log2
import random as rand
from numpy import inf

from bidict import bidict

from fineman import preprocess_graph
from fineman.dijkstra import dijkstra
from fineman.elimination_algorithm import elimination_algorithm
from fineman.helper_functions import reweight_graph


def _reverse_price_functions_on_distances(source, dists, price_function):
    actual_dists = [0] * len(dists)

    for i in range(len(actual_dists)):
        actual_dists[i] = dists[i] + price_function[i] - price_function[source]

    return actual_dists

def _find_connected_component_to_source(graph, source: int):
    mapping = bidict()

    queue = deque()
    explored = [False] * len(graph)
    mapping[source] = 0
    queue.append(source)
    explored[source] = True

    new_graph = {0: {}}

    while queue:
        vertex = queue.popleft()
        if mapping[vertex] not in new_graph:
            new_graph[mapping[vertex]] = {}

        for n, w in graph[vertex].items():
            if not explored[n]:
                new_name = len(mapping)
                mapping[n] = new_name
                queue.append(n)
                explored[n] = True
            new_graph[mapping[vertex]][mapping[n]] = w

    return new_graph, mapping


def _remapping_distances(distances, n, mapping):
    dist = [inf] * n

    for old, new in mapping.items():
        dist[old] = distances[new]

    return dist



def fineman(graph: dict[int, dict[int, int]], source: int, seed = None):

    if seed is not None: rand.seed(seed)

    # TODO: consider how to handle empty graphs
    org_graph = graph.copy()
    org_n = len(org_graph.keys())
    m = sum(len(neighbors) for neighbors in org_graph.values())

    graph, mapping = _find_connected_component_to_source(graph, source)

    graph, neg_edges = preprocess_graph(graph, org_n, m)
    n = len(graph.keys())
    neg_edges = {(u,v) for u, edges in graph.items() for v, w in edges.items() if w < 0}

    composed_price_function = [0] * len(graph.keys())

    for _ in range(int(log2(n))):

        k = len(neg_edges)

        for _ in range(int(k**(2/3))):
            price_functions = elimination_algorithm(graph, neg_edges)
            for p in price_functions:
                graph, neg_edges = reweight_graph(org_graph, p)
                composed_price_function = [x + y for x, y in zip(composed_price_function, p)]

            if len(neg_edges) == 0: break

    dist = dijkstra(graph, source)

    return _remapping_distances(_reverse_price_functions_on_distances(source, dist, composed_price_function), org_n, mapping)
