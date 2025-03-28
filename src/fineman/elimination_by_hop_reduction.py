from math import ceil

from bidict import bidict

from fineman.helper_functions import super_source_bfd_save_rounds, super_source_bfd


def elimination_of_r_remote_edges_by_hop_reduction(graph: dict[int, dict[int, int]], neg_edge_subset: set, r):

    k_hat = len(neg_edge_subset)
    dists = super_source_bfd_save_rounds(graph, neg_edge_subset, graph.keys(), r)

    R_set = {v for v in graph.keys() if dists[r][v] < 0}

    h, h_neg_edges, mapping = construct_h(graph, neg_edge_subset, dists, R_set, r)

    kappa = ceil(k_hat / r)

    h_distances = super_source_bfd(h, h_neg_edges, kappa, cycleDetection=True)

    g_distances = [0] * len(graph)
    for v in graph.keys():
        g_distances[v] = h_distances[mapping[f"{v}_0"]]

    return g_distances



def construct_h(graph, neg_edges, dists, R_set, r):
    h = {}
    mapping = bidict()

    for v in graph:
        if v in R_set:
            for i in range(r+1):
                idx = len(h.keys())
                mapping[f"{v}_{i}"] = idx
                h[idx] = {}
        else:
            idx = len(h.keys())
            mapping[f"{v}_0"] = idx
            h[idx] = {}

    h_neg_edges = set()

    for u, edges in graph.items():
        for v in edges.keys():
            # case 1
            if (u,v) not in neg_edges and u in R_set and v in R_set:
                for j in range(r+1):
                    h[mapping[f"{u}_{j}"]][mapping[f"{v}_{j}"]] = _compute_weight(j, u, j, v, graph, dists)
                    _construct_neg_edges_set(h, h_neg_edges, mapping[f"{u}_{j}"], mapping[f"{v}_{j}"])

            # case 2
            if (u,v) in neg_edges and u in R_set and v in R_set:
                for j in range(r):
                    weight = _compute_weight(j, u, j+1, v, graph, dists)
                    h[mapping[f"{u}_{j}"]][mapping[f"{v}_{j+1}"]] = _compute_weight(j, u, j+1, v, graph, dists)
                    _construct_neg_edges_set(h, h_neg_edges, mapping[f"{u}_{j}"], mapping[f"{v}_{j+1}"])

            # case 3
            if (u,v) not in neg_edges and u in R_set and v not in R_set:
                for j in range(r+1):
                    h[mapping[f"{u}_{j}"]][mapping[f"{v}_0"]] = _compute_weight(j, u, 0, v, graph, dists)
                    _construct_neg_edges_set(h, h_neg_edges, mapping[f"{u}_{j}"], mapping[f"{v}_0"])

            # case 4
            if (u,v) in neg_edges and u in R_set and v not in R_set:
                for j in range(r):
                    h[mapping[f"{u}_{j}"]][mapping[f"{v}_0"]] = _compute_weight(j, u, 0, v, graph, dists)
                    _construct_neg_edges_set(h, h_neg_edges, mapping[f"{u}_{j}"], mapping[f"{v}_0"])

            # case 5
            if (u,v) not in neg_edges and u not in R_set and v in R_set:
                h[mapping[f"{u}_0"]][mapping[f"{v}_0"]] = _compute_weight(0, u, 0, v, graph, dists)
                _construct_neg_edges_set(h, h_neg_edges, mapping[f"{u}_0"], mapping[f"{v}_0"])

            # case 6
            if (u,v) in neg_edges and u not in R_set and v in R_set:
                weight = _compute_weight(0, u, 1, v, graph, dists)
                h[mapping[f"{u}_0"]][mapping[f"{v}_1"]] = _compute_weight(0, u, 1, v, graph, dists)
                _construct_neg_edges_set(h, h_neg_edges, mapping[f"{u}_0"], mapping[f"{v}_1"])

            # case 7
            if (u,v) not in neg_edges and u not in R_set and v not in R_set:
                h[mapping[f"{u}_0"]][mapping[f"{v}_0"]] = _compute_weight(0, u, 0, v, graph, dists)
                _construct_neg_edges_set(h, h_neg_edges, mapping[f"{u}_0"], mapping[f"{v}_0"])

            #case 8
            if (u,v) in neg_edges and u not in R_set and v not in R_set:
                h[mapping[f"{u}_0"]][mapping[f"{v}_0"]] = _compute_weight(0, u, 0, v, graph, dists)
                _construct_neg_edges_set(h, h_neg_edges, mapping[f"{u}_0"], mapping[f"{v}_0"])


    for u in R_set:
        # case 9
        for j in range(r+1):
            if j == r:
                h[mapping[f"{u}_{j}"]][mapping[f"{u}_0"]] = _compute_weight(j, u, 0, u, graph, dists)
                _construct_neg_edges_set(h, h_neg_edges, mapping[f"{u}_{j}"], mapping[f"{u}_0"])
            else:
                h[mapping[f"{u}_{j}"]][mapping[f"{u}_{j+1}"]] = _compute_weight(j, u, j+1, u, graph, dists)
                _construct_neg_edges_set(h, h_neg_edges, mapping[f"{u}_{j}"], mapping[f"{u}_{j+1}"])

    return h, h_neg_edges, mapping


def _compute_weight(i, u, j, v, graph, dists):
    weight = 0 if u == v else graph[u][v]
    return weight + (dists[i][u]) - (dists[j][v])


def _construct_neg_edges_set(graph, cur_set, u, v):
    if graph[u][v] < 0:
        cur_set.add((u,v))