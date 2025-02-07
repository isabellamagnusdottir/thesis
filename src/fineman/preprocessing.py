from math import ceil
from collections import deque
from utils import get_set_of_neg_vertices, transpose_graph

def ensure_neg_vertices_has_degree_of_one(graph: dict[int, set[tuple[int, int]]]):
    
    n = len(graph.keys())
    neg_vertices = get_set_of_neg_vertices(graph)

    for vertex in neg_vertices:
        if len(graph[vertex]) > 1:
            
            old_neighbours = graph[vertex]

            # introduce new vertex
            new_vertex = n + 1
            most_neg_weight = min(graph[vertex], key=lambda x: x[1])[1]
            graph[vertex] = {(new_vertex, most_neg_weight)}

            # change weights on existing edges
            for (neighbour, weight) in old_neighbours:
                if new_vertex not in graph:
                    graph[new_vertex] = set()
                graph[new_vertex].add((neighbour, weight - most_neg_weight))

    return graph


def ensure_max_degree(graph: dict[int, set[tuple[int, int]]], threshold: int):

    print("her... Jakob + Isabella = <3")
    print(graph)
    n = len(graph.keys())

    split_queue = deque()

    for vertex in graph.keys():
        if len(graph[vertex]) > threshold:
            split_queue.append(vertex)

    while split_queue:
        vertex = split_queue.popleft()

        # TODO: consider if it can be done without converting to list?
        outgoing_edges = list(graph[vertex])

        new_vertex1, new_vertex2 = n+1, n+2
        n = n + 2

        # half edges
        mid = ceil(len(outgoing_edges)/2)
        edges1 = outgoing_edges[:mid]
        edges2 = outgoing_edges[mid:]

        graph[new_vertex1] = set(edges1)
        graph[new_vertex2] = set(edges2)

        graph[vertex] = {(new_vertex1, 0), (new_vertex2, 0)}

        # check whether new vertices violate the degree threshold
        if len(graph[new_vertex1]) > threshold:
            split_queue.append(new_vertex1)
        if len(graph[new_vertex2]) > threshold:
            split_queue.append(new_vertex2)
        # TODO: consider if it even happens that the first one does not, but the second does?

    return graph


def preproces_graph(graph, threshold):
    transformed_graph = ensure_neg_vertices_has_degree_of_one(graph)

    # ensure for out-degree
    transformed_graph = ensure_max_degree(transformed_graph, threshold)

    # ensure for in-degree
    transposed_graph, _ = transpose_graph(transformed_graph)
    final_transposed_graph = ensure_max_degree(transposed_graph, threshold)
    
    return transpose_graph(final_transposed_graph)[0]

