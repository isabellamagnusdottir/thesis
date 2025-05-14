import argparse
import json
import re
import random as rand
import networkx as nx

from src.fineman import bellman_ford
from src.scripts.synthetic_graph_generator import _get_weight
from src.scripts.bellman_ford import standard_bellman_ford
from src.utils.cycle_error import NegativeCycleError
import src.globals as globals


def _swap_sign_of_neg_edge_in_cycle(graph, cycle):
    u = rand.choice(cycle)
    while True:
        if cycle.index(u) + 1 >= len(cycle):
            v = cycle[0]
        else:
            v = cycle[cycle.index(u)+1]
        weight = graph[u][v]
        if weight > 0:
            u = v
            continue
        else:
            graph[u][v] = abs(weight)
            break


def _digraph_to_json(graph: nx.classes.DiGraph):
    graph_data = {}

    for u in range(len(graph.nodes)):
        if not str(u) in graph_data:
            graph_data[str(u)] = []
        if u in graph.nodes:
            for v in graph.neighbors(u):
                graph_data[str(u)].append([v, str(graph[u][v]['weight'])])
    return graph_data

def _graph_to_json(graph: dict[int, dict[int, float]]):
    json_graph = {}
    neg_count = 0
    for u in graph.keys():
        json_graph[str(u)] = []
        for v in graph[u].keys():
            weight = graph[u][v]
            json_graph[str(u)].append([v, str(weight)])
            if weight < 0:
                neg_count += 1
    return json_graph, neg_count

def _save_to_json(json_data, filename: str):
    with open("src/tests/test_data/synthetic_graphs/" + filename + ".json", 'w') as f:
        json_str = json.dumps(json_data, indent=2)
        json_str = re.sub(r'\[\s*\n\s*(\d+),\s*\n\s*("?-?\d+(?:\.\d+)?")\s*\n\s*\]',
                          r'[\1, \2]',
                          json_str)
        f.write(json_str)

def generate_random_no_neg_cycles_graph_1(no_of_vertices: int, edge_scalar: int):
    graph = nx.gnm_random_graph(no_of_vertices, edge_scalar * no_of_vertices, directed=True)

    while (not nx.is_weakly_connected(graph)) or (graph.out_degree(0) == 0):
        graph = nx.gnm_random_graph(no_of_vertices, edge_scalar * no_of_vertices, directed=True)

    for u, v in graph.edges():
        graph[u][v]['weight'] = _get_weight((1.0, 0.0))

    all_edges = list(graph.edges())
    rand.shuffle(all_edges)
    neg_edges = set()

    failed_attempts = 100

    for u,v in all_edges:
        org_weight = graph[u][v]['weight']
        if org_weight == 0:
            continue
        graph[u][v]['weight'] = -org_weight

        if nx.negative_edge_cycle(graph):
            graph[u][v]['weight'] = org_weight
            failed_attempts -= 1
            if failed_attempts == 0:
                break
        else:
            neg_edges.add((u,v))
            failed_attempts = 100

    filename = f"random-no-neg-cycles-1_{no_of_vertices}_{edge_scalar*no_of_vertices}_{len(neg_edges)}"
    json_graph = _digraph_to_json(graph)
    _save_to_json(json_graph, filename)
    return filename

def generate_random_no_neg_cycles_graph_2(n,scalar,ratio: tuple[float,float]):
    G = nx.gnm_random_graph(n, scalar * n, directed=True)
    graph = {}
    for u in G.nodes():
        graph[u] = {}
    for u,v in G.edges():
        graph[u][v] = _get_weight(ratio)

    while True:
        try:
            standard_bellman_ford(graph,0,with_parent=True)
        except NegativeCycleError as e:
            _swap_sign_of_neg_edge_in_cycle(graph, e.get_cycle()[:-1])
            continue
        break

    json_graph, neg_count = _graph_to_json(graph)
    filename = f"random-no-neg-cycles-2_{n}_{scalar * n}_{neg_count}_{str(ratio[1]).replace(".","")}"
    _save_to_json(json_graph, filename)
    return filename


def main(w_type):
    globals.change_weight_type(w_type)
    sizes = [10, 50, 100, 200, 500, 750, 1000]
    scalars = [3, 5, 6, 9]
    ratios = [(0.9, 0.1), (0.8, 0.2), (0.66, 0.34), (0.5, 0.5), (0.2, 0.8), (0.0, 1.0)]
    for num in sizes:
        for scalar in scalars:
            generate_random_no_neg_cycles_graph_1(num, scalar)
            for ratio in ratios:
                generate_random_no_neg_cycles_graph_2(num,scalar,ratio)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Data type of edge weights")
    parser.add_argument("type", type=str, default="int", help="Data type to use: int, float or decimal")
    args = parser.parse_args()
    main(globals.types[args.type])
