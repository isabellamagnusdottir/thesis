import numpy as np
from queue import PriorityQueue

def dijkstra(graph: dict[int, dict[int, int]], neg_edges: set, dist: list, I_prime = None, parent = None, anc_in_I=None, Sources = False):

    pq = PriorityQueue()

    for v in graph.keys():
        pq.put((dist[v], v))

    while not pq.empty():
        current_dist, u = pq.get()
        if current_dist > dist[u]:
            continue
        for v in graph[u]:
            if (u,v) in neg_edges:
                continue
            alt_dist = dist[u]+graph[u][v]
            if alt_dist < dist[v]:
                dist[v] = alt_dist
                pq.put((alt_dist,v))

                if Sources:
                    _independent_set_cycle_check(parent, anc_in_I, I_prime, u,v, len(graph))
    return dist


# hold styr på hvorvidt vægten, som står der nu, kommer fra den nuværende bellman-ford eller fra tidligere
def bellman_ford(graph : dict[int, dict[int, int]], neg_edges: set, dist: list, I_prime = None, anc_in_I = None, parent = None, Sources = False):
    
    old_dist = dist.copy()
    # TODO: consider it a dict from vertex to bool is better? depends on the ratio between neg_edges and all edges
    used_hop_in_round = [False] * (len(graph.keys()))
    for (u,v) in neg_edges:
        alt_dist = dist[u] + graph[u][v]

        if used_hop_in_round[u]:
            alt_dist = old_dist[u] + graph[u][v]

        if alt_dist < dist[v]:
            dist[v] = alt_dist
            used_hop_in_round[v] = True
 
            if Sources:
                _independent_set_cycle_check(parent, anc_in_I, I_prime, u,v, len(graph))

    return dist

def bfd(graph, neg_edges, dist: list, beta: int, I_prime = None,parent=None, anc_in_I=None,Sources = False):

    dist = dijkstra(graph, neg_edges, dist, I_prime, parent, anc_in_I, Sources)
    for _ in range(beta):
        dist = bellman_ford(graph, neg_edges, dist, I_prime, parent, anc_in_I, Sources)
        dist = dijkstra(graph, neg_edges, dist, I_prime, parent, anc_in_I, Sources)
    return dist

def bfd_save_rounds(graph, neg_edges, dist: list, beta: int):
    rounds = [dijkstra(graph, neg_edges, dist)]
    for i in range(beta):
        dist = bellman_ford(graph,neg_edges,rounds[i])
        rounds.append(dijkstra(graph,neg_edges,dist))
    return rounds

def b_hop_sssp(source, graph: dict[int, dict[int, int]], neg_edges: set, beta, I_prime=None,parent=None,anc_in_I=None,Sources=False):
    dist = [np.inf]*(len(graph.keys()))
    dist[source] = 0
    
    return bfd(graph, neg_edges, dist, beta, I_prime,parent,anc_in_I, Sources)

def b_hop_stsp(target, graph: dict[int, dict[int, int]], beta):
    t_graph, t_neg_edges = transpose_graph(graph)
    return b_hop_sssp(target, t_graph, t_neg_edges, beta)

def transpose_graph(graph: dict[int, dict[int, int]]):
    t_graph = {}
    t_neg_edges = set()

    for k, neighbors in graph.items():
        if k not in t_graph:
            t_graph[k] = {}

        for v, w in neighbors.items():
            if v not in t_graph:
                t_graph[v] = {}
            
            t_graph[v][k] = w
            
            if w < 0:
                t_neg_edges.add((v,k))

    return t_graph, t_neg_edges


def _subset_bfd(graph, neg_edges, subset, beta,I_prime=None,Sources=False):
    super_source = len(graph)
    graph[super_source] = {}
    parent = [np.nan]*len(graph.keys()) if Sources else None
    anc_in_I = [np.nan]*len(graph.keys()) if Sources else None

  
    for v in subset:
        graph[super_source][v] = 0

    distances = b_hop_sssp(super_source, graph, neg_edges, beta,I_prime,parent,anc_in_I,Sources)
    del graph[super_source]
    if Sources:
        for i in I_prime:
            if distances[i] < 0 and anc_in_I[i] == i:
                raise ValueError("Error -- negative cycle detected (!)")
    return distances

def subset_bfd(graph, neg_edges, subset, beta,I_prime=None,Sources=False):
    return _subset_bfd(graph,neg_edges,subset,beta,I_prime,Sources)[:-1]

# TODO: consider refactoring cycle detection
def super_source_bfd(graph: dict[int, dict[int, int]], neg_edges: set, beta, cycleDetection = False):
    distances1 = _subset_bfd(graph,neg_edges,graph.keys(),beta)
    if cycleDetection:
        distances2 = bellman_ford(graph, neg_edges, distances1.copy(),None)
        distances2 = dijkstra(graph, neg_edges, distances2,None)
        
        for v in graph.keys():
            if distances2[v] < distances1[v]:
                # TODO: implement cycle error
                raise ValueError
 
    return distances1[:-1]

def get_set_of_neg_vertices(graph: dict[int, dict[int, int]]):
    neg_vertices = set()

    for vertex, edges in graph.items():
        for weight in edges.values():
            if weight < 0:
                neg_vertices.add(vertex)
    
    return neg_vertices

# TODO: Find better name for mid
# Rethink if this is both the correct way to do it and if this is even neccessary?
def compute_throughdist(source, mid, target, graph, neg_edges, beta):
    dist1 = b_hop_sssp(source,graph,neg_edges,beta)
    dist2 = b_hop_stsp(target,graph,beta)
    return dist1[mid]+dist2[mid]

def find_betweenness_set(source, target, graph, neg_edges, beta):
    dist1 = b_hop_sssp(source,graph,neg_edges,beta)
    dist2 = b_hop_stsp(target,graph,beta)
    between = set()
    for x in graph.keys():
        if dist1[x]+dist2[x] < 0:
            between.add(x)
    return between

def betweenness(source, target, graph, neg_edges, beta):
    return len(find_betweenness_set(source,target,graph,neg_edges,beta))

def reweight_graph(graph, price_function):
    # TODO: consider if it makes more sense to just hold the total set of edges for 
    # exactly the purpose of reweighting the graph in O(m) time (assuming m is the
    # number of edges in the graph), rather than the current O(n^2) time.
    for u in graph.keys(): 
        for v in graph[u].keys():
            graph[u][v] = graph[u][v] + price_function[u] - price_function[v]
    return graph

def compute_reach(graph,neg_edges,subset,h):
    d = subset_bfd(graph,neg_edges,subset,h)
    return {v for v in graph.keys() if d[v] < 0}


# # TODO: Consider moving this to the independent set file.
# def _independent_set_validate_input(I_prime,parent,Sources):
#     if Sources:
#         if parent is None or I_prime is None:
#             raise ValueError("Error: 'parent' and 'I_prime' must both be non-None if Sources is True.")
#     else:
#         if (parent is None) ^ (I_prime is None):
#             raise ValueError("Error: Either both 'parent' and 'I_prime' should be None, or neither should be .")

# TODO: Non-Functional - missing edge cases (and therefore likely some trivial cases)
def _independent_set_cycle_check(parent, anc_in_I, I_prime, u: int,v: int, super_source: int):
    if u == super_source:
        return
    
    parent[v] = u

    if parent[v] in I_prime and v not in I_prime:
        anc_in_I[v] = parent[v]
    else:
        anc_in_I[v] = anc_in_I[parent[v]]