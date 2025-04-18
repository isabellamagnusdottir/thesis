from queue import PriorityQueue
from numpy import inf

def dijkstra(graph, source, org_graph):
    dist = [inf] * (len(graph.keys()))
    dist[source] = 0
    pq = PriorityQueue()

    org_dist = [inf] * (len(graph.keys()))
    org_dist[source] = 0

    for v in graph.keys():
        pq.put((dist[v], v))

    while not pq.empty():
        current_dist, u = pq.get()
        if current_dist > dist[u]:
            continue

        for v in graph[u]:
            alt_dist = dist[u] + graph[u][v]
            if alt_dist < dist[v]:
                org_dist[v] = org_dist[u] + org_graph[u][v]
                dist[v] = alt_dist
                pq.put((alt_dist, v))

    return org_dist
