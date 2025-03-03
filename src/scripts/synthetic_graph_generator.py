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
            return nx.gnp_random_graph(no_of_vertices, 0.66, seed = seed, directed=True)


def _get_weight(cap: int, weights, only_positives=True):
    if rand.choices([True, False], weights) or only_positives:
        return rand.randint(0, cap)
    return rand.randint(-cap, -1)


def _graph_to_json(graph: DiGraph, num, weights):
    graph_data = {}

    for u,v in graph.edges.keys():
        if not str(u) in graph_data:
            graph_data[str(u)] = []
        graph_data[str(u)].append([v, _get_weight(num, weights)])

    return graph_data


def save_graph_json(graph: DiGraph, num, weights, filename: str):
    json_data = _graph_to_json(graph, num, weights)
    with open("../tests/test_data/synthetic_graphs/" + filename + ".json", 'w') as f:
        json_str = json.dumps(json_data, indent=2)
        json_str = re.sub(r'\[\n\s*(\d+),\n\s*(\d+)\n\s*\]', r'[\1,\2]', json_str)
        f.write(json_str)


def main():
    lst = [10, 100]#, 1000]
    types_of_graphs = ["empty", "path", "cycle", "random_tree", "complete", "random"]
    pos_neg_edges_ratio = [0.6,0.4]

    for family in types_of_graphs:
        for num in lst:
            graph = graph_generator(family, num, None)
            save_graph_json(graph, num, pos_neg_edges_ratio, f"{family}_{num}")

    # for GRIDS
    lst = [3, 10]#, 30]
    for num in lst:
        graph = graph_generator("grid", num, None)
        save_graph_json(graph, num, pos_neg_edges_ratio,f"grid_{num}_{num}")

if __name__ == "__main__":
    main()