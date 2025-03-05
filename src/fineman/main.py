from math import log2

from fineman import reweight_graph
from fineman.dijkstra import dijkstra
from fineman.elimination_algorithm import elimination_algorithm
from scripts import generate_double_tree


def main(graph: dict[int, dict[int, int]], source: int):
    n = len(graph.keys())
    neg_edges = {(u,v) for u, edges in graph.items() for v, w in edges.items() if w < 0}
    k = len(neg_edges)

    for _ in range(int(log2(n))):

        for _ in range(int(k**(2/3))):

            price_functions = elimination_algorithm(graph, neg_edges)

            for p in price_functions:
                graph, neg_edges = reweight_graph(graph, p)

    dists = dijkstra(graph, source)
    print(dists)

if __name__ == '__main__':
    graph, _ = generate_double_tree(12, -28)
    main(graph, 0)
