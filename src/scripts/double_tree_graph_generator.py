# Generate two binary trees with n nodes and matching inbetween them
def generate_double_tree(depth: int, neg_edge_weight: int):
    n = 2 ** depth - 1
    graph = {1: {}}
    neg_edges = set()

    for v in range(2, n+1):
        if v not in graph:
            graph[v] = {}
        graph[v//2][v] = 1

    graph[-1] = {}

    for v in range(2, n+1):
        if -v not in graph:
            graph[-v] = {}
        graph[-v][-(v//2)] = 1

    for u in range(n//2+1, n+1):
        graph[u][-u] = neg_edge_weight
        neg_edges.add((u,-u))

    graph, neg_edges = _relabel_graph(graph, depth)

    return graph, neg_edges


def _relabel_graph(graph, depth):
    relabelled_graph = {}
    relabelled_neg_edges = set()

    # compute mapping
    mapping = {i: i-1 for i in range(1, len(graph.keys())//2+1)}

    for height in range(depth, 0, -1):
        n = 2**height - 1

        for i in range(int((n+1)/2), n+1):
            mapping[-i] = len(mapping)

    # apply mapping
    for old_node, edges in graph.items():
        new_node = mapping[old_node]
        relabelled_graph[new_node] = {}
        for neighbor, weight in edges.items():
            relabelled_graph[new_node][mapping[neighbor]] = weight
            if weight < 0:
                relabelled_neg_edges.add((new_node, mapping[neighbor]))

    return relabelled_graph, relabelled_neg_edges
