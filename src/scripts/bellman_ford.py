from numpy import inf

from src.utils.cycle_error import NegativeCycleError


def standard_bellman_ford(graph: dict[int, dict[int, int]], source: int, with_parent = False):
    dist = [inf]*len(graph)
    dist[source] = 0
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
                # TODO: Consider implementing finding the negative cycle using
                # a predecessor array.
                if with_parent:
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

                    raise NegativeCycleError(cycle)
                raise NegativeCycleError()
    return dist
