from queue import PriorityQueue
from numpy import nan,inf

from src.utils import NegativeCycleError


def dijkstra(graph: dict[int, dict[int, int]], neg_edges: set, dist: list, I_prime = None, parent = None, anc_in_I=None, save_source = False):

    pq = PriorityQueue()

    for v in graph.keys():
        dist[v][0] = min(dist[v][0],dist[v][1])
        dist[v][1] = inf
        pq.put((dist[v][0], v))

    while not pq.empty():
        current_dist, u = pq.get()
        if current_dist > dist[u][0]:
            continue
        for v in graph[u]:
            if (u,v) in neg_edges:
                continue
            alt_dist = dist[u][0]+graph[u][v]
            if alt_dist < dist[v][0]:
                dist[v][0] = alt_dist
                pq.put((alt_dist,v))

                if save_source:
                    _compute_ancestor_parent(parent, anc_in_I, I_prime, u,v, len(graph))
    return dist


def bellman_ford(graph : dict[int, dict[int, int]], neg_edges: set, dist: list, I_prime = None, anc_in_I = None, parent = None, save_source = False):

    for (u,v) in neg_edges:
        alt_dist = dist[u][0] + graph[u][v]

        if alt_dist < dist[v][0]:
            dist[v][1] = alt_dist
            if save_source:
                _compute_ancestor_parent(parent, anc_in_I, I_prime, u,v, len(graph))

    return dist

def bfd(graph, neg_edges, dist: list, beta: int, I_prime = None,parent=None, anc_in_I=None,save_source = False):
    dist = dijkstra(graph, neg_edges, dist, I_prime, parent, anc_in_I, save_source)
    for _ in range(beta):
        dist = bellman_ford(graph, neg_edges, dist, I_prime, parent, anc_in_I, save_source)
        dist = dijkstra(graph, neg_edges, dist, I_prime, parent, anc_in_I, save_source)
    return [dist[v][0] for v in range(len(graph))]

def bfd_save_rounds(graph, neg_edges, dist: list, beta: int):
    dist = dijkstra(graph, neg_edges, dist)
    rounds = [[dist[v][0] for v in graph.keys()]]
    for _ in range(beta):
        # TODO: find fix to avoid copying the rounds.
        dist = bellman_ford(graph,neg_edges,dist)
        dist = dijkstra(graph, neg_edges, dist)
        rounds.append([dist[v][0] for v in range(len(graph))])
    return rounds

def b_hop_sssp(source, graph: dict[int, dict[int, int]], neg_edges: set, beta, I_prime=None,parent=None,anc_in_I=None,save_source=False):
    dist = [[inf,inf] for _ in range(len(graph))]
    dist[source][0] = 0

    return bfd(graph, neg_edges, dist, beta, I_prime,parent,anc_in_I, save_source)

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


def _subset_bfd(graph, neg_edges, subset, beta,I_prime=None,save_source=False):
    super_source = len(graph)
    graph[super_source] = {}
    parent = [nan]*len(graph.keys()) if save_source else None
    anc_in_I = [nan]*len(graph.keys()) if save_source else None

    for v in subset:
        graph[super_source][v] = 0

    distances = b_hop_sssp(super_source, graph, neg_edges, beta,I_prime,parent,anc_in_I,save_source)
    del graph[super_source]
    if save_source:
        for i in I_prime:
            if distances[i] < 0 and anc_in_I[i] == i:
                raise NegativeCycleError
    return distances

def subset_bfd(graph, neg_edges, subset, beta: int, I_prime=None, save_source=False):
    return _subset_bfd(graph,neg_edges,subset,beta,I_prime,save_source)[:-1]


def super_source_bfd(graph: dict[int, dict[int, int]], neg_edges: set, beta, cycleDetection = False):
    distances1 = _subset_bfd(graph,neg_edges,graph.keys(),beta)
    if cycleDetection:
        tent_dist = [[distance,inf] for distance in distances1]
        tent_dist = bellman_ford(graph, neg_edges, tent_dist)
        tent_dist = dijkstra(graph, neg_edges, tent_dist)
        for v in graph.keys():
            if tent_dist[v][0] < distances1[v]:
                raise NegativeCycleError

    return distances1[:-1]

def get_set_of_neg_vertices(graph: dict[int, dict[int, int]]):
    neg_vertices = set()

    for vertex, edges in graph.items():
        for weight in edges.values():
            if weight < 0:
                neg_vertices.add(vertex)
    
    return neg_vertices


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


def reweight_graph_and_composes_price_functions(graph: dict[int, dict[int, int]], new_price_function: list[int], existing: list[int], with_transpose = False):
    """
    Reweights the given graph with the provided new_price_function, and composes the new_price_function with existing
    precomputed price functions.

    :param graph: the initial graphs, which needs to be reweighted (dict[int, dict[int, int]])
    :param new_price_function: the price function which reweights the graph (list[int])
    :param existing: the composed price function of previously computed price functions (list[int])
    :param with_transpose: boolean flag deciding whether a transpose graph should be generated as well

    :return: the graph reweighted in new_price_function, a set of the negative edges, a set of the negative vertices,
    and the composed price function.
    """
    new_graph = {}
    new_neg_edges = set()
    negative_vertices = set()

    if with_transpose:
        new_graph_T = {}
        negative_edges_T = set()


    for u, edges in graph.items():
        existing[u] += new_price_function[u]

        if u not in new_graph:
            new_graph[u] = {}

        if with_transpose and u not in new_graph_T:
            new_graph_T[u] = {}

        for v, w in edges.items():
            new_graph[u][v] = w + new_price_function[u] - new_price_function[v]


            if with_transpose:
                if v not in new_graph_T: new_graph_T[v] = {}
                new_graph_T[v][u] = new_graph[u][v]

            if new_graph[u][v] < 0:
                new_neg_edges.add((u, v))
                negative_vertices.add(u)
                if with_transpose: negative_edges_T.add((v,u))

    if with_transpose:
        return new_graph, new_neg_edges, negative_vertices, existing, new_graph_T, negative_edges_T 
    else:
        return new_graph, new_neg_edges, negative_vertices, existing


def reweight_graph_and_get_price_functions(graph, new_price_function, existing):
    new_graph = {}
    new_neg_edges = set()
    negative_vertices = set()

    for u, edges in graph.items():
        existing[u] += new_price_function[u]

        if u not in new_graph:
            new_graph[u] = {}
        for v, w in edges.items():
            new_graph[u][v] = w + new_price_function[u] - new_price_function[v]
            if new_graph[u][v] < 0:
                new_neg_edges.add((u, v))
                negative_vertices.add(u)

    return new_graph, new_neg_edges, negative_vertices, existing

def compute_reach(graph,neg_edges,subset,h):
    d = subset_bfd(graph,neg_edges,subset,h)
    return {v for v in graph.keys() if d[v] < 0}

# TODO: Non-Functional - missing edge cases (and therefore likely some trivial cases)
def _compute_ancestor_parent(parent, anc_in_I, I_prime, u: int,v: int, super_source: int):
    if u == super_source:
        return

    parent[v] = u
    if parent[v] in I_prime and v not in I_prime:
        anc_in_I[v] = parent[v]
    else:
        anc_in_I[v] = anc_in_I[parent[v]]

def super_source_bfd_save_rounds(graph, neg_edges, subset, beta):
    super_source = len(graph)
    graph[super_source] = {}
    for v in subset:
        if v != super_source:
            graph[super_source][v] = 0

    dist = [[inf,inf] for _ in range(len(graph))]
    dist[super_source][0] = 0

    dists = bfd_save_rounds(graph, neg_edges, dist, beta)
    del graph[super_source]
    return [lst[:-1] for lst in dists]
