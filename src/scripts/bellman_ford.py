from numpy import inf

from utils.cycle_error import NegativeCycleError


def standard_bellman_ford(graph: dict[int, dict[int, int]], source: int):
    dist = [inf]*len(graph)
    dist[source] = 0
    for _ in range(len(graph)-1):
        for u,neighborhood in graph.items():
            for v in neighborhood.keys():
                if dist[u] + graph[u][v] < dist[v]:
                    dist[v] = dist[u]+graph[u][v]
    
    for u,neighborhood in graph.items():
        for v in neighborhood.keys():
            if dist[u] + graph[u][v] < dist[v]:
                # TODO: Consider implementing finding the negative cycle using
                # a predecessor array.
                raise NegativeCycleError
    return dist
