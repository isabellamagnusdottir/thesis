from math import ceil

from bidict import bidict

from fineman import super_source_bfd_save_rounds, super_source_bfd


def elimination_of_r_remote_edges_by_hop_reduction(graph: dict[int, dict[int, int]], neg_edges: set, r):

    k_hat = len(neg_edges)
    dists = super_source_bfd_save_rounds(graph, neg_edges, graph.keys(), r)

    R_set = {v for v in graph if dists[r][v] < 0 for v in graph.keys()}

    h, mapping = construct_h(graph, neg_edges, dists, R_set, r)
    h_neg_edges = {(u,v) for u, edges in h.items() for v, weight in edges.items() if weight < 0}

    kappa = ceil(k_hat / r)

    distances = super_source_bfd(h, h_neg_edges, kappa, cycleDetection=True)
    return distances



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

    # TODO: needs to be done in a better way
    all_edges = {(u,v) for u, edge in graph.items() for v in edge.keys()}

    for u in graph:
        for v in graph:

            if (u,v) in all_edges:

                # case 1
                if (u,v) not in neg_edges and u in R_set and v in R_set:
                    for j in range(r+1):
                        h[mapping[f"{u}_{j}"]][mapping[f"{v}_{j}"]] = _compute_weight(j, u, j, v, graph, dists)

                # case 2
                if (u,v) in neg_edges and u in R_set and v in R_set:
                    for j in range(r):
                        h[mapping[f"{u}_{j}"]][mapping[f"{v}_{j+1}"]] = _compute_weight(j, u, j+1, v, graph, dists)

                # case 3
                if (u,v) not in neg_edges and u in R_set and v not in R_set:
                    for j in range(r+1):
                        h[mapping[f"{u}_{j}"]][mapping[f"{v}_0"]] = _compute_weight(j, u, 0, v, graph, dists)

                # case 4
                if (u,v) in neg_edges and u in R_set and v not in R_set:
                    for j in range(r):
                        h[mapping[f"{u}_{j}"]][mapping[f"{v}_0"]] = _compute_weight(j, u, 0, v, graph, dists)

                # case 5
                if (u,v) not in neg_edges and u not in R_set and v in R_set:
                    h[mapping[f"{u}_0"]][mapping[f"{v}_0"]] = _compute_weight(0, u, 0, v, graph, dists)

                # case 6
                if (u,v) in neg_edges and u not in R_set and v in R_set:
                    h[mapping[f"{u}_0"]][mapping[f"{v}_1"]] = _compute_weight(0, u, 1, v, graph, dists)

                # case 7
                if (u,v) not in neg_edges and u not in R_set and v not in R_set:
                    h[mapping[f"{u}_0"]][mapping[f"{v}_0"]] = _compute_weight(0, u, 0, v, graph, dists)

                #case 8
                if (u,v) in neg_edges and u not in R_set and v not in R_set:
                    h[mapping[f"{u}_0"]][mapping[f"{v}_0"]] = _compute_weight(0, u, 0, v, graph, dists)

        # case 9
        if u in R_set:
            for j in range(r+1):
                if j == r:
                    h[mapping[f"{u}_{j}"]][mapping[f"{u}_0"]] = _compute_weight(j, u, 0, u, graph, dists)
                else:
                    h[mapping[f"{u}_{j}"]][mapping[f"{u}_{j+1}"]] = _compute_weight(j, u, j+1, u, graph, dists)

    return h, mapping


def _compute_weight(i, u, j, v, graph, dists):
    weight = 0 if u == v else graph[u][v]
    return weight + (dists[i][u]) - (dists[j][v])
