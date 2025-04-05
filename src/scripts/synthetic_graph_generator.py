import json
import random as rand
import re

import networkx as nx
from networkx.classes import DiGraph


def _get_weight(weights):
    if rand.choices([True, False], weights)[0]:
        return rand.randint(0, 30)
    return rand.randint(-10, -1)


def _graph_to_json(graph: DiGraph, weights):
    graph_data = {}

    for u in range(len(graph.nodes)):
        if not str(u) in graph_data:
            graph_data[str(u)] = []
        if u in graph.nodes:
            for v in graph.neighbors(u):
                graph_data[str(u)].append([v, _get_weight(weights)])

    return graph_data


def _save_graph_json(graph: DiGraph, weights, filename: str):
    json_data = _graph_to_json(graph, weights)
    with open("src/tests/test_data/synthetic_graphs/" + filename + ".json", 'w') as f:
        json_str = json.dumps(json_data, indent=2)
        json_str = re.sub(r'\[\n\s*(\d+),\n\s*(-?\d+)\n\s*\]', r'[\1,\2]', json_str)
        f.write(json_str)


def _generate_single_grid_graph(size):
    grid = DiGraph()

    for i in range(size):
        for j in range(size-1):
            if f"({i},{j})" not in grid:
                grid.add_node(f"({i},{j})")
            if f"({i},{j+1})" not in grid:
                grid.add_node(f"({i},{j+1})")

            if rand.choice([True, False]):
                grid.add_edge(f"({i},{j})", f"({i},{j+1})")

    for i in range(size-1):
        for j in range(size):
            if rand.choice([True, False]):
                grid.add_edge(f"({i},{j})", f"({i+1},{j})")

    for i in range(size-1, -1, -1):
        for j in range(size-1, 0, -1):
            if (f"({i},{j-1})", f"({i},{j})") not in grid.edges:
                grid.add_edge(f"({i},{j})", f"({i},{j-1})")

    for i in range(size-1, 0, -1):
        for j in range(size-1, -1, -1):
            if (f"({i-1},{j})", f"({i},{j})") not in grid.edges:
                grid.add_edge(f"({i},{j})", f"({i-1},{j})")

    mapping = {old_label: i for i, old_label in enumerate(grid.nodes())}

    return nx.relabel_nodes(grid, mapping)


def single_graph_generator(graph_family: str, no_of_vertices: int, ratio: tuple[float, float], **kwargs):
    filename = ""

    match graph_family:
        case "path":
            graph = nx.path_graph(no_of_vertices, create_using=nx.DiGraph())

        case "cycle":
            graph = nx.cycle_graph(no_of_vertices, create_using=nx.DiGraph())

        case "random-tree":
            tree = nx.random_labeled_tree(no_of_vertices)
            directed_tree = nx.DiGraph()
            directed_tree.add_edges_from(tree.edges)
            if nx.is_tree(directed_tree):
                graph = directed_tree

        case "complete":
            graph = nx.complete_graph(no_of_vertices, create_using=nx.DiGraph())

        case "watts-strogatz":
            k = kwargs.get("k")
            p = kwargs.get("p")

            graph = nx.connected_watts_strogatz_graph(no_of_vertices, k, p, 1000)
            filename = f"watts-strogatz_{no_of_vertices}_{len(graph.edges)}_{str(ratio[1]).replace(".", "")}_{str(p).replace(".", "")}_{str(k).replace(".", "")}"

        case "grid":
            graph = _generate_single_grid_graph(no_of_vertices)
            while graph.out_degree(0) == 0:
                graph = _generate_single_grid_graph(no_of_vertices)

        case "random":
            scalar = kwargs.get("scalar")
            graph = nx.gnm_random_graph(no_of_vertices, scalar * no_of_vertices, directed=True)

            while (not nx.is_weakly_connected(graph)) or (graph.out_degree(0) == 0):
                graph = nx.gnm_random_graph(no_of_vertices, scalar * no_of_vertices, directed=True)
            filename = f"random_{no_of_vertices}_{scalar * no_of_vertices}_{str(ratio[1]).replace(".", "")}"


    if not filename:
        filename = f"{graph_family}_{no_of_vertices}_{len(graph.edges)}_{str(ratio[1]).replace(".", "")}"

    _save_graph_json(graph, ratio, filename)


def generate_multiple_graphs(family: str, no_of_vertices, ratios):
    for num in no_of_vertices:
        for r in ratios:
            single_graph_generator(family, num, r)

def generate_multiple_grids(no_of_vertices, ratios):
    for num in no_of_vertices:
        for r in ratios:
            single_graph_generator("grid", num, r)

def generate_multiple_random_graphs(no_of_vertices, ratios, scalars):
    for num in no_of_vertices:
        for r in ratios:
            for s in scalars:
                single_graph_generator("random", num, r, scalar=s)

def generate_multiple_watts_strogatz_graphs(no_of_vertices, ratios, ks, ps):
    for num in no_of_vertices:
        for r in ratios:
            for k in ks:
                for p in ps:
                    single_graph_generator("watts-strogatz", num, r, k=k, p=p)

def main():
    # PATHS, CYCLES, TREES, COMPLETE GRAPHS
    families_of_graphs = ["path", "cycle", "random-tree", "complete"]
    no_of_vertices = [10, 50, 100, 200, 500, 750, 1000]
    ratios = [(1.0, 0.0), (0.9, 0.1), (0.8, 0.2), (0.66, 0.34), (0.5, 0.5), (0.2, 0.8), (0.0, 1.0)]

    for family in families_of_graphs:
        generate_multiple_graphs(family, no_of_vertices, ratios)

    # RANDOM GRAPHS
    edges_scalar = [3, 5, 6, 9]
    ratios = [(1.0,0.0), (0.98, 0.02), (0.95, 0.05), (0.92, 0.08), (0.9,0.1), (0.8, 0.2), (0.5, 0.5), (0.2, 0.8), (0.0, 1.0)]
    generate_multiple_random_graphs(no_of_vertices, ratios, edges_scalar)

    # GRIDS
    no_of_vertices = [6, 10, 30]
    ratios = [(1.0, 0.0), (0.95, 0.05), (0.9, 0.1), (0.8, 0.2), (0.66, 0.34), (0.5, 0.5), (0.2, 0.8), (0.0, 1.0)]
    generate_multiple_grids(no_of_vertices, ratios)

    # WATTS-STOGATZ GRAPHS
    no_of_vertices = [10, 50, 100, 500, 1000]
    ratios = [(0.9, 0.1), (0.8, 0.2), (0.66, 0.34), (0.5, 0.5)]
    neighbors = [2, 3, 4, 5]
    probabilities = [0.05, 0.1, 0.25, 0.4]
    generate_multiple_watts_strogatz_graphs(no_of_vertices, ratios, neighbors, probabilities)


if __name__ == "__main__":
    main()
