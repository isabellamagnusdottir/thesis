import json
import networkx as nx
import random as rand
import re

from networkx.classes import DiGraph


def graph_generator(graph_family: str, no_of_vertices: int, seed = None):
    match graph_family:
        case "empty":
            return nx.empty_graph(create_using=nx.DiGraph())

        case "path":
            return nx.path_graph(no_of_vertices, create_using=nx.DiGraph())

        case "cycle":
            return nx.cycle_graph(no_of_vertices, create_using=nx.DiGraph())

        case "random_tree":
            tree = nx.random_labeled_tree(no_of_vertices, seed=seed)
            directed_tree = nx.DiGraph()
            directed_tree.add_edges_from(tree.edges)
            if nx.is_tree(directed_tree):
                return directed_tree

        case "complete":
            return nx.complete_graph(no_of_vertices, create_using=nx.DiGraph())

        case "grid":
            graph = nx.grid_2d_graph(no_of_vertices, no_of_vertices, create_using=nx.DiGraph())
            mapping = {old_label: i for i, old_label in enumerate(graph.nodes())}
            return nx.relabel_nodes(graph, mapping)

        case "random":
            return nx.gnm_random_graph(no_of_vertices, 3*no_of_vertices, seed=seed, directed=True)


def _get_weight(cap: int, weights, only_positives=False):
    if rand.choices([True, False], weights)[0] or only_positives:
        return rand.randint(0, cap)
    return rand.randint(-cap, -1)


def _graph_to_json(graph: DiGraph, num, weights):
    graph_data = {}

    for u in range(num):
        if not str(u) in graph_data:
            graph_data[str(u)] = []
        if u in graph.nodes:
            for v in graph.neighbors(u):
                graph_data[str(u)].append([v, _get_weight(num, weights)])

    return graph_data


def save_graph_json(graph: DiGraph, num, weights, filename: str):
    json_data = _graph_to_json(graph, num, weights)
    with open("../tests/test_data/synthetic_graphs/" + filename + ".json", 'w') as f:
        json_str = json.dumps(json_data, indent=2)
        json_str = re.sub(r'\[\n\s*(\d+),\n\s*(-?\d+)\n\s*\]', r'[\1,\2]', json_str)
        f.write(json_str)


def _generate_random_graphs(seed = None):
    no_of_vertices = [10, 50, 100, 200, 500, 750, 1000]
    ratios = [[0.66, 0.34], [0.5, 0.5], [0.8, 0.2], [0.9, 0.1]]
    edges_scalar = [1,3,5,9]

    # for family in types_of_graphs:
    for num in no_of_vertices:
        for ratio in ratios:
            for scalar in edges_scalar:
                graph = nx.gnm_random_graph(num, scalar*num, seed=seed, directed=True)
                save_graph_json(graph, num, ratio, f"random_{num}_{scalar}n_{str(ratio[1]).replace(".", "_")}")


def _generate_families_of_graphs(seed = None):
    no_of_vertices = [10, 50, 100, 200, 500, 750, 1000]
    families_of_graphs = ["path", "cycle", "random_tree", "complete"]
    ratios = [[0.66, 0.34], [0.5, 0.5], [0.8, 0.2], [0.9, 0.1]]

    for f in families_of_graphs:
        for v in no_of_vertices:
            for ratio in ratios:
                graph = graph_generator("random", v, None)
                save_graph_json(graph, v, ratio, f"{f}{v}_{str(ratio[1]).replace(".", "_")}")

    # for GRIDS
    no_of_vertices = [3, 10, 30]
    for num in no_of_vertices:
        for ratio in ratios:
            graph = graph_generator("grid", num, None)
            save_graph_json(graph, num, ratio,f"grid_{num}_{num}_{str(ratio[1]).replace(".", "_")}")

def main():
    _generate_random_graphs()
    _generate_families_of_graphs()

if __name__ == "__main__":
    main()