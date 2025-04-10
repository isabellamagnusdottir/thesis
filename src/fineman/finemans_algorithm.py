import random as rand
from collections import deque
from math import log2

from bidict import bidict
from numpy import inf

from src.fineman import preprocess_graph
from src.fineman.dijkstra import dijkstra
from src.fineman.elimination_algorithm import elimination_algorithm


def _compute_original_distances(source, org_n, reweighted_distances, composed_price_function):
    actual_dists = [0] * org_n

    for i in range(len(actual_dists)):
        actual_dists[i] = reweighted_distances[i] + composed_price_function[i] - composed_price_function[source]

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

    org_n = len(graph.keys())

    m = sum(len(neighbors) for neighbors in graph.values())
    graph, neg_edges = preprocess_graph(graph, org_n, m)

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

    distances = dijkstra(graph, source)
    converted_distances = _compute_original_distances(source, org_n, distances, all_price_functions)

    return converted_distances
