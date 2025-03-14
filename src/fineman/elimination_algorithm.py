from math import ceil

from fineman.betweenness_reduction import betweenness_reduction
from fineman.elimination_by_hop_reduction import elimination_of_r_remote_edges_by_hop_reduction
from fineman.helper_functions import reweight_graph, super_source_bfd, compute_reach, transpose_graph, b_hop_sssp, \
    b_hop_stsp
from fineman.independent_set_or_crust import find_is_or_crust


def _compute_price_function_to_eliminate_independent_set(graph, independent_set):
    out_I = {(u,v) for u in independent_set for v in graph[u].keys()}
    graph_out_I, _ = _subgraph_with_out_subset(graph, out_I)
    return super_source_bfd(graph_out_I, out_I, 1)


def _compute_price_function_to_make_U_r_remote(graph, neg_edges, negative_sandwich, beta):

    (x,U,y) = negative_sandwich
    phi = [] * len(graph)

    dists_from_x= b_hop_sssp(x, graph, neg_edges, beta)
    dists_to_y = b_hop_stsp(y, graph, beta)

    for v in graph.keys():
        phi[v] = min(0, max(dists_from_x[v], -(dists_to_y[v])))

    return phi


def _subgraph_with_out_subset(graph: dict[int, dict[int, int]], out_set: set):
    new_graph = {}
    new_neg_edges = set()

    for u, edge in graph.items():
        if u not in new_graph:
            new_graph[u] = {}
        for v, w in edge.items():
            if v not in out_set:
                new_graph[u][v] = w
                if w < 0:
                    new_neg_edges.add((u,v))

    return new_graph, new_neg_edges


def elimination_algorithm(org_graph, org_neg_edges, seed = None):

    n = len(org_graph.keys())

    # TODO: probably not efficient to compute these each time.
    neg_vertices = {u for u,_ in org_neg_edges}

    c = 3
    k = len(org_neg_edges)
    r = ceil(k**(1/9))

    phi_1 = betweenness_reduction(org_graph, org_neg_edges, tau=r, beta=r+1, c=c)
    graph_phi1, neg_edges = reweight_graph(org_graph, phi_1)

    match find_is_or_crust(graph_phi1, neg_edges, neg_vertices, c, c+1):
        case (y,U):
            print("First half of negative sandwich found")

            graph_T, neg_edges_T = transpose_graph(graph_phi1)
            match find_is_or_crust(graph_T, neg_edges_T, U, c, c+1):
                case (x,U):
                    print("Second half of negative sandwich found")
                    while len(U) > k**(1/3):
                        U.pop()
                    phi_2 = _compute_price_function_to_make_U_r_remote(graph_phi1, neg_edges, (x,U,y), beta=r+1)

                    graph_phi1_phi2, neg_edges = reweight_graph(graph_phi1, phi_2)

                    if len(compute_reach(graph_phi1_phi2, neg_edges, U, r)) > n / r:
                        return elimination_algorithm(org_graph, org_neg_edges)

                    out_U = {(u, v) for u in U for v in org_graph[u].keys()}
                    graph_phi1_phi2_out_U, neg_edges = _subgraph_with_out_subset(graph_phi1_phi2, out_U)
                    phi = elimination_of_r_remote_edges_by_hop_reduction(graph_phi1_phi2_out_U, neg_edges, r)

                    return [phi, phi_1, phi_2]

                case I:
                    print("Independent set found")
                    return [phi_1, _compute_price_function_to_eliminate_independent_set(graph_phi1, I)]


        case I:
            print("Independent set found")
            return [phi_1, _compute_price_function_to_eliminate_independent_set(graph_phi1, I)]
