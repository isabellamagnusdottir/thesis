from decimal import Decimal

from numpy import inf
import src.globals as globals
from math import isclose

from src.utils.cycle_error import NegativeCycleError


def standard_bellman_ford(graph, source: int, with_parent = False):
    if globals.WEIGHT_TYPE is Decimal:
        infi = Decimal("Infinity")
    else:
        infi = inf
    dist = [infi] * len(graph)
    dist[source] = globals.WEIGHT_TYPE(0)
    if with_parent: parent = [None] * len(graph)
    for _ in range(len(graph)-1):
        for u,neighborhood in graph.items():
            for v in neighborhood.keys():
                if dist[u] + graph[u][v] < dist[v]:
                    dist[v] = dist[u]+graph[u][v]
                    if with_parent: parent[v] = u
                    
    for u,neighborhood in graph.items():
        for v in neighborhood.keys():
            if dist[u] + graph[u][v] < dist[v]:
                if globals.WEIGHT_TYPE is float and isclose(dist[u] + graph[u][v], dist[v], abs_tol=1e-9):
                    continue
                # TODO: Consider implementing finding the negative cycle using
                # a predecessor array.
                if with_parent:
                    parent[v] = u
                    cycle = []
                    visited = set()
                    cur = v
                    while cur not in visited:
                        if cur is None:
                            raise RuntimeError("Impossible state: Trying to fetch negative cycle that should exist")
                        visited.add(cur)
                        cycle.append(cur)
                        cur = parent[cur]
                    cycle_start = cycle.index(cur)
                    cycle = cycle[cycle_start:] + [cur]
                    cycle.reverse()
                    raise NegativeCycleError(cycle)
                raise NegativeCycleError()
    return dist
