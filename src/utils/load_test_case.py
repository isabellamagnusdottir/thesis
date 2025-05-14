from decimal import Decimal
import json
import os
from collections import deque
import src.globals as globals

def _find_connected_component_to_source(graph, source: int):
    mapping = {}
    mapping[source] = 0

    queue = deque()
    queue.append(source)

    explored = [False] * len(graph)
    explored[source] = True

    new_graph = {0: {}}
    neg_edges = set()

    while queue:
        vertex = queue.popleft()
        if mapping[vertex] not in new_graph:
            new_graph[mapping[vertex]] = {}

        for n, w in graph[vertex].items():
            if not explored[n]:
                new_name = len(mapping)
                mapping[n] = new_name
                queue.append(n)
                explored[n] = True
            new_graph[mapping[vertex]][mapping[n]] = w
            if w < 0:
                neg_edges.add((mapping[vertex], mapping[n]))
                
    return new_graph, neg_edges


def load_test_case(path: str, only_cc = False):

    with open(path, 'r') as file:
        data = json.load(file)

    graph = {}
    neg_set = set()

    for k, v in data.items():
        vertex = int(k)
        if vertex not in graph:
            graph[vertex] = {}

        for neighbor, weight in v:
            if globals.WEIGHT_TYPE is Decimal:
                weight = Decimal(weight)
            elif globals.WEIGHT_TYPE is float:
                weight = float(weight)
            else:
                weight = int(weight)
            graph[vertex][neighbor] = weight

            if weight < 0.0:
                neg_set.add((vertex, neighbor))

    if only_cc:
        return _find_connected_component_to_source(graph, 0)
    return graph, neg_set

def main():
    print(os.getcwd())

if __name__ == "__main__":
    main()