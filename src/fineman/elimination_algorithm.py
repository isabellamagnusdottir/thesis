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
    phi = [0] * len(graph)

    dists_from_x = b_hop_sssp(x, graph, neg_edges, beta)
    dists_to_y = b_hop_stsp(y, graph, beta)

    for v in graph.keys():
        phi[v] = min(0, max(dists_from_x[v], -(dists_to_y[v])))

    return phi

#TODO: rename function
def _subgraph_with_out_subset(graph: dict[int, dict[int, int]], out_set: set):
    new_graph = {}
    new_neg_edges = set()

    for u, edge in graph.items():
        if u not in new_graph:
            new_graph[u] = {}
        for v, w in edge.items():
            if (u,v) in out_set or w >= 0:
                new_graph[u][v] = w
                if w < 0:
                    new_neg_edges.add((u,v))

    return new_graph, new_neg_edges


def elimination_algorithm(org_graph, org_neg_edges, seed = None):
    n = len(org_graph.keys())

    c = 3
    k = len(org_neg_edges)
    r = ceil(k**(1/9))

    phi_1 = betweenness_reduction(org_graph, org_neg_edges, tau=r, beta=r+1, c=c)
    graph_phi1, neg_edges = reweight_graph(org_graph, phi_1)

    if len(neg_edges) == 0: return [phi_1]

    U_0 = {u for u, _ in neg_edges}

    match find_is_or_crust(graph_phi1, neg_edges, U_0, c, c+1):
        case (y,U_1):
            print("First half of negative sandwich found")

            # TODO: refactor to keep track of global transposed graph
            graph_T, neg_edges_T = transpose_graph(graph_phi1)
            match find_is_or_crust(graph_T, neg_edges_T, U_1, c, c+1):
                case (x,U_2):
                    print("Second half of negative sandwich found")
                    while len(U_2) > k**(1/3):
                        U_2.pop()
                    phi_2 = _compute_price_function_to_make_U_r_remote(graph_phi1, neg_edges, (x,U_2,y), beta=r+1)

                    graph_phi1_phi2, neg_edges = reweight_graph(graph_phi1, phi_2)

                    if len(compute_reach(graph_phi1_phi2, neg_edges, U_2, r)) > n / r:
                        return elimination_algorithm(org_graph, org_neg_edges)

                    out_U_2 = {(u, v) for u in U_2 for v in org_graph[u].keys()}
                    graph_phi1_phi2_out_U_2, neg_edges = _subgraph_with_out_subset(graph_phi1_phi2, out_U_2)
                    phi = elimination_of_r_remote_edges_by_hop_reduction(graph_phi1_phi2_out_U_2, neg_edges, r)

                    return [phi, phi_1, phi_2]

                case I:
                    print("Independent set found")
                    return [_compute_price_function_to_eliminate_independent_set(graph_phi1, I), phi_1]


        case I:
            print("Independent set found")
            return [_compute_price_function_to_eliminate_independent_set(graph_phi1, I), phi_1]
