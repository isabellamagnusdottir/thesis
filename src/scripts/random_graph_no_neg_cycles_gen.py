import json
import re

import networkx as nx
import random as rand

from networkx.classes import DiGraph


def _graph_to_json(graph: DiGraph):
    graph_data = {}

    for u in range(len(graph.nodes)):
        if not str(u) in graph_data:
            graph_data[str(u)] = []
        if u in graph.nodes:
            for v in graph.neighbors(u):
                graph_data[str(u)].append([v, graph[u][v]['weight']])

    return graph_data


def _save_graph_json(graph: DiGraph, filename: str):
    json_data = _graph_to_json(graph)
    with open("src/tests/test_data/synthetic_graphs/" + filename + ".json", 'w') as f:
        json_str = json.dumps(json_data, indent=2)
        json_str = re.sub(r'\[\n\s*(\d+),\n\s*(-?\d+)\n\s*\]', r'[\1,\2]', json_str)
        f.write(json_str)

def random_graph_no_neg_cycles_generator(no_of_vertices: int, edge_scalar: int):
    graph = nx.gnm_random_graph(no_of_vertices, edge_scalar * no_of_vertices, directed=True)

    while (not nx.is_weakly_connected(graph)) or (graph.out_degree(0) == 0):
        graph = nx.gnm_random_graph(no_of_vertices, edge_scalar * no_of_vertices, directed=True)

    for u, v in graph.edges():
        graph[u][v]['weight'] = rand.randint(1, 12)

    all_edges = list(graph.edges())
    rand.shuffle(all_edges)
    neg_edges = set()

    failed_attempts = 100

    for u,v in all_edges:
        org_weight = graph[u][v]['weight']
        graph[u][v]['weight'] = -org_weight

        if nx.negative_edge_cycle(graph):
            graph[u][v]['weight'] = org_weight
            failed_attempts -= 1
            if failed_attempts == 0:
                break
        else:
            neg_edges.add((u,v))
            failed_attempts = 100

    filename = f"random-no-neg-cycles_{no_of_vertices}_{edge_scalar}_{len(neg_edges)}"
    _save_graph_json(graph, filename)
    return filename


def main():
    sizes = [10, 50, 100, 200, 500, 750, 1000]
    scalars = [3, 5, 6, 9]
    for num in sizes:
        for scalar in scalars:
            random_graph_no_neg_cycles_generator(num, scalar)

if __name__ == '__main__':
    main()